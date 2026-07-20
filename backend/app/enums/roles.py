import enum

class RoleEnum(enum.Enum):
    super_admin = "super_admin"
    admin_paroisse = "admin_paroisse"
    resp_musical = "resp_musical"
    resp_lecteurs = "resp_lecteurs"
    fidele = "fidele"