from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.annonces import AnnonceCreate, AnnonceOut, AnnonceUpdate
from app.services import annonces_service
from app.auth.permissions import require_roles, get_current_user, verify_paroisse_access
from app.enums.roles import RoleEnum
from app.models.user import User

router = APIRouter(prefix="/api/v1/annonces", tags=["annonces"])


@router.get("", response_model=list[AnnonceOut])
def liste_annonces(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    paroisse_id: Optional[int] = Query(None),
    publie: Optional[bool] = Query(None),
    actives_seulement: bool = Query(False),
    db: Session = Depends(get_db),
):
    return annonces_service.get_annonces(
        db, page, limit, paroisse_id, publie, actives_seulement
    )


@router.get("/{id}", response_model=AnnonceOut)
def detail_annonce(id: int, db: Session = Depends(get_db)):
    annonce = annonces_service.get_annonce_by_id(db, id)
    if not annonce:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    return annonce


@router.post("", response_model=AnnonceOut, status_code=201)
def creer_annonce(
    payload: AnnonceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    verify_paroisse_access(current_user, payload.paroisse_id)
    try:
        return annonces_service.create_annonce(db, payload, auteur_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.put("/{id}", response_model=AnnonceOut)
def modifier_annonce(
    id: int,
    payload: AnnonceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    existant = annonces_service.get_annonce_by_id(db, id)
    if not existant:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    verify_paroisse_access(current_user, existant.paroisse_id)

    try:
        return annonces_service.update_annonce(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.delete("/{id}", status_code=204)
def supprimer_annonce(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    existant = annonces_service.get_annonce_by_id(db, id)
    if not existant:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")
    verify_paroisse_access(current_user, existant.paroisse_id)

    annonces_service.delete_annonce(db, id)