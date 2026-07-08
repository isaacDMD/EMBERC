from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.users import UserOut
from app.services.users_service import get_user_by_identifiant, get_user_by_id
from app.auth.security import verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.permissions import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_identifiant(db, payload.identifiant)
    if not user or not verify_password(payload.mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Identifiant ou mot de passe incorrect")

    token_data = {"sub": str(user.id), "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if decoded is None or decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token invalide")

    user = get_user_by_id(db, int(decoded["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    token_data = {"sub": str(user.id), "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user