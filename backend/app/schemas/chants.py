from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.chant_categorie import CategorieChantEnum


class ChantBase(BaseModel):
    numero: str
    titre: str
    paroles: Optional[str] = None
    categorie: Optional[CategorieChantEnum] = CategorieChantEnum.CHANT
    auteur: Optional[str] = None
    fichier_audio_url: Optional[str] = None


class ChantCreate(ChantBase):
    pass


class ChantUpdate(BaseModel):
    numero: Optional[str] = None
    titre: Optional[str] = None
    paroles: Optional[str] = None
    categorie: Optional[CategorieChantEnum] = None
    auteur: Optional[str] = None
    fichier_audio_url: Optional[str] = None


class ChantOut(ChantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime