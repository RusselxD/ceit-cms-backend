from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool

from app.api.v1.dependencies import CurrentUser, require_auth
from app.schemas import UploadResponse
from app.services import upload_service


router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    folder: str | None = None,
    public_id: str | None = None,
    current_user: CurrentUser = Depends(require_auth),
):
    """Upload a file to Cloudinary (authenticated endpoint)."""

    try:
        result = await run_in_threadpool(
            upload_service.upload_to_cloudinary,
            file=file,
            folder=folder,
            public_id=public_id,
            resource_type="auto",
        )
        return UploadResponse(
            public_id=result["public_id"],
            secure_url=result["secure_url"],
            url=result["url"],
            resource_type=result["resource_type"],
            format=result.get("format"),
            bytes=result.get("bytes"),
            width=result.get("width"),
            height=result.get("height"),
            original_filename=result.get("original_filename"),
        )
    except upload_service.CloudinaryConfigError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    except ModuleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary dependency is not installed",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload failed",
        )
    finally:
        await file.close()
