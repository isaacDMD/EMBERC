from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.users import UserCreate, UserOut, UserUpdateRole
from app.services import users_service
from app.auth.permissions import require_roles
from app.enums.roles import RoleEnum
from app.models.user import User

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def liste_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_lecteurs)
    ),
):
    """
    super_admin voit tous les utilisateurs.
    admin_paroisse / resp_lecteurs ne voient QUE les utilisateurs de leur propre paroisse
    (utile pour choisir un lecteur à assigner) — jamais une autre paroisse, jamais paramétrable.
    """
    paroisse_id = None if current_user.role == RoleEnum.super_admin else current_user.paroisse_id
    return users_service.get_users(db, page, limit, paroisse_id)


@router.post("", response_model=UserOut, status_code=201, dependencies=[Depends(require_roles(RoleEnum.super_admin))])
def creer_user(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        return users_service.create_user(db, payload)
    except ValueError as e:
        code = str(e)
        if code == "identifiant_deja_existant":
            raise HTTPException(status_code=409, detail="Cet identifiant est déjà utilisé")
        if code == "email_deja_existant":
            raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")
        raise HTTPException(status_code=409, detail="Identifiant ou email déjà utilisé")


@router.put("/{id}/role", response_model=UserOut, dependencies=[Depends(require_roles(RoleEnum.super_admin))])
def modifier_role(id: int, payload: UserUpdateRole, db: Session = Depends(get_db)):
    user = users_service.update_role(db, id, payload.role)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user