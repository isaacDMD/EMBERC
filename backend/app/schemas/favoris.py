from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.enums.favoris_type import FavorisTypeEnum

class FavorisCreate(BaseModel):
    type_favoris : FavorisTypeEnum
    item_id : int

class FavorisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    user_id : int
    type_favoris : FavorisTypeEnum
    item_id : int
    created_at : datetime