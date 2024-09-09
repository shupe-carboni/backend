
from typing import Annotated
from fastapi import Depends
from fastapi.routing import APIRouter
from app import auth
from app.db import SCA_DB, Session
from app.jsonapi.core_models import convert_query
#from app.RELATED_RESOURCE.models import 
from app.v2.models import (
    VendorProductResp,
    VendorProductQuery,
    VendorProductQueryJSONAPI,
)
from app.jsonapi.sqla_models import VendorProduct

PARENT_PREFIX = "/vendors/v2"
VENDOR_PRODUCTS = VendorProduct.__jsonapi_type_override__

vendor_products = APIRouter(
    prefix=f"/{VENDOR_PRODUCTS}", tags=["v2", ""]
)

Token = Annotated[auth.VerifiedToken, Depends(auth.authenticate_auth0_token)]
NewSession = Annotated[Session, Depends(SCA_DB.get_db)]
converter = convert_query(VendorProductQueryJSONAPI)


@vendor_products.get(
    "",
    response_model=VendorProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_collection(
    token: Token, session: NewSession, query: VendorProductQuery = Depends()
) -> VendorProductResp:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query))
    )


@vendor_products.get(
    "/{vendor_product_id}",
    response_model=VendorProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_resource(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> VendorProductResp:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id)
    )


@vendor_products.get(
    "/{vendor_product_id}/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_related_vendors(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendors")
    )

@vendor_products.get(
    "/{vendor_product_id}/relationships/vendors",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_relationships_vendors(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendors", True)
    )

    
@vendor_products.get(
    "/{vendor_product_id}/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_related_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-pricing-by-class")
    )

@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-pricing-by-class",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_relationships_vendor_pricing_by_class(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-pricing-by-class", True)
    )

    
@vendor_products.get(
    "/{vendor_product_id}/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_related_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-pricing-by-customer")
    )

@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-pricing-by-customer",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_relationships_vendor_pricing_by_customer(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-pricing-by-customer", True)
    )

    
@vendor_products.get(
    "/{vendor_product_id}/vendor-product-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_related_vendor_product_attrs(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-product-attrs")
    )

@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-product-attrs",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_relationships_vendor_product_attrs(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-product-attrs", True)
    )

    
@vendor_products.get(
    "/{vendor_product_id}/vendor-product-to-class-mapping",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_related_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-product-to-class-mapping")
    )

@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-product-to-class-mapping",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_relationships_vendor_product_to_class_mapping(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-product-to-class-mapping", True)
    )

    
@vendor_products.get(
    "/{vendor_product_id}/vendor-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_related_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-quote-products")
    )

@vendor_products.get(
    "/{vendor_product_id}/relationships/vendor-quote-products",
    response_model=None,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def vendor_product_relationships_vendor_quote_products(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    query: VendorProductQuery = Depends(),
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .get(session, converter(query), vendor_product_id, "vendor-quote-products", True)
    )

    

from app.v2.models import ModVendorProduct

@vendor_products.patch(
    "/{vendor_product_id}",
    response_model=VendorProductResp,
    response_model_exclude_none=True,
    tags=["jsonapi"],
)
async def mod_vendor_product(
    token: Token,
    session: NewSession,
    vendor_product_id: int,
    mod_data: ModVendorProduct,
) -> VendorProductResp:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .patch(
            session=session,
            data=mod_data.model_dump(exclude_none=True, by_alias=True),
            obj_id=vendor_product_id,
                primary_id=mod_data.data.relationships.vendors.data.id
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
    vendor_id: int,
) -> None:
    return (
        auth.VOperations(token, VendorProduct, PARENT_PREFIX)
        .allow_admin()
        .allow_sca()
        .allow_dev()
        .allow_customer("std")
        .delete(session, obj_id=vendor_product_id, primary_id=vendor_id)
    )
    