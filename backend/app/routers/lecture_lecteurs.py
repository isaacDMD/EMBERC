from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.lecture_lecteurs import LecteurAssigne, LectureLecteurCreate
from app.services import lecture_lecteurs_service, lectures_service

router = APIRouter(prefix="/api/v1/lectures", tags=["lecture_lecteurs"])


@router.get("/{lecture_id}/lecteurs", response_model=list[LecteurAssigne])
def liste_lecteurs_de_lecture(lecture_id: int, db: Session = Depends(get_db)):
    if not lectures_service.get_lecture_by_id(db, lecture_id):
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    return lecture_lecteurs_service.get_lecteurs_by_lecture(db, lecture_id)


@router.post("/{lecture_id}/lecteurs", status_code=201)
def assigner_lecteur(
    lecture_id: int, payload: LectureLecteurCreate, db: Session = Depends(get_db)
):
    if not lectures_service.get_lecture_by_id(db, lecture_id):
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    try:
        lecture_lecteurs_service.assign_lecteur(db, lecture_id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Lecteur invalide")
    return lecture_lecteurs_service.get_lecteurs_by_lecture(db, lecture_id)


@router.delete("/{lecture_id}/lecteurs/{assoc_id}", status_code=204)
def retirer_lecteur(lecture_id: int, assoc_id: int, db: Session = Depends(get_db)):
    removed = lecture_lecteurs_service.remove_lecteur(db, lecture_id, assoc_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Association non trouvée")