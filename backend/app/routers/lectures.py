from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.lectures import (
    LectureBibliqueCreate,
    LectureBibliqueOut,
    LectureBibliqueUpdate,
)
from app.services import lectures_service

router = APIRouter(prefix="/api/v1/lectures", tags=["lectures"])


@router.get("", response_model=list[LectureBibliqueOut])
def liste_lectures(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    paroisse_id: Optional[int] = Query(None),
    programme_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    return lectures_service.get_lectures(db, page, limit, paroisse_id, programme_id)


@router.get("/{id}", response_model=LectureBibliqueOut)
def detail_lecture(id: int, db: Session = Depends(get_db)):
    lecture = lectures_service.get_lecture_by_id(db, id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    return lecture


@router.post("", response_model=LectureBibliqueOut, status_code=201)
def creer_lecture(payload: LectureBibliqueCreate, db: Session = Depends(get_db)):
    try:
        return lectures_service.create_lecture(db, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Programme ou paroisse invalide")


@router.put("/{id}", response_model=LectureBibliqueOut)
def modifier_lecture(
    id: int, payload: LectureBibliqueUpdate, db: Session = Depends(get_db)
):
    try:
        lecture_updated = lectures_service.update_lecture(db, id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Programme ou paroisse invalide")

    if not lecture_updated:
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    return lecture_updated


@router.delete("/{id}", status_code=204)
def supprimer_lecture(id: int, db: Session = Depends(get_db)):
    deleted = lectures_service.delete_lecture(db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lecture non trouvée")