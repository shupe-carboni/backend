from typing import Annotated
from logging import getLogger
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from app import auth
from app.db import DB_V2, Session
from app.db.sql import queries
from app.v2.models import VendorProductResourceResp, ModVendorProduct, NewVendorProduct
from app.jsonapi.sqla_models import VendorProduct

PARENT_PREFIX = "/vendors"
VENDOR_PRODUCTS = VendorProduct.__jsonapi_type_override__

vendor_products = APIRouter(prefix=f"/{VENDOR_PRODUCTS}", tags=["v2"])

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(DB_V2.get_db)]

logger = getLogger("uvicorn.info")


@vendor_products.post(
    "",
    response_model=VendorProductResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def new_vendor_product(
    token: Token,
    session: NewSession,
    new_obj: NewVendorProduct,
) -> VendorProductResourceResp:
    vendor_id = new_obj.data.relationships.vendors.data.id
    custom_attributes = new_obj.data.attributes.vendor_product_attrs
    try:
        ret = (
            auth.VendorOperations2(token, VendorProduct, PARENT_PREFIX, id=vendor_id)
            .allow_admin()
            .allow_sca()
            .allow_dev()
            .post(
                session=session,
                data=new_obj.model_dump(exclude_none=True, by_alias=True),
                primary_id=vendor_id,
            )
        )
    except Exception as e:
        raise e
    else:
        new_id = ret["data"]["id"]
        params = []
        if custom_attributes:
            logger.info("new product added - registering custom_attributes")
            for attr in custom_attributes:
                attr_dict = attr.model_dump(exclude_none=True)
                match attr_dict:
                    case {"attr": a, "type": b, "value": c}:
                        logger.info(f"Adding attribute: {attr}")
                        params.append(attr_dict | {"vendor_product_id": new_id})
                    case _:
                        logger.warning(
                            "Ignored custom attribute due to mismatch"
                            f"between obj structure and expected structure. Got: {attr}"
                        )
            try:
                DB_V2.execute(session, queries.insert_vendor_product_attrs, params)
            except Exception as e:
                logger.error(e)
            else:
                session.commit()
            finally:
                return ret
        logger.info(f"No custom attributes provided")
        return ret


@vendor_products.patch(
    "/{vendor_product_id}",
    response_model=VendorProductResourceResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    mod_data: ModVendorProduct,
) -> VendorProductResourceResp:
    vendor_id = mod_data.data.relationships.vendors.data.id
    return (
        auth.VendorOperations2(token, VendorProduct, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_id,
            primary_id=vendor_id,
        )
    )


@vendor_products.delete(
    "/{vendor_product_id}",
    tags=["jsonapi"],
)
async def del_vendor_product(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    vendor_id: str,
) -> None:
    return (
        auth.VendorOperations2(token, VendorProduct, PARENT_PREFIX, id=vendor_id)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .delete(session, obj_id=vendor_product_id, primary_id=vendor_id)
    )


## NOT IMPLEMENTED ##


@vendor_products.get("", tags=["jsonapi"])
async def vendor_product_collection(
    token: Token, session: NewSession
) -> VendorProductResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get("/{vendor_product_id}", tags=["Not Implemented"])
async def vendor_product_resource(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> VendorProductResourceResp:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get("/{vendor_product_id}/vendors", tags=["Not Implemented"])
async def vendor_product_related_vendors(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/relationships/vendors", tags=["Not Implemented"]
)
async def vendor_product_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/vendor-pricing-by-class", tags=["Not Implemented"]
)
async def vendor_product_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-pricing-by-class",
    tags=["Not Implemented"],
)
async def vendor_product_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/vendor-pricing-by-customer", tags=["Not Implemented"]
)
async def vendor_product_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-pricing-by-customer",
    tags=["Not Implemented"],
)
async def vendor_product_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/vendor-product-attrs", tags=["Not Implemented"]
)
async def vendor_product_related_vendor_product_attrs(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-product-attrs", tags=["Not Implemented"]
)
async def vendor_product_relationships_vendor_product_attrs(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/vendor-product-to-class-mapping", tags=["Not Implemented"]
)
async def vendor_product_related_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-product-to-class-mapping",
    tags=["Not Implemented"],
)
async def vendor_product_relationships_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/vendor-quote-products", tags=["Not Implemented"]
)
async def vendor_product_related_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)


@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-quote-products", tags=["Not Implemented"]
)
async def vendor_product_relationships_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
