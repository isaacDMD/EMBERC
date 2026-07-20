import enum

class CategorieChantEnum(enum.Enum):
    """Enum pour les catégories de chants.
        A modifier plus tard pour ajouter d'autres catégories de chants si nécessaire.
    """

    CHANT = "chant"
    CHANT_DE_MESSE = "chant_de_messe"
    CHANT_DE_LA_SAINTETE = "chant_de_la_saintete"
    CHANT_DE_LA_VIE = "chant_de_la_vie"
    CHANT_DE_LA_PAIX = "chant_de_la_paix"
    CHANT_DE_LA_JOIE = "chant_de_la_joie"