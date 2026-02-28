import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from fastapi import UploadFile, HTTPException
from app.core.config import settings


def _init_cloudinary():
    """Initialize Cloudinary with credentials from settings"""
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET
    )


async def upload_file(
    file: UploadFile,
    folder: str = "ceit-cms",
    resource_type: str = "auto"
) -> dict:
    
    #Upload file to Cloudinary
    #Args:
    #    file: The file to upload
    #    folder: Cloudinary folder path
    #    resource_type: Type of resource (auto, image, video, etc.)
    #Returns:
    #    dict with upload details including public_id, url, secure_url, etc
    
    _init_cloudinary()
    
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=folder,
            resource_type=resource_type,
            public_id=file.filename.rsplit('.', 1)[0]  # Remove extension for public_id
        )
        
        return {
            "public_id": result.get("public_id"),
            "url": result.get("url"),
            "secure_url": result.get("secure_url"),
            "resource_type": result.get("resource_type"),
            "file_size": result.get("bytes"),
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )


async def delete_file(public_id: str, resource_type: str = "image") -> dict:

    # Delete file from Cloudinary
    #Args:
    #    public_id: Cloudinary public ID of the file to delete
    #   resource_type: Type of resource (image, video, etc.)
    #Returns:
    #    dict with deletion result
    
    _init_cloudinary()
    
    try:
        result = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type
        )
        
        return {"message": "File deleted successfully", "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File deletion failed: {str(e)}"
        )
