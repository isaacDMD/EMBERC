from typing import Optional
from pydantic import BaseModel
from app.enums.chant_categorie import CategorieChantEnum


class ProgrammeChantCreate(BaseModel):
    chant_id: int
    ordre: int


class ProgrammeChantUpdate(BaseModel):
    ordre: int


class ChantDansProgramme(BaseModel):
    id: int  
    chant_id: int
    ordre: int
    titre: str
    numero: str
    categorie: Optional[CategorieChantEnum] = None