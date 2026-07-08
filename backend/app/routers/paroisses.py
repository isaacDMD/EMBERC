from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth.permissions import require_roles
from app.enums.roles import RoleEnum
from app.dependencies import get_db
from app.schemas.paroisses import ParoisseCreate, ParoisseUpdate, ParoisseOut
from app.services import paroisses_service

router = APIRouter(prefix="/api/v1/paroisses", tags=["paroisses"])


@router.get("", response_model=List[ParoisseOut])
def liste_paroisses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return paroisses_service.get_paroisses(db, page, limit)


@router.get("/{paroisse_id}", response_model=ParoisseOut)
def detail_paroisse(paroisse_id: int, db: Session = Depends(get_db)):
    paroisse = paroisses_service.get_paroisse_by_id(db, paroisse_id)
    if not paroisse:
        raise HTTPException(status_code=404, detail="Paroisse introuvable")
    return paroisse


@router.post("", response_model=ParoisseOut, status_code=201)
def creer_paroisse(
    payload: ParoisseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin)),
):
    return paroisses_service.create_paroisse(db, payload)


@router.put("/{paroisse_id}", response_model=ParoisseOut)
def modifier_paroisse(
    paroisse_id: int,
    payload: ParoisseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    paroisse = paroisses_service.get_paroisse_by_id(db, paroisse_id)
    if not paroisse:
        raise HTTPException(status_code=404, detail="Paroisse introuvable")
    return paroisses_service.update_paroisse(db, paroisse, payload)