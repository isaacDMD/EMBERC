from sqlalchemy import Column, Enum, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
from app.enums.roles import RoleEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(150), nullable=False)
    identifiant = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    mot_de_passe = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum, native_enum=False), nullable=False, default=RoleEnum.fidele)
    paroisse_id = Column(Integer, ForeignKey("paroisses.id"), nullable=True)
    locale = Column(String(10), default="fr")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())