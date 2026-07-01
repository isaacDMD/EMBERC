import enum

class CulteTypeEnum(enum.Enum):
    """
    Tous les types de cultes .
    """
    ACTION_DE_GRACE = "Messe d'action de grâce"
    DIMANCHE = "Messe du dimanche"
    MERCREDI = "Prière de bénédiction"
    VENDREDI = "Prière de délivrance"
    ANIVERSAIRE = "Messe d'anniversaire"
    PAQUES = "Pâques"
    PENTECOTE = "Pentecôte"
    NOEL = "Noël"
    REVEILLON = "Nouvel An"
    REVEILLON_DE_NOEL = "Veille de Noël"