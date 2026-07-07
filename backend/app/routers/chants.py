from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.chants import ChantCreate, ChantOut, ChantUpdate
from app.services import chants_service

router = APIRouter(prefix="/api/v1/chants", tags=["chants"])


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
def create_chant(payload: ChantCreate, db: Session = Depends(get_db)):
    try:
        return chants_service.create_chant(db, payload)
    except ValueError:
        raise HTTPException(status_code=409, detail="Ce numéro de chant existe déjà")


@router.put("/{id}", response_model=ChantOut)
def update_chant(id: int, payload: ChantUpdate, db: Session = Depends(get_db)):
    try:
        chant_updated = chants_service.update_chant(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=409, detail="Ce numéro de chant existe déjà")

    if not chant_updated:
        raise HTTPException(status_code=404, detail="Le chant que vous essayez de modifier n'existe pas")
    return chant_updated