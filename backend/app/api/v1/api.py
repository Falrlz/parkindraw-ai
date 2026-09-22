"""API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, models, predict

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(models.router, tags=["Models"])
api_router.include_router(predict.router, tags=["Inference & Screening"])
