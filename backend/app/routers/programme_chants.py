from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.enums.roles import RoleEnum
from app.auth.permissions import require_roles
from app.dependencies import get_db
from app.schemas.programme_chants import (
    ChantDansProgramme,
    ProgrammeChantCreate,
    ProgrammeChantUpdate,
)
from app.services import programme_chants_service, programmes_service

router = APIRouter(prefix="/api/v1/programmes", tags=["programme_chants"])


@router.get("/{programme_id}/chants", response_model=list[ChantDansProgramme])
def liste_chants_du_programme(programme_id: int, db: Session = Depends(get_db)):
    if not programmes_service.get_programme_by_id(db, programme_id):
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    return programme_chants_service.get_chants_by_programme(db, programme_id)


@router.post("/{programme_id}/chants", status_code=201)
def ajouter_chant_au_programme(
    programme_id: int,
    payload: ProgrammeChantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_musical)),
):
    if not programmes_service.get_programme_by_id(db, programme_id):
        raise HTTPException(status_code=404, detail="Programme non trouvé")
    try:
        programme_chants_service.add_chant_to_programme(db, programme_id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Chant invalide")
    return programme_chants_service.get_chants_by_programme(db, programme_id)


@router.put("/{programme_id}/chants/{chant_id}")
def modifier_ordre_chant(
    programme_id: int,
    chant_id: int,
    payload: ProgrammeChantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_musical)),
):
    updated = programme_chants_service.update_ordre(db, programme_id, chant_id, payload.ordre)
    if not updated:
        raise HTTPException(status_code=404, detail="Association non trouvée")
    return programme_chants_service.get_chants_by_programme(db, programme_id)


@router.delete("/{programme_id}/chants/{chant_id}", status_code=204)
def retirer_chant_du_programme(
    programme_id: int,
    chant_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_musical)),
):
    removed = programme_chants_service.remove_chant_from_programme(db, programme_id, chant_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Association non trouvée")