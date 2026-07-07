from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.programme_chants import ProgrammeChants
from app.models.chant import Chants
from app.schemas.programme_chants import ProgrammeChantCreate, ChantDansProgramme


def add_chant_to_programme(
    db: Session, programme_id: int, payload: ProgrammeChantCreate
) -> ProgrammeChants:
    item = ProgrammeChants(
        programme_culte_id=programme_id,
        chant_id=payload.chant_id,
        ordre=payload.ordre,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("programme_ou_chant_invalide")
    db.refresh(item)
    return item


def get_chants_by_programme(db: Session, programme_id: int) -> list[ChantDansProgramme]:
    stmt = (
        select(ProgrammeChants, Chants)
        .join(Chants, ProgrammeChants.chant_id == Chants.id)
        .where(ProgrammeChants.programme_culte_id == programme_id)
        .order_by(ProgrammeChants.ordre)
    )
    rows = db.execute(stmt).all()

    return [
        ChantDansProgramme(
            id=assoc.id,
            chant_id=chant.id,
            ordre=assoc.ordre,
            titre=chant.titre,
            numero=chant.numero,
            categorie=chant.categorie,
        )
        for assoc, chant in rows
    ]


def get_association(db: Session, programme_id: int, chant_id: int) -> Optional[ProgrammeChants]:
    return db.scalars(
        select(ProgrammeChants).where(
            ProgrammeChants.programme_culte_id == programme_id,
            ProgrammeChants.chant_id == chant_id,
        )
    ).first()


def update_ordre(
    db: Session, programme_id: int, chant_id: int, nouvel_ordre: int
) -> Optional[ProgrammeChants]:
    item = get_association(db, programme_id, chant_id)
    if not item:
        return None
    item.ordre = nouvel_ordre
    db.commit()
    db.refresh(item)
    return item


def remove_chant_from_programme(db: Session, programme_id: int, chant_id: int) -> bool:
    item = get_association(db, programme_id, chant_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True