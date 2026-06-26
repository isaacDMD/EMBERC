from sqlalchemy import TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.sql import func
from app.database import Base

class Paroisse(Base):
    __tablename__ = "paroisses"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    adresse = Column(Text)
    ville = Column(String(100))
    telephone = Column(String(20))
    email = Column(String(100))
    pasteur_nom = Column(String(100))
    description = Column(Text)
    logo_url = Column(String(255))
    actif = Column(bool, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
