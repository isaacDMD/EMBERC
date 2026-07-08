from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.medias_type import MediaTypeEnum


class MediaBase(BaseModel):
    titre: str
    type_media: MediaTypeEnum
    description: Optional[str] = None
    url_media: str
    thumbnail_url: Optional[str] = None
    duree_secondes: Optional[int] = None
    paroisse_id: int


class MediaCreate(MediaBase):
    pass


class MediaUpdate(BaseModel):
    titre: Optional[str] = None
    type_media: Optional[MediaTypeEnum] = None
    description: Optional[str] = None
    url_media: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duree_secondes: Optional[int] = None
    paroisse_id: Optional[int] = None
    publie: Optional[bool] = None


class MediaOut(MediaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publie: bool
    created_at: datetime
    updated_at: datetime