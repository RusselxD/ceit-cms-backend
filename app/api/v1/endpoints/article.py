from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, text
from pathlib import Path
import uuid
import io
import cloudinary
import cloudinary.uploader

from app.core.database import get_db
from app.core.config import settings
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleWithAuthor
from app.services import article_service
from app.api.v1.dependencies import CurrentUser, require_auth, require_permission, require_role
from app.models.article import Article, ArticleStatus
from app.models.user import User
from app.models.role import Role


router = APIRouter(prefix="/articles", tags=["articles"])

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    article_in: ArticleCreate,
    current_user: CurrentUser = Depends(require_permission("article.create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new article (requires article.create permission)"""
    return await article_service.create_article(db, article_in, current_user.user_id)


@router.post("/{article_id}/upload-image", response_model=ArticleResponse)
async def upload_article_image_for_article(
    article_id: UUID,
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_permission("article.update")),
    db: AsyncSession = Depends(get_db),
):
    """Upload article image to Cloudinary and persist it on a specific article."""
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Allowed: jpg, jpeg, png, webp, gif",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is too large. Maximum size is 5MB",
        )

    if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY or not settings.CLOUDINARY_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary is not configured on the server",
        )

    try:
        uploaded = cloudinary.uploader.upload(
            io.BytesIO(content),
            folder=settings.CLOUDINARY_FOLDER,
            public_id=uuid.uuid4().hex,
            overwrite=False,
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Image upload failed: {exc}",
        )

    secure_url = uploaded.get("secure_url")
    if not secure_url:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Image upload failed: no URL returned",
        )

    return await article_service.update_article(
        db,
        article_id,
        ArticleUpdate(image_path=secure_url),
        current_user,
    )


@router.get("/", response_model=List[ArticleWithAuthor])
async def get_all_articles(
    db: AsyncSession = Depends(get_db)
):
    """Get all published articles (public endpoint)"""
    return await article_service.get_all_articles(db)


@router.get("/admin/all", response_model=List[ArticleWithAuthor])
async def get_all_articles_admin(
    current_user: CurrentUser = Depends(require_role("super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """Get all articles for admin dashboard (all statuses)"""
    return await article_service.get_all_articles_admin(db)


@router.get("/admin/analytics")
async def get_admin_analytics(
    current_user: CurrentUser = Depends(require_permission("article.update")),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard analytics with near real-time updates"""
    article_count_result = await db.execute(select(func.count(Article.id)))
    total_articles = int(article_count_result.scalar() or 0)

    approved_count_result = await db.execute(
        select(func.count(Article.id)).where(Article.status == ArticleStatus.APPROVED)
    )
    approved_articles = int(approved_count_result.scalar() or 0)

    active_admins_result = await db.execute(
        select(func.count(User.id))
        .join(Role, User.role_id == Role.id)
        .where((Role.name == "super_admin") | (Role.name.like("author_%")))
    )
    active_admins = int(active_admins_result.scalar() or 0)

    student_engagement = round((approved_articles / total_articles) * 100, 1) if total_articles else 0.0

    today = datetime.now(timezone.utc).date()
    days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]

    posts_by_day_result = await db.execute(
        select(func.date(Article.created_at), func.count(Article.id))
        .where(Article.created_at >= datetime.combine(days[0], datetime.min.time(), tzinfo=timezone.utc))
        .group_by(func.date(Article.created_at))
    )
    posts_by_day_raw = {str(day): int(count) for day, count in posts_by_day_result.all()}

    views_by_day_result = await db.execute(
        text(
            """
            SELECT day, COALESCE(SUM(views), 0) AS views
            FROM public_page_views
            WHERE day >= :start_day
            GROUP BY day
            ORDER BY day ASC
            """
        ),
        {"start_day": days[0]},
    )
    views_by_day_raw = {str(day): int(views) for day, views in views_by_day_result.all()}

    traffic_overview = []
    post_frequency = []

    for day in days:
        day_key = day.isoformat()
        label = day.strftime("%a")
        traffic_overview.append({"name": label, "views": int(views_by_day_raw.get(day_key, 0))})
        post_frequency.append({"name": label, "posts": int(posts_by_day_raw.get(day_key, 0))})

    total_views_result = await db.execute(text("SELECT COALESCE(SUM(views), 0) FROM public_page_views"))
    total_page_views = int(total_views_result.scalar() or 0)

    return {
        "total_page_views": total_page_views,
        "total_articles": total_articles,
        "student_engagement": student_engagement,
        "active_admins": active_admins,
        "traffic_overview": traffic_overview,
        "post_frequency": post_frequency,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


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


@router.post("/{article_id}/like", response_model=ArticleResponse)
async def like_article(
    article_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Increment article likes (public endpoint)"""
    return await article_service.like_article(db, article_id)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: UUID,
    article_in: ArticleUpdate,
    current_user: CurrentUser = Depends(require_permission("article.update")),
    db: AsyncSession = Depends(get_db)
):
    """Update an article (author or admin with article.update permission)"""
    return await article_service.update_article(db, article_id, article_in, current_user)


@router.delete("/{article_id}", status_code=status.HTTP_200_OK)
async def delete_article(
    article_id: UUID,
    current_user: CurrentUser = Depends(require_auth),
    db: AsyncSession = Depends(get_db)
):
    """Archive an article (author, or admin with article.archive permission)"""
    return await article_service.delete_article(db, article_id, current_user)

