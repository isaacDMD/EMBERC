from sqlalchemy import Column, Enum, ForeignKey, Integer, String,TIMESTAMP, Boolean
from sqlalchemy.sql import func
from app.database import Base
from app.enums.culte_type import CulteTypeEnum


class ProgrammeCulte(Base):
    __tablename__ = "programme_culte"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    type_culte = Column(Enum(CulteTypeEnum), nullable=False, default=CulteTypeEnum.DIMANCHE)
    predicateur = Column(String(255), nullable=True)
    date_heure = Column(TIMESTAMP, nullable=False)
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=False)
    publie = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())