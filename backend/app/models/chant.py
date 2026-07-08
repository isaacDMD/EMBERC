from sqlalchemy import TIMESTAMP, Column, Enum, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base
from app.enums.chant_categorie import CategorieChantEnum


class Chants(Base):
    __tablename__ = "chants"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    paroles = Column(Text)
    numero = Column(String(20), nullable=False, unique=True)
    categorie = Column(Enum(CategorieChantEnum, native_enum=False), nullable=False)
    auteur = Column(String(255), nullable=True)
    fichier_audio_url = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())