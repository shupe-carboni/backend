from time import time
from typing import Annotated, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends, Form, UploadFile, status
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
S3_DIR = "/adp/quotes"
quotes = APIRouter(prefix=f"/{QUOTES_RESOURCE}", tags=["adp quotes"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(ADP_DB.get_db)]
converter = convert_query(QuoteQueryJSONAPI)


@quotes.get("", response_model=QuoteResponse, tags=["jsonapi"])
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
    tags=["jsonapi", "form"],
)
async def new_quote(
    token: Token,
    session: NewSession,
    S3: Annotated[S3, Depends()],
    adp_customer_id: int,
    job_name: str = Form(),
    place_id: int = Form(),
    customer_location_id: int = Form(),
    status: Stage = Form(default=Stage.PROPOSED),
    adp_quote_id: str = Form(default=None),
    expires_at: date = Form(default=datetime.today().date() + timedelta(days=90)),
    quote_doc: Optional[UploadFile] = None,
    plans_doc: Optional[UploadFile] = None,
) -> QuoteResponse:
    """Create a new quote.

    If a customer is filling out the form, they won't have the quote document from ADP
    nor expires_at.

    If an sca employee is filling out this form, they may have all of the info but may
    not.
    """
    time_id: int = int(time())
    s3_quote_path = S3_DIR + f"/{adp_customer_id}/{time_id}"
    created_at: date = datetime.today().date()
    attrs = {
        "job-name": job_name,
        "created-at": created_at,
        "expires-at": expires_at,
        "status": status,
    }
    s3_quote_path = S3_DIR + f"/{adp_customer_id}/{time_id}"
    if plans_doc:
        plans_file = File(
            file_name=S3_DIR + plans_doc.filename,
            file_mime=plans_doc.content_type,
            file_content=await plans_doc.read(),
        )
        s3_path = f"{s3_quote_path}/{plans_file.file_name}"
        await S3.upload_file(plans_file, s3_path)
        attrs["plans-doc"] = s3_path

    new_quote_obj = {
        "type": QUOTES_RESOURCE,
        "attributes": attrs,
        "relationships": {
            "places": {"data": {"id": place_id, "type": "places"}},
            "customer-locations": {
                "data": {"id": customer_location_id, "type": "customer-locations"}
            },
            "adp-customers": {"data": {"id": adp_customer_id, "type": "adp-customers"}},
        },
    }
    new_quote = NewQuote(data=new_quote_obj)
    # will bubble up an error if user is not authorized in some way
    quote_resource = QuoteResponse(
        **auth.ADPOperations(token, QUOTES_RESOURCE)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .post(
            session=session,
            data=new_quote.model_dump(exclude_none=True, by_alias=True),
            primary_id=adp_customer_id,
        )
    )
    # Assuming customers won't have this information when requesting a quote
    if token.permissions >= auth.Permissions.developer:
        additional_attrs = {}

        if adp_quote_id:
            additional_attrs["adp-quote-id"] = adp_quote_id

        if quote_doc:
            quote_file = File(
                file_name=S3_DIR + quote_doc.filename,
                file_mime=quote_doc.content_type,
                file_content=await quote_doc.read(),
            )
            s3_path = f"{s3_quote_path}/{quote_file.file_name}"
            await S3.upload_file(quote_file, s3_path)
            additional_attrs["quote-doc"] = s3_path

        if additional_attrs:
            updated_quote_obj = {
                "id": quote_resource.data.id,
                "type": QUOTES_RESOURCE,
                "attributes": additional_attrs,
                "relationships": {
                    "adp-customers": {
                        "data": {"id": adp_customer_id, "type": "adp-customers"}
                    },
                },
            }
            return await modify_quote(
                token,
                session,
                quote_resource.data.id,
                ExistingQuoteRequest(data=updated_quote_obj),
            )
    return quote_resource


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


@quotes.patch(
    "/{quote_id}/new-file",
    response_model=QuoteResponse,
    response_model_exclude_none=True,
    tags=["jsonapi", "form"],
)
async def modify_quote_with_new_file_upload(
    token: Token,
    session: NewSession,
    quote_id: int,
    adp_customer_id: int,
    quote_doc: Optional[UploadFile] = None,
    plans_doc: Optional[UploadFile] = None,
) -> QuoteResponse:
    if not any(quote_doc, plans_doc):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "either a new plans document or a new quote document are required for "
            "this operation",
        )
    current_quote = await one_quote(token, quote_id, session, QuoteQuery())
    attrs = {}
    documents_strs = [
        current_quote.data.attributes.quote_doc,
        current_quote.data.attributes.plans_doc,
    ]
    if not any(documents_strs):
        time_id: int = int(time())
        s3_quote_path = S3_DIR + f"/{adp_customer_id}/{time_id}"
    else:
        # lop off the filename from the s3 path, dedup, and extract
        document_dir = set(
            [doc[::-1][doc[::-1].find("/") :][::-1] for doc in documents_strs if doc]
        ).pop()
        s3_quote_path = document_dir
    if token.permissions >= auth.Permissions.developer and quote_doc:
        quote_file = File(
            file_name=S3_DIR + quote_doc.filename,
            file_mime=quote_doc.content_type,
            file_content=await quote_doc.read(),
        )
        s3_path = f"{s3_quote_path}/{quote_file.file_name}"
        await S3.upload_file(quote_file, s3_path)
        attrs["quote-doc"] = s3_path
    if token.permissions >= auth.Permissions.customer_std and plans_doc:
        plans_file = File(
            file_name=S3_DIR + plans_doc.filename,
            file_mime=plans_doc.content_type,
            file_content=await plans_doc.read(),
        )
        s3_path = f"{s3_quote_path}/{plans_file.file_name}"
        await S3.upload_file(plans_file, s3_path)
        attrs["plans-doc"] = s3_path

    updated_quote_obj = {
        "id": quote_id,
        "type": QUOTES_RESOURCE,
        "attributes": attrs,
        "relationships": {
            "adp-customers": {"data": {"id": adp_customer_id, "type": "adp-customers"}},
        },
    }
    return await modify_quote(
        token,
        session,
        quote_id,
        ExistingQuoteRequest(data=updated_quote_obj),
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
        .allow_customer("std")
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
