from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.site_content import SiteContent


async def get_page_content(db: AsyncSession, page: str) -> SiteContent | None:
    result = await db.execute(select(SiteContent).where(SiteContent.page == page))
    return result.scalar_one_or_none()


async def upsert_page_content(db: AsyncSession, page: str, content: dict) -> SiteContent:
    existing = await get_page_content(db, page)
    if existing:
        existing.content = content
        await db.commit()
        await db.refresh(existing)
        return existing

    new_record = SiteContent(page=page, content=content)
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record
