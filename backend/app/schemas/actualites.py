from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActualiteBase(BaseModel):
    titre: str
    resume: Optional[str] = None
    contenu: str
    image_url: Optional[str] = None
    paroisse_id: int


class ActualiteCreate(ActualiteBase):
    pass


class ActualiteUpdate(BaseModel):
    titre: Optional[str] = None
    resume: Optional[str] = None
    contenu: Optional[str] = None
    image_url: Optional[str] = None
    paroisse_id: Optional[int] = None
    publie: Optional[bool] = None


class ActualiteOut(ActualiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publie: bool
    auteur_id: int
    created_at: datetime
    updated_at: datetime