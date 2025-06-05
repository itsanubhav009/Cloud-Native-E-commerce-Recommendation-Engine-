from fastapi import APIRouter
from app.api.endpoints import products, recommendations, users, analytics

router = APIRouter()

router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])