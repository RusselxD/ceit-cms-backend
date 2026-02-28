from __future__ import annotations

from typing import Any

from fastapi import UploadFile

from app.core.config import settings


class CloudinaryConfigError(RuntimeError):
    pass


def _get_cloudinary_config() -> dict[str, str]:
    cloud_name = settings.CLOUDINARY_CLOUD_NAME
    api_key = settings.CLOUDINARY_API_KEY
    api_secret = settings.CLOUDINARY_API_SECRET

    missing: list[str] = []
    if not cloud_name:
        missing.append("CLOUDINARY_CLOUD_NAME")
    if not api_key:
        missing.append("CLOUDINARY_API_KEY")
    if not api_secret:
        missing.append("CLOUDINARY_API_SECRET")

    if missing:
        raise CloudinaryConfigError(
            "Cloudinary is not configured. Missing env vars: " + ", ".join(missing)
        )

    return {
        "cloud_name": cloud_name,
        "api_key": api_key,
        "api_secret": api_secret,
        "secure": True,
    }


def _configure_cloudinary() -> None:
    # Local import so app startup doesn't require the dependency unless used.
    import cloudinary

    cloudinary.config(**_get_cloudinary_config())


def upload_to_cloudinary(
    *,
    file: UploadFile,
    folder: str | None = None,
    public_id: str | None = None,
    resource_type: str = "auto",
) -> dict[str, Any]:
    """Upload a FastAPI UploadFile to Cloudinary.

    Returns the raw Cloudinary response (dict). This function is synchronous.
    """

    _configure_cloudinary()

    upload_folder = folder if folder is not None else settings.CLOUDINARY_FOLDER

    import cloudinary.uploader

    options: dict[str, Any] = {
        "resource_type": resource_type,
        "unique_filename": True,
        "overwrite": False,
    }
    if upload_folder:
        options["folder"] = upload_folder
    if public_id:
        options["public_id"] = public_id

    return cloudinary.uploader.upload(file.file, **options)
