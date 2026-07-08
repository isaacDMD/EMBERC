from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth.permissions import require_roles
from app.enums.roles import RoleEnum
from app.dependencies import get_db
from app.schemas.programmes import (
    ProgrammeCulteCreate,
    ProgrammeCulteOut,
    ProgrammeCulteUpdate,
)
from app.services import programmes_service

router = APIRouter(prefix="/api/v1/programmes", tags=["programmes"])


@router.get("", response_model=list[ProgrammeCulteOut])
def liste_programmes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    paroisse_id: Optional[int] = Query(None),
    publie: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    return programmes_service.get_programmes(db, page, limit, paroisse_id, publie)


@router.get("/{id}", response_model=ProgrammeCulteOut)
def detail_programme(id: int, db: Session = Depends(get_db)):
    programme = programmes_service.get_programme_by_id(db, id)
    if not programme:
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    return programme


@router.post("", response_model=ProgrammeCulteOut, status_code=201)
def creer_programme(
    payload: ProgrammeCulteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    try:
        return programmes_service.create_programme(db, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.put("/{id}", response_model=ProgrammeCulteOut)
def modifier_programme(
    id: int,
    payload: ProgrammeCulteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    try:
        programme_updated = programmes_service.update_programme(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")

    if not programme_updated:
        raise HTTPException(status_code=404, detail="Le programme que vous essayez de modifier n'existe pas")
    return programme_updated


@router.delete("/{id}", status_code=204)
def supprimer_programme(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    deleted = programmes_service.delete_programme(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Programme non trouvé")