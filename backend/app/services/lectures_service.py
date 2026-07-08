from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.lecture_biblique import LectureBiblique
from app.schemas.lectures import LectureBibliqueCreate, LectureBibliqueUpdate


def create_lecture(db: Session, payload: LectureBibliqueCreate) -> LectureBiblique:
    lecture = LectureBiblique(**payload.model_dump())
    db.add(lecture)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("programme_ou_paroisse_invalide")
    db.refresh(lecture)
    return lecture


def get_lectures(
    db: Session,
    page: int = 1,
    limit: int = 20,
    paroisse_id: Optional[int] = None,
    programme_id: Optional[int] = None,
) -> list[LectureBiblique]:
    stmt = select(LectureBiblique)

    if paroisse_id is not None:
        stmt = stmt.where(LectureBiblique.paroisse_id == paroisse_id)
    if programme_id is not None:
        stmt = stmt.where(LectureBiblique.programme_id == programme_id)

    stmt = (
        stmt.order_by(LectureBiblique.date_lecture.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return db.scalars(stmt).all()


def get_lecture_by_id(db: Session, lecture_id: int) -> Optional[LectureBiblique]:
    return db.scalars(
        select(LectureBiblique).where(LectureBiblique.id == lecture_id)
    ).first()


def update_lecture(
    db: Session, lecture_id: int, payload: LectureBibliqueUpdate
) -> Optional[LectureBiblique]:
    lecture = get_lecture_by_id(db, lecture_id)
    if not lecture:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lecture, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("programme_ou_paroisse_invalide")
    db.refresh(lecture)
    return lecture


def delete_lecture(db: Session, lecture_id: int) -> bool:
    lecture = get_lecture_by_id(db, lecture_id)
    if not lecture:
        return False
    db.delete(lecture)
    db.commit()
    return True