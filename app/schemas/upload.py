from pydantic import BaseModel
from typing import Optional


class FileUploadResponse(BaseModel):

    #Response model for file upload
    public_id: str
    url: str
    secure_url: str
    resource_type: str
    file_size: int
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

    class Config:
        from_attributes = True


class FileDeleteRequest(BaseModel):
    
    #Request model for file deletion
    public_id: str
    resource_type: str = "image"


class FileDeleteResponse(BaseModel):
    
    # Response model for file deletion
    message: str
    result: dict
