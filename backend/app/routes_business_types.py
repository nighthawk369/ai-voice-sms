"""API endpoints for business type management"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.industry_config import get_all_business_types

router = APIRouter(prefix="/api/v1", tags=["business-types"])


@router.get("/business-types")
async def get_business_types(db: AsyncSession = Depends(get_db)):
    """
    Get all supported business types for dropdown selection

    Returns list of business types grouped by category
    """
    business_types = get_all_business_types()

    return {
        "business_types": business_types,
        "total": len(business_types),
        "categories": list(set(bt["category"] for bt in business_types)),
    }


@router.get("/business-types/{business_type}")
async def get_business_type_details(business_type: str, db: AsyncSession = Depends(get_db)):
    """
    Get details for a specific business type

    Returns configuration, features, and custom fields for the business type
    """
    from app.industry_config import (
        INDUSTRY_CONFIGS,
        get_custom_fields,
        get_features,
        get_intents,
    )

    if business_type not in INDUSTRY_CONFIGS:
        return {"error": f"Business type '{business_type}' not found"}

    config = INDUSTRY_CONFIGS[business_type]

    return {
        "business_type": business_type,
        "display_name": config["display_name"],
        "description": config.get("description", ""),
        "category": config["category"],
        "system_prompt": config["system_prompt"],
        "custom_fields": get_custom_fields(business_type),
        "features": get_features(business_type),
        "intents": get_intents(business_type),
    }
