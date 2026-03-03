from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import HTTPException, status

from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleWithAuthor
from app.api.v1.dependencies import CurrentUser
from app.repositories.article import article_repo
from app.core.authz import ensure_owner_or_superadmin


async def create_article(
    db: AsyncSession, 
    article_in: ArticleCreate, 
    author_id: UUID
) -> ArticleResponse:
    article = await article_repo.create_article(db, article_in, author_id)
    return ArticleResponse.model_validate(article)


async def get_article(db: AsyncSession, article_id: UUID) -> ArticleWithAuthor:
    article = await article_repo.get_by_id(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    return ArticleWithAuthor(
        id=article.id,
        author_id=article.author_id,
        title=article.title,
        body=article.body,
        category=article.category,
        like_count=article.like_count,
        image_path=article.image_path,
        image_alt_text=article.image_alt_text,
        status=article.status,
        created_at=article.created_at,
        updated_at=article.updated_at,
        approved_at=article.approved_at,
        archived_at=article.archived_at,
        author_first_name=article.author.first_name,
        author_last_name=article.author.last_name,
        author_email=article.author.email
    )


async def get_all_articles(db: AsyncSession) -> List[ArticleWithAuthor]:
    articles = await article_repo.get_public_with_author(db)
    return [
        ArticleWithAuthor(
            id=article.id,
            author_id=article.author_id,
            title=article.title,
            body=article.body,
            category=article.category,
            like_count=article.like_count,
            image_path=article.image_path,
            image_alt_text=article.image_alt_text,
            status=article.status,
            created_at=article.created_at,
            updated_at=article.updated_at,
            approved_at=article.approved_at,
            archived_at=article.archived_at,
            author_first_name=article.author.first_name,
            author_last_name=article.author.last_name,
            author_email=article.author.email
        )
        for article in articles
    ]


async def get_all_articles_admin(db: AsyncSession) -> List[ArticleWithAuthor]:
    articles = await article_repo.get_all_with_author(db)
    return [
        ArticleWithAuthor(
            id=article.id,
            author_id=article.author_id,
            title=article.title,
            body=article.body,
            category=article.category,
            like_count=article.like_count,
            image_path=article.image_path,
            image_alt_text=article.image_alt_text,
            status=article.status,
            created_at=article.created_at,
            updated_at=article.updated_at,
            approved_at=article.approved_at,
            archived_at=article.archived_at,
            author_first_name=article.author.first_name,
            author_last_name=article.author.last_name,
            author_email=article.author.email
        )
        for article in articles
    ]


async def get_my_articles(db: AsyncSession, author_id: UUID) -> List[ArticleWithAuthor]:
    articles = await article_repo.get_by_author(db, author_id)
    return [
        ArticleWithAuthor(
            id=article.id,
            author_id=article.author_id,
            title=article.title,
            body=article.body,
            category=article.category,
            like_count=article.like_count,
            image_path=article.image_path,
            image_alt_text=article.image_alt_text,
            status=article.status,
            created_at=article.created_at,
            updated_at=article.updated_at,
            approved_at=article.approved_at,
            archived_at=article.archived_at,
            author_first_name=article.author.first_name,
            author_last_name=article.author.last_name,
            author_email=article.author.email
        )
        for article in articles
    ]


async def update_article(
    db: AsyncSession, 
    article_id: UUID, 
    article_in: ArticleUpdate,
    current_user: CurrentUser
) -> ArticleResponse:
    # Check if article exists
    existing_article = await article_repo.get_by_id(db, article_id)
    if not existing_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    ensure_owner_or_superadmin(current_user, existing_article.author_id)
    
    article = await article_repo.update_article(db, article_id, article_in)
    return ArticleResponse.model_validate(article)


async def delete_article(db: AsyncSession, article_id: UUID, current_user: CurrentUser) -> dict:
    # Check if article exists
    existing_article = await article_repo.get_by_id(db, article_id)
    if not existing_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    ensure_owner_or_superadmin(current_user, existing_article.author_id)
    
    await article_repo.delete_article(db, article_id)
    return {"message": "Article archived successfully"}


async def like_article(db: AsyncSession, article_id: UUID) -> ArticleResponse:
    article = await article_repo.increment_like_count(db, article_id)
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )

    return ArticleResponse.model_validate(article)
