from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleWithAuthor
from app.services import article_service
from app.api.v1.dependencies import CurrentUser, require_auth, require_permission


router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_in: ArticleCreate,
    current_user: CurrentUser = Depends(require_permission("article.create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new article (requires article.create permission)"""
    return await article_service.create_article(db, article_in, current_user.user_id)


@router.get("/", response_model=List[ArticleWithAuthor])
async def get_all_articles(
    db: AsyncSession = Depends(get_db)
):
    """Get all published articles (public endpoint)"""
    return await article_service.get_all_articles(db)


@router.get("/my-articles", response_model=List[ArticleWithAuthor])
async def get_my_articles(
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's articles"""
    return await article_service.get_my_articles(db, current_user.user_id)


@router.get("/{article_id}", response_model=ArticleWithAuthor)
async def get_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific article (public endpoint)"""
    return await article_service.get_article(db, article_id)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: UUID,
    article_in: ArticleUpdate,
    current_user: CurrentUser = Depends(require_permission("article.update")),
    db: AsyncSession = Depends(get_db)
):
    """Update an article (author or admin with article.update permission)"""
    return await article_service.update_article(db, article_id, article_in, current_user.user_id)

