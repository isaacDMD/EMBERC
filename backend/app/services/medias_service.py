from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.media import Medias
from app.schemas.medias import MediaCreate, MediaUpdate
from app.enums.medias_type import MediaTypeEnum


def create_media(db: Session, payload: MediaCreate) -> Medias:
    media = Medias(**payload.model_dump())
    db.add(media)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(media)
    return media


def get_medias(
    db: Session,
    page: int = 1,
    limit: int = 20,
    paroisse_id: Optional[int] = None,
    publie: Optional[bool] = None,
    type_media: Optional[MediaTypeEnum] = None,
) -> list[Medias]:
    stmt = select(Medias)

    if paroisse_id is not None:
        stmt = stmt.where(Medias.paroisse_id == paroisse_id)
    if publie is not None:
        stmt = stmt.where(Medias.publie == publie)
    if type_media is not None:
        stmt = stmt.where(Medias.type_media == type_media)

    stmt = (
        stmt.order_by(Medias.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_media_by_id(db: Session, media_id: int) -> Optional[Medias]:
    return db.scalars(select(Medias).where(Medias.id == media_id)).first()


def update_media(db: Session, media_id: int, payload: MediaUpdate) -> Optional[Medias]:
    media = get_media_by_id(db, media_id)
    if not media:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(media, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(media)
    return media


def delete_media(db: Session, media_id: int) -> bool:
    media = get_media_by_id(db, media_id)
    if not media:
        return False
    db.delete(media)
    db.commit()
    return True