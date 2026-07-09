from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.actualites import Actualite
from app.schemas.actualites import ActualiteCreate, ActualiteUpdate


def create_actualite(db: Session, payload: ActualiteCreate, auteur_id: int) -> Actualite:
    actualite = Actualite(**payload.model_dump(), auteur_id=auteur_id)
    db.add(actualite)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(actualite)
    return actualite


def get_actualites(
    db: Session,
    page: int = 1,
    limit: int = 20,
    paroisse_id: Optional[int] = None,
    publie: Optional[bool] = None,
) -> list[Actualite]:
    stmt = select(Actualite)

    if paroisse_id is not None:
        stmt = stmt.where(Actualite.paroisse_id == paroisse_id)
    if publie is not None:
        stmt = stmt.where(Actualite.publie == publie)

    stmt = (
        stmt.order_by(Actualite.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_actualite_by_id(db: Session, actualite_id: int) -> Optional[Actualite]:
    return db.scalars(select(Actualite).where(Actualite.id == actualite_id)).first()


def update_actualite(
    db: Session, actualite_id: int, payload: ActualiteUpdate
) -> Optional[Actualite]:
    actualite = get_actualite_by_id(db, actualite_id)
    if not actualite:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(actualite, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(actualite)
    return actualite


def delete_actualite(db: Session, actualite_id: int) -> bool:
    actualite = get_actualite_by_id(db, actualite_id)
    if not actualite:
        return False
    db.delete(actualite)
    db.commit()
    return True