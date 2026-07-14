from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.medias import (
    MediaCreate, MediaOut, 
    MediaUpdate, MediaUploadRequest, 
    MediaConfirmUploadRequest, MediaUploadResponse, 
    MediaConfirmUploadResponse)
from app.services import medias_service, storage
from app.auth.permissions import require_roles,verify_paroisse_access
from app.enums.roles import RoleEnum
from app.enums.medias_type import MediaTypeEnum

router = APIRouter(prefix="/api/v1/medias", tags=["medias"])

@router.post("/upload-url", response_model=MediaUploadResponse)
def demander_url_upload(
    payload: MediaUploadRequest,
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    verify_paroisse_access(current_user, payload.paroisse_id)

    categorie = payload.type_media.value
    autorises = storage.ALLOWED_CONTENT_TYPES.get(categorie, set())
    if payload.content_type not in autorises:
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé pour cette catégorie")

    key = storage.generate_object_key(f"medias/{categorie}", payload.nom_fichier)
    upload_url = storage.generate_presigned_upload_url(key, payload.content_type, expires_in=1200)

    return MediaUploadResponse(upload_url=upload_url, key=key, expires_in=1200)

@router.post("/confirm-upload", response_model=MediaConfirmUploadResponse)
def confirmer_upload(
    payload: MediaConfirmUploadRequest,
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    taille = storage.get_object_size(payload.key)
    if taille is None:
        raise HTTPException(status_code=400, detail="Fichier non trouvé — l'upload a-t-il abouti ?")

    categorie = payload.type_media.value
    limite = storage.MAX_SIZE_BYTES.get(categorie)
    if limite and taille > limite:
        storage.delete_object(payload.key)
        raise HTTPException(status_code=400, detail=f"Fichier trop volumineux (max {limite // (1024*1024)} Mo)")

    url_finale = storage.build_public_url(payload.key)
    return MediaConfirmUploadResponse(url_media=url_finale, taille_octets=taille)

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
    verify_paroisse_access(current_user, payload.paroisse_id)
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
    existant = medias_service.get_media_by_id(db, id)
    if not existant:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    verify_paroisse_access(current_user, existant.paroisse_id)

    try:
        return medias_service.update_media(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Paroisse invalide")


@router.delete("/{id}", status_code=204)
def supprimer_media(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse)),
):
    existant = medias_service.get_media_by_id(db, id)
    if not existant:
        raise HTTPException(status_code=404, detail="Média non trouvé")
    verify_paroisse_access(current_user, existant.paroisse_id)

    medias_service.delete_media(db, id)