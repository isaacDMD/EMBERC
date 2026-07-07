from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.chant import Chants
from app.schemas.chants import ChantCreate, ChantUpdate


def create_chant(db: Session, payload: ChantCreate) -> Chants:
    chant = Chants(**payload.model_dump())
    db.add(chant)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("numero_deja_existant")
    db.refresh(chant)
    return chant


def get_chants(db: Session, page: int, limit: int) -> list[Chants]:
    return db.scalars(
        select(Chants).offset((page - 1) * limit).limit(limit)
    ).all()


def get_chant_by_id(db: Session, chant_id: int) -> Chants | None:
    return db.scalars(select(Chants).where(Chants.id == chant_id)).first()


def update_chant(db: Session, chant_id: int, payload: ChantUpdate) -> Chants | None:
    chant = get_chant_by_id(db, chant_id)
    if not chant:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chant, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("numero_deja_existant")
    db.refresh(chant)
    return chant