from sqlalchemy import Column, Enum, ForeignKey, Integer, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base
from app.enums.favoris_type import FavorisTypeEnum

class Favoris(Base):
    __tablename__ = "favoris"
    __table_args__ = (
        UniqueConstraint("user_id", "type_favoris", "item_id", name="uq_favoris_user_type_item"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type_favoris = Column(Enum(FavorisTypeEnum, native_enum=False), nullable=False)
    item_id = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())