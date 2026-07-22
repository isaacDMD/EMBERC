import enum

class AnnonceType(enum.Enum):
    """
    Enumeration pour les differents types d'annonces 
    """
    MARRIAGE = "mariage"
    FUNERAIRE = "funeraire"
    BAPTEME = "bapteme"
    CONFIRMATION = "confirmation"
    REUNION = "reunion"
    ASSEMBLEE = "assemblée_générale"