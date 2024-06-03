import os
from typing import Annotated, Optional
from time import time
from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, Form, UploadFile
from fastapi.routing import APIRouter
from app import auth
from app.db import ADP_DB, Stage, File, S3
from app.jsonapi.core_models import convert_query
from app.adp.quotes.job_quotes.models import (
    QuoteResponse,
    NewQuote,
    ExistingQuoteRequest,
    QuoteQuery,
    QuoteQueryJSONAPI,
)
from app.adp.models import RelatedCustomerResponse, CustomersRelResp
from app.customers.locations.models import (
    LocationRelationshipsResponse,
    RelatedLocationResponse,
)
from app.places.models import RelatedPlaceResponse, PlaceRelationshipsResponse
from app.adp.quotes.products.models import (
    RelatedProductResponse,
    ProductRelationshipsResponse,
)
from app.jsonapi.sqla_models import ADPQuote

QUOTES_RESOURCE = ADPQuote.__jsonapi_type_override__
S3_DIR = os.getenv("S3_BUCKET") + "/adp/quotes"
quotes = APIRouter(prefix=f"/{QUOTES_RESOURCE}", tags=["adp quotes"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(QuoteQueryJSONAPI)


@quotes.get(
    "", response_model=QuoteResponse, response_model_exclude_none=True, tags=["jsonapi"]
)
async def quote_collection(
    token: Token, session: NewSession, query: QuoteQuery = Depends()
) -> QuoteResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, query=converter(query))
    )


@quotes.get(
    "/{quote_id}",
    response_model=QuoteResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def one_quote(
    token: Token,
    quote_id: int,
    session: NewSession,
    query: QuoteQuery = Depends(),
) -> QuoteResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            query=converter(query),
            obj_id=quote_id,
        )
    )


@quotes.post(
    "",
    response_model=QuoteResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_quote(
    token: Token,
    session: NewSession,
    adp_customer_id: int = Form(),
    adp_quote_id: str = Form(default=None),
    job_name: str = Form(),
    expires_at: date = Form(),
    status: Stage = Form(),
    quote_doc: Optional[UploadFile] = None,
    plans_doc: Optional[UploadFile] = None,
    place_id: int = Form(),
    customer_location_id: int = Form(),
) -> QuoteResponse:
    """Create a new quote.
    - ADP Quote ID, quote documents and plan documents are not required for creation.
    - ADP Quote ID comes from ADP and ought to be added in later if not supplied on creation.
    - Create timestamp is auto-generated and stuffed into the JSONAPI request
    - Expiration date is determined by rules associated with quote creation (i.e. +90 days).
    - Stage should defualt to 'proposed', but ought to be selectable."""
    # TODO generate filenames and upload documents to S3.
    # Plug the links to them into a NewQuote before post_collection
    created_at: datetime = datetime.today().date()
    time_id: int = int(time())
    s3_quote_path = S3_DIR + f"/{adp_customer_id}/{time_id}"
    if token.permissions >= auth.Permissions.developer:
        attrs = {
            "job_name": job_name,
            "created_at": created_at,
            "expires_at": expires_at,
            "status": status,
        }
        if adp_quote_id:
            attrs["adp_quote_id"] = adp_quote_id
        if quote_doc:
            quote_file = File(
                file_name=S3_DIR + quote_doc.filename,
                file_mime=quote_doc.content_type,
                file_content=await quote_doc.read(),
            )
            s3_path = f"{s3_quote_path}/{quote_file.file_name}"
            await S3.upload_file(quote_file, s3_path)
            attrs["quote_doc"] = s3_path

        if plans_doc:
            plans_file = File(
                file_name=S3_DIR + plans_doc.filename,
                file_mime=plans_doc.content_type,
                file_content=await plans_doc.read(),
            )
            s3_path = f"{s3_quote_path}/{plans_file.file_name}"
            await S3.upload_file(quote_file, s3_path)
            attrs["plans_doc"] = s3_path

        new_quote_obj = {
            "type": QUOTES_RESOURCE,
            "attributes": attrs,
            "relationships": {
                "places": {"data": {"id": place_id, "type": "places"}},
                "customer-locations": {
                    "data": {"id": customer_location_id, "type": "customer-locations"}
                },
                "adp-customers": {
                    "data": {"id": adp_customer_id, "type": "adp-customers"}
                },
            },
        }
        new_quote = NewQuote(data=new_quote_obj)
        return (
            auth.ADPOperations(token, QUOTES_RESOURCE)
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .post(
                session=session,
                data=new_quote.model_dump(exclude_none=True, by_alias=True),
                primary_id=adp_customer_id,
            )
        )

    raise HTTPException(status_code=401)


@quotes.patch(
    "/{quote_id}",
    response_model=QuoteResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def modify_quote(
    token: Token,
    session: NewSession,
    quote_id: int,
    body: ExistingQuoteRequest,
) -> QuoteResponse:
    customer_id = body.data.relationships.adp_customers.data.id
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=body.model_dump(exclude_none=True, by_alias=True),
            primary_id=customer_id,
            obj_id=quote_id,
        )
    )


@quotes.delete("/{quote_id}", tags=["jsonapi"])
async def delete_quote(
    token: Token, session: NewSession, quote_id: int, adp_customer_id: int
) -> None:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session=session, obj_id=quote_id, primary_id=adp_customer_id)
    )


@quotes.get(
    "/{quote_id}/adp-customers",
    response_model=RelatedCustomerResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_customers(
    token: Token, session: NewSession, quote_id: int
) -> RelatedCustomerResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, obj_id=quote_id, related_resource="adp-customers")
    )


@quotes.get(
    "/{quote_id}/adp-quote-products",
    response_model=RelatedProductResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_products(
    token: Token, session: NewSession, quote_id: int
) -> RelatedProductResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, obj_id=quote_id, related_resource="adp-quote-products")
    )


@quotes.get(
    "/{quote_id}/places",
    response_model=RelatedPlaceResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_place(
    token: Token, session: NewSession, quote_id: int
) -> RelatedPlaceResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, obj_id=quote_id, related_resource="places")
    )


@quotes.get(
    "/{quote_id}/customer-locations",
    response_model=RelatedLocationResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_customer_location(
    token: Token, session: NewSession, quote_id: int
) -> RelatedLocationResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session=session, obj_id=quote_id, related_resource="customer-locations")
    )


@quotes.get(
    "/{quote_id}/relationships/adp-customers",
    response_model=CustomersRelResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_customers_rel(
    token: Token, session: NewSession, quote_id: int
) -> CustomersRelResp:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            obj_id=quote_id,
            related_resource="adp-customers",
            relationship=True,
        )
    )


@quotes.get(
    "/{quote_id}/relationships/adp-quote-products",
    response_model=ProductRelationshipsResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_products_rel(
    token: Token, session: NewSession, quote_id: int
) -> ProductRelationshipsResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            obj_id=quote_id,
            related_resource="adp-quote-products",
            relationship=True,
        )
    )


@quotes.get(
    "/{quote_id}/relationships/places",
    response_model=PlaceRelationshipsResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_place_rel(
    token: Token, session: NewSession, quote_id: int
) -> PlaceRelationshipsResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            obj_id=quote_id,
            related_resource="places",
            relationship=True,
        )
    )


@quotes.get(
    "/{quote_id}/relationships/customer-locations",
    response_model=LocationRelationshipsResponse,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
def quote_customer_location_rel(
    token: Token, session: NewSession, quote_id: int
) -> LocationRelationshipsResponse:
    return (
        auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(
            session=session,
            obj_id=quote_id,
            related_resource="customer-locations",
            relationship=True,
        )
    )
