from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String,TIMESTAMP, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
from backend.app.enums.medias_type import MediaTypeEnum

class Medias(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    type_media = Column(Enum(MediaTypeEnum), nullable=False)
    description = Column(Text, nullable=True)
    url_media = Column(String(255), nullable=False)
    thumbnail_url = Column(String(255), nullable=True)
    duree_secondes = Column(Integer, nullable=True)
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=False)
    publie = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())