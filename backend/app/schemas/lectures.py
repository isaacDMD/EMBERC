from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LectureBibliqueBase(BaseModel):
    reference: str
    texte: Optional[str] = None
    date_lecture: datetime
    type_evenement: Optional[str] = None
    programme_id: int
    paroisse_id: int


class LectureBibliqueCreate(LectureBibliqueBase):
    pass


class LectureBibliqueUpdate(BaseModel):
    reference: Optional[str] = None
    texte: Optional[str] = None
    date_lecture: Optional[datetime] = None
    type_evenement: Optional[str] = None
    programme_id: Optional[int] = None
    paroisse_id: Optional[int] = None


class LectureBibliqueOut(LectureBibliqueBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime