from typing import Optional
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.evenement import Evenement
from app.schemas.evenements import EvenementCreate, EvenementUpdate


def create_evenement(db: Session, payload: EvenementCreate) -> Evenement:
    evenement = Evenement(**payload.model_dump())
    db.add(evenement)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(evenement)
    return evenement


def get_evenements(
    db: Session,
    page: int = 1,
    limit: int = 20,
    paroisse_id: Optional[int] = None,
    publie: Optional[bool] = None,
    a_venir_seulement: bool = False,
) -> list[Evenement]:
    stmt = select(Evenement)

    if paroisse_id is not None:
        stmt = stmt.where(Evenement.paroisse_id == paroisse_id)
    if publie is not None:
        stmt = stmt.where(Evenement.publie == publie)
    if a_venir_seulement:
        stmt = stmt.where(Evenement.date_fin >= date.today())

    stmt = (
        stmt.order_by(Evenement.date_debut.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_evenement_by_id(db: Session, evenement_id: int) -> Optional[Evenement]:
    return db.scalars(select(Evenement).where(Evenement.id == evenement_id)).first()


def update_evenement(
    db: Session, evenement_id: int, payload: EvenementUpdate
) -> Optional[Evenement]:
    evenement = get_evenement_by_id(db, evenement_id)
    if not evenement:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evenement, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(evenement)
    return evenement


def delete_evenement(db: Session, evenement_id: int) -> bool:
    evenement = get_evenement_by_id(db, evenement_id)
    if not evenement:
        return False
    db.delete(evenement)
    db.commit()
    return True