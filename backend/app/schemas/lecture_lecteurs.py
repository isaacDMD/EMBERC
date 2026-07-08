from datetime import datetime
from pydantic import BaseModel


class LectureLecteurCreate(BaseModel):
    lecteur_id: int
    langue: str = "fr"


class LecteurAssigne(BaseModel):
    """Un lecteur assigné à une lecture, avec ses infos affichables."""
    id: int 
    lecteur_id: int
    langue: str
    nom: str
    prenom: str
    created_at: datetime