from __future__ import annotations

import uuid
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from backend.config import get_settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png"}
FORMAT_TO_EXTENSION = {"JPEG": ".jpg", "PNG": ".png"}


async def read_validated_image(file: UploadFile) -> tuple[bytes, str, str, int]:
    settings = get_settings()
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A file name is required.")

    extension = Path(filename).suffix.lower()
    content_type = (file.content_type or "").lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPG, JPEG and PNG images are accepted.",
        )
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid content type. Only JPEG and PNG images are accepted.",
        )

    data = await file.read(settings.max_upload_bytes + 1)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty.")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.max_upload_mb} MB.",
        )

    try:
        with Image.open(BytesIO(data)) as image:
            image_format = (image.format or "").upper()
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file is not a valid JPEG or PNG image.",
        ) from exc

    if image_format not in FORMAT_TO_EXTENSION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image format. Only JPEG and PNG are accepted.",
        )

    return data, filename[:255], content_type or f"image/{image_format.lower()}", len(data)


def save_image(user_id: int, data: bytes, extension: str) -> str:
    settings = get_settings()
    safe_extension = extension.lower()
    if safe_extension not in ALLOWED_EXTENSIONS:
        safe_extension = ".jpg"
    user_dir = settings.upload_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    relative_path = Path(str(user_id)) / f"{uuid.uuid4().hex}{safe_extension}"
    target = settings.upload_dir / relative_path
    target.write_bytes(data)
    return relative_path.as_posix()


def resolve_image_path(relative_path: str) -> Path:
    settings = get_settings()
    root = settings.upload_dir.resolve()
    candidate = (settings.upload_dir / relative_path).resolve()
    if root not in candidate.parents and candidate != root:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    return candidate


def extension_for(data: bytes) -> str:
    try:
        with Image.open(BytesIO(data)) as image:
            return FORMAT_TO_EXTENSION.get((image.format or "").upper(), ".jpg")
    except (UnidentifiedImageError, OSError, ValueError):
        return ".jpg"
