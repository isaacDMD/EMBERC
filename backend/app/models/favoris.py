from sqlalchemy import Column, Enum, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base
from app.enums.favoris_type import FavorisTypeEnum

class Favoris(Base):
    __tablename__ = "favoris"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type_favoris = Column(Enum(FavorisTypeEnum, native_enum=False), nullable=False)
    item_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())