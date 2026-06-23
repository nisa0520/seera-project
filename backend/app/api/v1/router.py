from fastapi import APIRouter

from app.api.v1.endpoints import conversations, education, feedback, image_analysis, backgrounds, vton

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(conversations.router)
api_router.include_router(feedback.router)
api_router.include_router(education.router)
api_router.include_router(image_analysis.router)
api_router.include_router(backgrounds.router)
api_router.include_router(vton.router)
