from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String,TIMESTAMP, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
from app.enums.annoce_type import AnnonceTypeEnum

class Annonce(Base):
    __tablename__ = "annonces"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    contenu = Column(Text, nullable=False)
    type_annonce = Column (Enum(AnnonceTypeEnum), nullable=False, default=AnnonceTypeEnum.FUNERAIRE)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=False)
    publie = Column(Boolean, default=False)
    important = Column(Boolean, default=False)
    auteur_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())