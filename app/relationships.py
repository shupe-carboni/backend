"""Catch-all for undocumented links
    NOTE: removing from app setup on 2024-04-24.
    If enough time passes and this isen't needed. DELETE"""
from fastapi import APIRouter, HTTPException, status

err_desc_template = "{link_type} link {primary}/{id_}/{secondary} has not been implemented"
responses = {
    status.HTTP_501_NOT_IMPLEMENTED: {
        "description": "Not Implemented",
        "content": {
            "application/json": {
                "example": {
                    "detail": err_desc_template.format(
                        link_type="related",
                        primary="quotes",
                        id_=1,
                        secondary="customer"
                    )
                }
            }        
        }
    }
}

relationships = APIRouter(responses=responses)

@relationships.get("/{primary}/{id_}/{secondary}", tags=["Not Implemented"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_related_handler(
        primary: str,
        id_: int,
        secondary: str,
    ):
    """When implemented, returns a collection of resource objects representing the secondary resource
        similar to GET /secondary filtering for the primary resource id_"""
    link_type = "related"
    msg = err_desc_template.format(
        link_type=link_type,
        primary=primary,
        id_=id_,
        secondary=secondary
    )
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=msg)

@relationships.get("/{primary}/{id_}/relationships/{secondary}", tags=["Not Implemented"], status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_self_relationship_handler(
        primary: str,
        id_: int,
        secondary: str,
    ):
    """When implemented, returns a list of Resource Identifiers: { "type": type, "id": id } related to id_
        where the type is the seconady resource"""
    link_type = "self"
    msg = err_desc_template.format(
        link_type=link_type,
        primary=primary,
        id_=id_,
        secondary=secondary
    )
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=msg)