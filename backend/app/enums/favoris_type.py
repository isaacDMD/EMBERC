import enum

class FavorisTypeEnum(enum.Enum):
    """
    Enumeration pour les differents types de favoris 
    """
    ANNONCE = "annonce"
    EVENEMENT = "evenement"
    MEDIA = "media"
    CHANT = "chant"
    ARTICLE = "article"