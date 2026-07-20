from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base

class Actualite(Base):
    __tablename__ = "actualites"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    resume = Column(String(500), nullable=True)
    contenu = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=False)
    auteur_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    publie = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())