from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from datetime import datetime, timezone

from app.models.article import Article, ArticleStatus
from app.models.user import User
from app.schemas.article import ArticleCreate, ArticleUpdate
from .base import CRUDBase


class ArticleRepository(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    
    async def get_by_id(self, db: AsyncSession, article_id: UUID) -> Optional[Article]:
        result = await db.execute(
            select(Article)
            .filter(Article.id == article_id)
            .options(selectinload(Article.author).selectinload(User.role))
            .execution_options(populate_existing=False)
        )
        return result.scalars().first()
    
    async def get_all_with_author(self, db: AsyncSession) -> List[Article]:
        result = await db.execute(
            select(Article)
            .options(selectinload(Article.author))
            .execution_options(populate_existing=False)
        )
        return result.scalars().unique().all()
    
    async def get_by_author(self, db: AsyncSession, author_id: UUID) -> List[Article]:
        result = await db.execute(
            select(Article)
            .filter(Article.author_id == author_id)
            .options(selectinload(Article.author))
            .execution_options(populate_existing=False)
        )
        return result.scalars().unique().all()
    
    async def get_by_status(self, db: AsyncSession, status: ArticleStatus) -> List[Article]:
        result = await db.execute(
            select(Article)
            .filter(Article.status == status)
            .options(selectinload(Article.author))
            .execution_options(populate_existing=False)
        )
        return result.scalars().unique().all()
    
    async def create_article(
        self, 
        db: AsyncSession, 
        article_in: ArticleCreate, 
        author_id: UUID
    ) -> Article:
        article_data = article_in.model_dump()
        article_data["author_id"] = author_id
        db_article = Article(**article_data)
        db.add(db_article)
        await db.commit()
        await db.refresh(db_article)
        return db_article
    
    async def update_article(
        self, 
        db: AsyncSession, 
        article_id: UUID, 
        article_in: ArticleUpdate
    ) -> Optional[Article]:
        result = await db.execute(
            select(Article).filter(Article.id == article_id)
        )
        article = result.scalars().first()
        if not article:
            return None
        
        update_data = article_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(article, field, value)
        
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article
    
    async def delete_article(self, db: AsyncSession, article_id: UUID) -> Optional[Article]:
        result = await db.execute(
            select(Article).filter(Article.id == article_id)
        )
        article = result.scalars().first()
        if article:
            article.status = ArticleStatus.ARCHIVED
            article.archived_at = datetime.now(timezone.utc)
            db.add(article)
            await db.commit()
            await db.refresh(article)
        return article


article_repo = ArticleRepository(Article)
