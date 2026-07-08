from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.enums.roles import RoleEnum


class UserCreate(BaseModel):
    nom: str
    prenom: str
    identifiant: str
    email: Optional[EmailStr] = None
    mot_de_passe: str
    role: Optional[RoleEnum] = RoleEnum.fidele
    paroisse_id: Optional[int] = None
    locale: Optional[str] = "fr"


class UserUpdateRole(BaseModel):
    role: RoleEnum


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str
    identifiant: str
    email: Optional[EmailStr] = None
    role: RoleEnum
    paroisse_id: Optional[int] = None
    locale: str
    created_at: datetime