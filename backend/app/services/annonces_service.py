from typing import Optional
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.annonces import Annonce
from app.schemas.annonces import AnnonceCreate, AnnonceUpdate


def create_annonce(db: Session, payload: AnnonceCreate, auteur_id: int) -> Annonce:
    annonce = Annonce(**payload.model_dump(), auteur_id=auteur_id)
    db.add(annonce)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(annonce)
    return annonce


def get_annonces(
    db: Session,
    page: int = 1,
    limit: int = 20,
    paroisse_id: Optional[int] = None,
    publie: Optional[bool] = None,
    actives_seulement: bool = False,
) -> list[Annonce]:
    stmt = select(Annonce)

    if paroisse_id is not None:
        stmt = stmt.where(Annonce.paroisse_id == paroisse_id)
    if publie is not None:
        stmt = stmt.where(Annonce.publie == publie)
    if actives_seulement:
        today = date.today()
        stmt = stmt.where(Annonce.date_debut <= today, Annonce.date_fin >= today)

    stmt = (
        stmt.order_by(Annonce.important.desc(), Annonce.date_debut.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_annonce_by_id(db: Session, annonce_id: int) -> Optional[Annonce]:
    return db.scalars(select(Annonce).where(Annonce.id == annonce_id)).first()


def update_annonce(
    db: Session, annonce_id: int, payload: AnnonceUpdate
) -> Optional[Annonce]:
    annonce = get_annonce_by_id(db, annonce_id)
    if not annonce:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(annonce, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(annonce)
    return annonce


def delete_annonce(db: Session, annonce_id: int) -> bool:
    annonce = get_annonce_by_id(db, annonce_id)
    if not annonce:
        return False
    db.delete(annonce)
    db.commit()
    return True