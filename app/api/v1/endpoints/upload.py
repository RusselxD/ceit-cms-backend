from fastapi import APIRouter, File, UploadFile, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.upload import FileUploadResponse, FileDeleteResponse, FileDeleteRequest
from app.services import upload_service
from app.api.v1.dependencies import require_auth, CurrentUser


router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/image", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_auth)
):
    
    # Upload an image to Cloudinary.
    #Requires authentication. The image will be stored in the 'ceit-cms/images' folder.
    result = await upload_service.upload_file(
        file=file,
        folder="ceit-cms/images",
        resource_type="image"
    )
    return result


@router.post("/video", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_auth)
):
    
    # Upload a video to Cloudinary.
    # Requires authentication. The video will be stored in the 'ceit-cms/videos' folder.
    result = await upload_service.upload_file(
        file=file,
        folder="ceit-cms/videos",
        resource_type="video"
    )
    return result


@router.post("/document", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_auth)
):
    
    # Upload a document (PDF, DOCX, etc.) to Cloudinary.
    # Requires authentication. The file will be stored in the 'ceit-cms/documents' folder.
    result = await upload_service.upload_file(
        file=file,
        folder="ceit-cms/documents",
        resource_type="raw"
    )
    return result


@router.post("/", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query("ceit-cms", description="Cloudinary folder path"),
    current_user: CurrentUser = Depends(require_auth)
):
    
    #Upload a file to Cloudinary with custom folder.
    #Requires authentication.
    #Query Parameters:
    # - folder: Location in Cloudinary (default: ceit-cms)
    result = await upload_service.upload_file(
        file=file,
        folder=folder,
        resource_type="auto"
    )
    return result


@router.delete("/{file_id:path}", response_model=FileDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_file(
    file_id: str,
    resource_type: str = Query("image", description="Resource type (image, video, raw)"),
    current_user: CurrentUser = Depends(require_auth)
):
    
    #Delete a file from Cloudinary.
    #Requires authentication. The file_id is the Cloudinary public_id.
    result = await upload_service.delete_file(
        public_id=file_id,
        resource_type=resource_type
    )
    return result
