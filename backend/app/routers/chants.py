from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.chants import (
    ChantCreate, ChantOut, ChantUpdate,
    ChantUploadRequest, ChantUploadResponse,
    ChantConfirmUploadRequest, ChantConfirmUploadResponse,
)
from app.services import chants_service, storage
from app.auth.permissions import require_roles
from app.enums.roles import RoleEnum

router = APIRouter(prefix="/api/v1/chants", tags=["chants"])


@router.post("/upload-url", response_model=ChantUploadResponse)
def demander_url_upload_chant(
    payload: ChantUploadRequest,
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_musical)),
):
    autorises = storage.ALLOWED_CONTENT_TYPES.get("audio", set())
    if payload.content_type not in autorises:
        raise HTTPException(status_code=400, detail="Type de fichier non autorisé pour un chant")

    key = storage.generate_object_key("chants/audio", payload.nom_fichier)
    limite = storage.MAX_SIZE_BYTES.get("audio")
    presigned = storage.generate_presigned_post(key, payload.content_type, limite, expires_in=1200)

    return ChantUploadResponse(
        upload_url=presigned["url"],
        key=key,
        fields=presigned["fields"],
        expires_in=1200,
    )


@router.post("/confirm-upload", response_model=ChantConfirmUploadResponse)
def confirmer_upload_chant(
    payload: ChantConfirmUploadRequest,
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_musical)),
):
    taille = storage.get_object_size(payload.key)
    if taille is None:
        raise HTTPException(status_code=400, detail="Fichier non trouvé — l'upload a-t-il abouti ?")

    limite = storage.MAX_SIZE_BYTES.get("audio")
    if limite and taille > limite:
        storage.delete_object(payload.key)
        raise HTTPException(status_code=400, detail=f"Fichier trop volumineux (max {limite // (1024*1024)} Mo)")

    url_finale = storage.build_public_url(payload.key)
    return ChantConfirmUploadResponse(fichier_audio_url=url_finale, taille_octets=taille)


@router.get("", response_model=list[ChantOut])
def get_chants(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return chants_service.get_chants(db, page, limit)


@router.get("/{id}", response_model=ChantOut)
def get_chant_by_id(id: int, db: Session = Depends(get_db)):
    chant = chants_service.get_chant_by_id(db, id)
    if not chant:
        raise HTTPException(status_code=404, detail="Chant non trouvé")
    return chant


@router.post("", response_model=ChantOut, status_code=201)
def create_chant(
    payload: ChantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_musical)),
):
    try:
        return chants_service.create_chant(db, payload)
    except ValueError:
        raise HTTPException(status_code=409, detail="Ce numéro de chant existe déjà")


@router.put("/{id}", response_model=ChantOut)
def update_chant(
    id: int,
    payload: ChantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_musical)),
):
    try:
        chant_updated = chants_service.update_chant(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=409, detail="Ce numéro de chant existe déjà")

    if not chant_updated:
        raise HTTPException(status_code=404, detail="Le chant que vous essayez de modifier n'existe pas")
    return chant_updated