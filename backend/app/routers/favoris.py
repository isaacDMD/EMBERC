from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.favoris import FavorisCreate, FavorisOut
from app.services import favoris_service
from app.auth.permissions import get_current_user
from app.models.user import User
from app.enums.favoris_type import FavorisTypeEnum

router = APIRouter(prefix="/api/v1/favoris", tags=["favoris"])


@router.get("", response_model=list[FavorisOut])
def liste_favoris(
    type_favoris: Optional[FavorisTypeEnum] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return favoris_service.get_favoris_by_user(db, current_user.id, type_favoris)


@router.post("", response_model=FavorisOut, status_code=201)
def ajouter_favori(
    payload: FavorisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return favoris_service.add_favori(db, current_user.id, payload)
    except ValueError:
        raise HTTPException(status_code=409, detail="Ce favori existe déjà")


@router.delete("/{id}", status_code=204)
def retirer_favori(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    removed = favoris_service.remove_favori(db, current_user.id, id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favori non trouvé")