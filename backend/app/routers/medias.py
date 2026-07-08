from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.medias import MediaCreate, MediaOut, MediaUpdate
from app.services import medias_service
from app.auth.permissions import require_roles
from app.enums.roles import RoleEnum
from app.enums.medias_type import MediaTypeEnum

router = APIRouter(prefix="/api/v1/medias", tags=["medias"])


@router.get("", response_model=list[MediaOut])
def liste_medias(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    paroisse_id: Optional[int] = Query(None),
    publie: Optional[bool] = Query(None),
    type_media: Optional[MediaTypeEnum] = Query(None),
    db: Session = Depends(get_db),
):
    return medias_service.get_medias(db, page, limit, paroisse_id, publie, type_media)


@router.get("/{id}", response_model=MediaOut)
def detail_media(id: int, db: Session = Depends(get_db)):
    media = medias_service.get_media_by_id(db, id)
    if not media:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    return media


@router.post("", response_model=MediaOut, status_code=201)
def creer_media(
    payload: MediaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    try:
        return medias_service.create_media(db, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.put("/{id}", response_model=MediaOut)
def modifier_media(
    id: int,
    payload: MediaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    try:
        media_updated = medias_service.update_media(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")

    if not media_updated:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    return media_updated


@router.delete("/{id}", status_code=204)
def supprimer_media(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    deleted = medias_service.delete_media(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Média non trouvé")