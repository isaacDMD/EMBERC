from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class LectureLecteurs(Base):
    __tablename__ = "lecture_lecteurs"

    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, ForeignKey("lecture_biblique.id"), nullable=False)
    lecteur_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    langue = Column(String(10), nullable=False, default="fr")  # fr / ewe / en / kab
    created_at = Column(TIMESTAMP, server_default=func.now())