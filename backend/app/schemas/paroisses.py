from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class ParoisseBase(BaseModel):
    nom: str
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pasteur_nom: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class ParoisseCreate(ParoisseBase):
    pass


class ParoisseUpdate(BaseModel):
    nom: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    pasteur_nom: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    actif: Optional[bool] = None


class ParoisseOut(ParoisseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actif: bool
    created_at: datetime
    updated_at: datetime