from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.site_content import SiteContentResponse, SiteContentUpdate
from app.services import site_content_service
from app.api.v1.dependencies import CurrentUser, require_auth


router = APIRouter(prefix="/site-content", tags=["site-content"])

VALID_PAGES = {"home", "academics", "administration"}


@router.get("/{page}", response_model=SiteContentResponse)
async def get_site_content(
    page: str,
    db: AsyncSession = Depends(get_db),
):
    """Get site content for a page (public endpoint)"""
    if page not in VALID_PAGES:
        raise HTTPException(status_code=404, detail=f"Page '{page}' not found")

    record = await site_content_service.get_page_content(db, page)
    if not record:
        raise HTTPException(status_code=404, detail=f"No content for page '{page}'")
    return record


@router.put("/{page}", response_model=SiteContentResponse)
async def update_site_content(
    page: str,
    data: SiteContentUpdate,
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update site content for a page (authenticated)"""
    if page not in VALID_PAGES:
        raise HTTPException(status_code=400, detail=f"Invalid page '{page}'")

    return await site_content_service.upsert_page_content(db, page, data.content)
