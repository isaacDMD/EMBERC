from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.actualites import ActualiteCreate, ActualiteOut, ActualiteUpdate
from app.services import actualites_service
from app.auth.permissions import require_roles, verify_paroisse_access
from app.enums.roles import RoleEnum
from app.models.user import User

router = APIRouter(prefix="/api/v1/actualites", tags=["actualites"])


@router.get("", response_model=list[ActualiteOut])
def liste_actualites(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    paroisse_id: Optional[int] = Query(None),
    publie: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    return actualites_service.get_actualites(db, page, limit, paroisse_id, publie)


@router.get("/{id}", response_model=ActualiteOut)
def detail_actualite(id: int, db: Session = Depends(get_db)):
    actualite = actualites_service.get_actualite_by_id(db, id)
    if not actualite:
        raise HTTPException(status_code=404, detail="Actualité non trouvée")
    return actualite


@router.post("", response_model=ActualiteOut, status_code=201)
def creer_actualite(
    payload: ActualiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    verify_paroisse_access(current_user, payload.paroisse_id)
    try:
        return actualites_service.create_actualite(db, payload, auteur_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.put("/{id}", response_model=ActualiteOut)
def modifier_actualite(
    id: int,
    payload: ActualiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    existant = actualites_service.get_actualite_by_id(db, id)
    if not existant:
        raise HTTPException(status_code=404, detail="Actualité non trouvée")
    verify_paroisse_access(current_user, existant.paroisse_id)
    if payload.paroisse_id is not None:
        verify_paroisse_access(current_user, payload.paroisse_id)

    try:
        return actualites_service.update_actualite(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.delete("/{id}", status_code=204)
def supprimer_actualite(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    existant = actualites_service.get_actualite_by_id(db, id)
    if not existant:
        raise HTTPException(status_code=404, detail="Actualité non trouvée")
    verify_paroisse_access(current_user, existant.paroisse_id)

    actualites_service.delete_actualite(db, id)