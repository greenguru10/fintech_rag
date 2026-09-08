"""Main API router combining all route endpoints."""

from fastapi import APIRouter
from app.api.routes import chat, calculations, documents, sources, feedback, health

api_router = APIRouter()

api_router.include_router(chat.router)
api_router.include_router(calculations.router)
api_router.include_router(documents.router)
api_router.include_router(sources.router)
api_router.include_router(feedback.router)
api_router.include_router(health.router)
