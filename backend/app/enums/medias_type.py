import enum

class MediaTypeEnum(enum.Enum):
    """
    Enumeration pour les differents types de medias 
    """
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"