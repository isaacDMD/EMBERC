from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.favoris import Favoris
from app.schemas.favoris import FavorisCreate
from app.enums.favoris_type import FavorisTypeEnum


def add_favori(db: Session, user_id: int, payload: FavorisCreate) -> Favoris:
    favori = Favoris(user_id=user_id, **payload.model_dump())
    db.add(favori)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("favori_deja_existant")
    db.refresh(favori)
    return favori


def get_favoris_by_user(
    db: Session, user_id: int, type_favoris: Optional[FavorisTypeEnum] = None
) -> list[Favoris]:
    stmt = select(Favoris).where(Favoris.user_id == user_id)
    if type_favoris is not None:
        stmt = stmt.where(Favoris.type_favoris == type_favoris)
    stmt = stmt.order_by(Favoris.created_at.desc())
    return db.scalars(stmt).all()


def get_favori_by_id(db: Session, favori_id: int) -> Optional[Favoris]:
    return db.scalars(select(Favoris).where(Favoris.id == favori_id)).first()


def remove_favori(db: Session, user_id: int, favori_id: int) -> bool:
    favori = get_favori_by_id(db, favori_id)
    if not favori or favori.user_id != user_id:
        return False
    db.delete(favori)
    db.commit()
    return True