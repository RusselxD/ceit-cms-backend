from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID

from app.models.newsletter import Newsletter
from app.schemas.newsletter import NewsletterCreate, NewsletterUpdate


async def get_all_newsletters(db: AsyncSession) -> list[Newsletter]:
    result = await db.execute(
        select(Newsletter).order_by(Newsletter.is_latest.desc(), Newsletter.created_at.desc())
    )
    return list(result.scalars().all())


async def get_newsletter(db: AsyncSession, newsletter_id: UUID) -> Newsletter | None:
    result = await db.execute(select(Newsletter).where(Newsletter.id == newsletter_id))
    return result.scalar_one_or_none()


async def create_newsletter(db: AsyncSession, data: NewsletterCreate) -> Newsletter:
    # If this is marked as latest, unmark all others
    if data.is_latest:
        await db.execute(update(Newsletter).values(is_latest=0))

    newsletter = Newsletter(**data.model_dump())
    db.add(newsletter)
    await db.commit()
    await db.refresh(newsletter)
    return newsletter


async def update_newsletter(
    db: AsyncSession, newsletter_id: UUID, data: NewsletterUpdate
) -> Newsletter | None:
    newsletter = await get_newsletter(db, newsletter_id)
    if not newsletter:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # If marking as latest, unmark all others
    if update_data.get("is_latest"):
        await db.execute(update(Newsletter).values(is_latest=0))

    for key, value in update_data.items():
        setattr(newsletter, key, value)

    await db.commit()
    await db.refresh(newsletter)
    return newsletter


async def delete_newsletter(db: AsyncSession, newsletter_id: UUID) -> bool:
    newsletter = await get_newsletter(db, newsletter_id)
    if not newsletter:
        return False
    await db.delete(newsletter)
    await db.commit()
    return True
