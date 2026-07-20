from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.programme_culte import ProgrammeCulte
from app.schemas.programmes import ProgrammeCulteCreate, ProgrammeCulteUpdate


def create_programme(db: Session, payload: ProgrammeCulteCreate) -> ProgrammeCulte:
    programme = ProgrammeCulte(**payload.model_dump())
    db.add(programme)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(programme)
    return programme


def get_programmes(
    db: Session,
    page: int = 1,
    limit: int = 20,
    paroisse_id: Optional[int] = None,
    publie: Optional[bool] = None,
) -> list[ProgrammeCulte]:
    stmt = select(ProgrammeCulte)

    if paroisse_id is not None:
        stmt = stmt.where(ProgrammeCulte.paroisse_id == paroisse_id)
    if publie is not None:
        stmt = stmt.where(ProgrammeCulte.publie == publie)

    stmt = (
        stmt.order_by(ProgrammeCulte.date_heure.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_programme_by_id(db: Session, programme_id: int) -> Optional[ProgrammeCulte]:
    return db.scalars(
        select(ProgrammeCulte).where(ProgrammeCulte.id == programme_id)
    ).first()


def update_programme(
    db: Session, programme_id: int, payload: ProgrammeCulteUpdate
) -> Optional[ProgrammeCulte]:
    programme = get_programme_by_id(db, programme_id)
    if not programme:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(programme, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("paroisse_invalide")
    db.refresh(programme)
    return programme


def delete_programme(db: Session, programme_id: int) -> bool:
    programme = get_programme_by_id(db, programme_id)
    if not programme:
        return False
    db.delete(programme)
    db.commit()
    return True