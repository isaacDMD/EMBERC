from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.paroisse import Paroisse
from app.schemas.paroisses import ParoisseCreate, ParoisseUpdate


def get_paroisses(db: Session, page: int = 1, limit: int = 20) -> List[Paroisse]:
    offset = (page - 1) * limit
    return (
        db.query(Paroisse)
        .filter(Paroisse.actif == True)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_paroisse_by_id(db: Session, paroisse_id: int) -> Optional[Paroisse]:
    return db.query(Paroisse).filter(Paroisse.id == paroisse_id).first()


def create_paroisse(db: Session, payload: ParoisseCreate) -> Paroisse:
    paroisse = Paroisse(**payload.model_dump())
    db.add(paroisse)
    db.commit()
    db.refresh(paroisse)
    return paroisse


def update_paroisse(db: Session, paroisse: Paroisse, payload: ParoisseUpdate) -> Paroisse:
    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(paroisse, champ, valeur)
    db.commit()
    db.refresh(paroisse)
    return paroisse