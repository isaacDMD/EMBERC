from app.enums.roles import RoleEnum


def test_login_succes(client, make_user):
    make_user(identifiant="jean_dupont", mot_de_passe="secret123")

    response = client.post(
        "/api/v1/auth/login",
        json={"identifiant": "jean_dupont", "mot_de_passe": "secret123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_mauvais_mot_de_passe(client, make_user):
    make_user(identifiant="jean_dupont", mot_de_passe="secret123")

    response = client.post(
        "/api/v1/auth/login",
        json={"identifiant": "jean_dupont", "mot_de_passe": "mauvais"},
    )

    assert response.status_code == 401


def test_login_identifiant_inconnu(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"identifiant": "inconnu", "mot_de_passe": "peu_importe"},
    )

    assert response.status_code == 401


def test_refresh_token_valide(client, make_user):
    make_user(identifiant="jean_dupont", mot_de_passe="secret123")
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"identifiant": "jean_dupont", "mot_de_passe": "secret123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_invalide(client):
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "token.invalide.ici"})
    assert response.status_code == 401


def test_refresh_avec_access_token_refuse(client, make_user):
    """Un access_token ne doit pas être accepté comme refresh_token (champ `type` distinct)."""
    make_user(identifiant="jean_dupont", mot_de_passe="secret123")
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"identifiant": "jean_dupont", "mot_de_passe": "secret123"},
    )
    access_token = login_resp.json()["access_token"]

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401


def test_me_sans_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_avec_token_valide(client, make_user):
    make_user(identifiant="jean_dupont", mot_de_passe="secret123", role=RoleEnum.fidele)
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"identifiant": "jean_dupont", "mot_de_passe": "secret123"},
    )
    token = login_resp.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["identifiant"] == "jean_dupont"
    assert data["role"] == "fidele"