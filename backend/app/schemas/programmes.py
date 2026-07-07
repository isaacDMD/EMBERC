from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.culte_type import CulteTypeEnum


class ProgrammeCulteBase(BaseModel):
    titre: str
    type_culte: Optional[CulteTypeEnum] = CulteTypeEnum.DIMANCHE
    predicateur: Optional[str] = None
    date_heure: datetime
    paroisse_id: int


class ProgrammeCulteCreate(ProgrammeCulteBase):
    pass


class ProgrammeCulteUpdate(BaseModel):
    titre: Optional[str] = None
    type_culte: Optional[CulteTypeEnum] = None
    predicateur: Optional[str] = None
    date_heure: Optional[datetime] = None
    paroisse_id: Optional[int] = None
    publie: Optional[bool] = None


class ProgrammeCulteOut(ProgrammeCulteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publie: bool
    created_at: datetime
    updated_at: datetime