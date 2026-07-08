from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.auth.jwt import decode_token
from app.services.users_service import get_user_by_id
from app.models.user import User
from app.enums.roles import RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception

    return user


def require_roles(*roles: RoleEnum):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé pour ce rôle",
            )
        return current_user

    return dependency


def verify_paroisse_access(current_user: User, paroisse_id: int) -> None:
    """
    Vérifie que l'utilisateur a le droit de faire ses bails sur cette paroisse.
    Un super_admin passe toujours. Les autres doivent être rattachés
    à cette paroisse précise.
    """
    if current_user.role == RoleEnum.super_admin:
        return

    if current_user.paroisse_id is None or current_user.paroisse_id != paroisse_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à cette paroisse",
        )