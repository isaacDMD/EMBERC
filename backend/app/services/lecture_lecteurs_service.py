from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.lecture_lecteurs import LectureLecteurs
from app.models.user import User
from app.schemas.lecture_lecteurs import LectureLecteurCreate, LecteurAssigne


def assign_lecteur(
    db: Session, lecture_id: int, payload: LectureLecteurCreate
) -> LectureLecteurs:
    item = LectureLecteurs(
        lecture_id=lecture_id,
        lecteur_id=payload.lecteur_id,
        langue=payload.langue,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("lecture_ou_lecteur_invalide")
    db.refresh(item)
    return item


def get_lecteurs_by_lecture(db: Session, lecture_id: int) -> list[LecteurAssigne]:
    stmt = (
        select(LectureLecteurs, User)
        .join(User, LectureLecteurs.lecteur_id == User.id)
        .where(LectureLecteurs.lecture_id == lecture_id)
    )
    rows = db.execute(stmt).all()

    return [
        LecteurAssigne(
            id=assoc.id,
            lecteur_id=user.id,
            langue=assoc.langue,
            nom=user.nom,
            prenom=user.prenom,
            created_at=assoc.created_at,
        )
        for assoc, user in rows
    ]


def get_association(db: Session, assoc_id: int) -> Optional[LectureLecteurs]:
    return db.scalars(
        select(LectureLecteurs).where(LectureLecteurs.id == assoc_id)
    ).first()


def remove_lecteur(db: Session, lecture_id: int, assoc_id: int) -> bool:
    item = get_association(db, assoc_id)
    if not item or item.lecture_id != lecture_id:
        return False
    db.delete(item)
    db.commit()
    return True