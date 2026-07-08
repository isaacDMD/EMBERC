from typing import Optional
from datetime import date
from datetime import datetime as dt
from pydantic import BaseModel, ConfigDict
from app.enums.evenement_type import EvenementTypeEnum


class EvenementBase(BaseModel):
    titre: str
    description: Optional[str] = None
    date_debut: date
    date_fin: date
    paroisse_id: int
    lieu: Optional[str] = None
    image_url: Optional[str] = None
    type_evenement: Optional[EvenementTypeEnum] = None


class EvenementCreate(EvenementBase):
    pass


class EvenementUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    paroisse_id: Optional[int] = None
    lieu: Optional[str] = None
    image_url: Optional[str] = None
    type_evenement: Optional[EvenementTypeEnum] = None
    publie: Optional[bool] = None


class EvenementOut(EvenementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publie: bool
    created_at: dt
    updated_at: dt