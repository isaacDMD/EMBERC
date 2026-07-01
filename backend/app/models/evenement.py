from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String,TIMESTAMP, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
from app.enums.evenement_type import EvenementTypeEnum

class Evenement(Base):
    __tablename__ = "evenements"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=False)
    lieu = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    publie = Column(Boolean, default=False)
    type_evenement = Column(Enum(EvenementTypeEnum), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
