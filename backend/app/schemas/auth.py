from pydantic import BaseModel


class LoginRequest(BaseModel):
    identifiant: str
    mot_de_passe: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str