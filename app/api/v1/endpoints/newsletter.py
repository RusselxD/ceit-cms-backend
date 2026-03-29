from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.newsletter import NewsletterCreate, NewsletterUpdate, NewsletterResponse
from app.services import newsletter_service, upload_service
from app.api.v1.dependencies import CurrentUser, require_auth, require_permission


router = APIRouter(prefix="/newsletters", tags=["newsletters"])


@router.get("/", response_model=List[NewsletterResponse])
async def get_all_newsletters(db: AsyncSession = Depends(get_db)):
    """Get all newsletters (public endpoint)"""
    return await newsletter_service.get_all_newsletters(db)


@router.get("/{newsletter_id}", response_model=NewsletterResponse)
async def get_newsletter(
    newsletter_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single newsletter (public endpoint)"""
    newsletter = await newsletter_service.get_newsletter(db, newsletter_id)
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    return newsletter


@router.post("/", response_model=NewsletterResponse, status_code=status.HTTP_201_CREATED)
async def create_newsletter(
    data: NewsletterCreate,
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a newsletter (authenticated)"""
    return await newsletter_service.create_newsletter(db, data)


@router.put("/{newsletter_id}", response_model=NewsletterResponse)
async def update_newsletter(
    newsletter_id: UUID,
    data: NewsletterUpdate,
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update a newsletter (authenticated)"""
    newsletter = await newsletter_service.update_newsletter(db, newsletter_id, data)
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    return newsletter


@router.delete("/{newsletter_id}", status_code=status.HTTP_200_OK)
async def delete_newsletter(
    newsletter_id: UUID,
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a newsletter (authenticated)"""
    deleted = await newsletter_service.delete_newsletter(db, newsletter_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Newsletter not found")
    return {"detail": "Newsletter deleted"}


@router.post("/{newsletter_id}/upload-pdf", response_model=NewsletterResponse)
async def upload_newsletter_pdf(
    newsletter_id: UUID,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a PDF for a newsletter to Cloudinary and store the URL"""
    newsletter = await newsletter_service.get_newsletter(db, newsletter_id)
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    # Validate PDF magic bytes
    header = await file.read(4)
    await file.seek(0)
    if header != b"%PDF":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content is not a valid PDF",
        )

    try:
        result = await run_in_threadpool(
            upload_service.upload_to_cloudinary,
            file=file,
            folder="ceit-cms/newsletters",
            resource_type="raw",
        )
    except upload_service.CloudinaryConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=400, detail="PDF upload failed")
    finally:
        await file.close()

    secure_url = result.get("secure_url")
    if not secure_url:
        raise HTTPException(status_code=502, detail="Upload failed: no URL returned")

    updated = await newsletter_service.update_newsletter(
        db, newsletter_id, NewsletterUpdate(pdf_url=secure_url)
    )
    return updated


@router.post("/{newsletter_id}/upload-cover", response_model=NewsletterResponse)
async def upload_newsletter_cover(
    newsletter_id: UUID,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a cover image for a newsletter to Cloudinary"""
    newsletter = await newsletter_service.get_newsletter(db, newsletter_id)
    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    ext = "." + (file.filename or "").rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, and WebP images are allowed",
        )

    try:
        result = await run_in_threadpool(
            upload_service.upload_to_cloudinary,
            file=file,
            folder="ceit-cms/newsletters",
            resource_type="image",
        )
    except upload_service.CloudinaryConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=400, detail="Cover upload failed")
    finally:
        await file.close()

    secure_url = result.get("secure_url")
    if not secure_url:
        raise HTTPException(status_code=502, detail="Upload failed: no URL returned")

    updated = await newsletter_service.update_newsletter(
        db, newsletter_id, NewsletterUpdate(cover_url=secure_url)
    )
    return updated
