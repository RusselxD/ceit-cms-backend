from fastapi import APIRouter

from app.api.v1.endpoints import auth, article, upload, analytics, newsletter, site_content, users

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(article.router)
api_router.include_router(upload.router)
api_router.include_router(analytics.router)
api_router.include_router(newsletter.router)
api_router.include_router(site_content.router)
