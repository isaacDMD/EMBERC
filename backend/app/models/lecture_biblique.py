from sqlalchemy import Column, Integer, String,TIMESTAMP, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class LectureBiblique(Base):
    __tablename__ = "lecture_biblique"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(100), nullable=False)
    texte = Column(Text)
    date_lecture = Column(TIMESTAMP, nullable=False)
    type_evenement = Column(String(100))
    programme_id = Column(Integer, ForeignKey("programme_culte.id"), nullable=False)
    lecteur_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
