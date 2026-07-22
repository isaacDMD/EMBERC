from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.lecture_lecteurs import LecteurAssigne, LectureLecteurCreate
from app.services import lecture_lecteurs_service, lectures_service
from app.auth.permissions import require_roles, verify_paroisse_access
from app.enums.roles import RoleEnum
from app.models.user import User

router = APIRouter(prefix="/api/v1/lectures", tags=["lecture_lecteurs"])


@router.get("/{lecture_id}/lecteurs", response_model=list[LecteurAssigne])
def liste_lecteurs_de_lecture(lecture_id: int, db: Session = Depends(get_db)):
    if not lectures_service.get_lecture_by_id(db, lecture_id):
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    return lecture_lecteurs_service.get_lecteurs_by_lecture(db, lecture_id)


@router.post("/{lecture_id}/lecteurs", status_code=201)
def assigner_lecteur(
    lecture_id: int,
    payload: LectureLecteurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_lecteurs)),
):
    lecture = lectures_service.get_lecture_by_id(db, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    verify_paroisse_access(current_user, lecture.paroisse_id)

    try:
        lecture_lecteurs_service.assign_lecteur(db, lecture_id, payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="Lecteur invalide")
    return lecture_lecteurs_service.get_lecteurs_by_lecture(db, lecture_id)


@router.delete("/{lecture_id}/lecteurs/{assoc_id}", status_code=204)
def retirer_lecteur(
    lecture_id: int,
    assoc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.super_admin, RoleEnum.admin_paroisse, RoleEnum.resp_lecteurs)),
):
    lecture = lectures_service.get_lecture_by_id(db, lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture non trouvée")
    verify_paroisse_access(current_user, lecture.paroisse_id)

    removed = lecture_lecteurs_service.remove_lecteur(db, lecture_id, assoc_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Association non trouvée")