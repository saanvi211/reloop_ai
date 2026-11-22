from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Identification, User
from backend.schemas import IdentificationCreate, IdentificationList, IdentificationRead
from backend.serializers import identification_to_dict
from backend.services.images import extension_for, read_validated_image, resolve_image_path, save_image
from data.mock_data import IDENTIFY_CATEGORIES
from utils.helpers import device_from_category
from utils.identification import manual_identification, predict_from_image

router = APIRouter(prefix="/identifications", tags=["Identifications"])


def _validate_category(category: str) -> None:
    if category not in IDENTIFY_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported category. Choose one of: {', '.join(IDENTIFY_CATEGORIES)}.",
        )


@router.post("", response_model=IdentificationRead, status_code=status.HTTP_201_CREATED)
async def upload_identification(
    file: UploadFile = File(...),
    hint: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    data, filename, content_type, size = await read_validated_image(file)
    prediction = predict_from_image(data, filename, hint.strip())

    stored_path = save_image(current_user.id, data, extension_for(data))
    record = Identification(
        user_id=current_user.id,
        image_path=stored_path,
        original_filename=filename,
        content_type=content_type,
        file_size=size,
        device_category=prediction["device"],
        mapped_device=device_from_category(prediction["device"]),
        confidence=prediction["confidence"],
        predictions=prediction["predictions"],
        method=prediction["method"],
        needs_review=prediction["needs_review"],
        hint=hint.strip() or None,
        hint_matched=prediction.get("hint_matched"),
        source=prediction["source"],
    )
    db.add(record)
    try:
        db.commit()
    except Exception:
        db.rollback()
        try:
            resolve_image_path(stored_path).unlink(missing_ok=True)
        except OSError:
            pass
        raise
    db.refresh(record)
    return identification_to_dict(record)


@router.post("/manual", response_model=IdentificationRead, status_code=status.HTTP_201_CREATED)
def manual_create(
    payload: IdentificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    _validate_category(payload.category)
    prediction = manual_identification(payload.category)
    record = Identification(
        user_id=current_user.id,
        image_path=None,
        original_filename=None,
        content_type=None,
        file_size=None,
        device_category=prediction["device"],
        mapped_device=device_from_category(prediction["device"]),
        confidence=prediction["confidence"],
        predictions=prediction["predictions"],
        method=prediction["method"],
        needs_review=False,
        hint=payload.hint.strip() if payload.hint else None,
        hint_matched=None,
        source="manual selection",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return identification_to_dict(record)


@router.get("", response_model=IdentificationList)
def list_identifications(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    base = select(Identification).where(Identification.user_id == current_user.id)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    records = db.scalars(
        base.order_by(Identification.created_at.desc()).limit(limit).offset(offset)
    ).all()
    return {"items": [identification_to_dict(record) for record in records], "total": total}


@router.get("/{identification_id}", response_model=IdentificationRead)
def get_identification(
    identification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    record = db.get(Identification, identification_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Identification not found.")
    return identification_to_dict(record)


@router.get("/{identification_id}/image")
def get_identification_image(
    identification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    record = db.get(Identification, identification_id)
    if record is None or record.user_id != current_user.id or not record.image_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    path = resolve_image_path(record.image_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    media_type = record.content_type or ("image/png" if path.suffix.lower() == ".png" else "image/jpeg")
    return FileResponse(path, media_type=media_type, headers={"Cache-Control": "private, max-age=3600"})


@router.delete("/{identification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_identification(
    identification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    record = db.get(Identification, identification_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Identification not found.")
    image_path = record.image_path
    db.delete(record)
    db.commit()
    if image_path:
        try:
            resolve_image_path(image_path).unlink(missing_ok=True)
        except (OSError, HTTPException):
            pass
    return None
