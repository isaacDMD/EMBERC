from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.enums.annonce_type import AnnonceType


class AnnonceBase(BaseModel):
    titre: str
    contenu: str
    type_annonce: Optional[AnnonceType] = AnnonceType.REUNION
    date_debut: date
    date_fin: date
    paroisse_id: int
    important: Optional[bool] = False


class AnnonceCreate(AnnonceBase):
    pass


class AnnonceUpdate(BaseModel):
    titre: Optional[str] = None
    contenu: Optional[str] = None
    type_annonce: Optional[AnnonceType] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    paroisse_id: Optional[int] = None
    important: Optional[bool] = None
    publie: Optional[bool] = None


class AnnonceOut(AnnonceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publie: bool
    auteur_id: int
    created_at: datetime
    updated_at: datetime