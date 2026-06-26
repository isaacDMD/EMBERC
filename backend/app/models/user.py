from sqlalchemy import Column, Enum, Integer, String, TIMESTAMP
from sqlalchemy.sql import func, ForeignKey
from backend.app.database import Base
from backend.app.enums.roles import RoleEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    mot_de_passe = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default="user")
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=True)
    locale = Column(String(10),default="fr")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())