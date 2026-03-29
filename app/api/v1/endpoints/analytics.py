from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/page-view")
async def track_public_page_view(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    payload = {}
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    path = str(payload.get("path") or request.headers.get("x-page-path") or "/")

    if len(path) > 255:
        raise HTTPException(status_code=400, detail="Path too long (max 255 chars)")
    if not path.startswith("/"):
        raise HTTPException(status_code=400, detail="Path must start with /")

    today = datetime.now(timezone.utc).date()

    await db.execute(
        text(
            """
            INSERT INTO public_page_views (day, path, views)
            VALUES (:day, :path, 1)
            ON CONFLICT (day, path)
            DO UPDATE SET views = public_page_views.views + 1
            """
        ),
        {"day": today, "path": path},
    )
    await db.commit()

    return {"message": "tracked"}
