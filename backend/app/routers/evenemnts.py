from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.evenements import EvenementCreate, EvenementOut, EvenementUpdate
from app.services import evenements_service
from app.auth.permissions import require_roles
from app.enums.roles import RoleEnum

router = APIRouter(prefix="/api/v1/evenements", tags=["evenements"])


@router.get("", response_model=list[EvenementOut])
def liste_evenements(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    paroisse_id: Optional[int] = Query(None),
    publie: Optional[bool] = Query(None),
    a_venir_seulement: bool = Query(False),
    db: Session = Depends(get_db),
):
    return evenements_service.get_evenements(
        db, page, limit, paroisse_id, publie, a_venir_seulement
    )


@router.get("/{id}", response_model=EvenementOut)
def detail_evenement(id: int, db: Session = Depends(get_db)):
    evenement = evenements_service.get_evenement_by_id(db, id)
    if not evenement:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    return evenement


@router.post("", response_model=EvenementOut, status_code=201)
def creer_evenement(
    payload: EvenementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    try:
        return evenements_service.create_evenement(db, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.put("/{id}", response_model=EvenementOut)
def modifier_evenement(
    id: int,
    payload: EvenementUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    try:
        evenement_updated = evenements_service.update_evenement(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")

    if not evenement_updated:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    return evenement_updated


@router.delete("/{id}", status_code=204)
def supprimer_evenement(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    deleted = evenements_service.delete_evenement(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Événement non trouvé")