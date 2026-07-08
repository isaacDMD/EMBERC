from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.users import UserCreate
from app.auth.security import hash_password


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        nom=payload.nom,
        prenom=payload.prenom,
        identifiant=payload.identifiant,
        email=payload.email,
        mot_de_passe=hash_password(payload.mot_de_passe),
        role=payload.role,
        paroisse_id=payload.paroisse_id,
        locale=payload.locale,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("identifiant_ou_email_deja_existant")
    db.refresh(user)
    return user


def get_user_by_identifiant(db: Session, identifiant: str) -> Optional[User]:
    return db.scalars(select(User).where(User.identifiant == identifiant)).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.scalars(select(User).where(User.id == user_id)).first()


def get_users(db: Session, page: int = 1, limit: int = 20) -> list[User]:
    return db.scalars(
        select(User).offset((page - 1) * limit).limit(limit)
    ).all()


def update_role(db: Session, user_id: int, new_role) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user