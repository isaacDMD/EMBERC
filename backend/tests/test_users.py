from app.enums.roles import RoleEnum
from tests.conftest import _login


def test_creer_user_super_admin(client, super_admin_headers):
    response = client.post(
        "/api/v1/users",
        json={
            "nom": "Kodjo",
            "prenom": "Ama",
            "identifiant": "ama_kodjo",
            "mot_de_passe": "motdepasse123",
        },
        headers=super_admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["identifiant"] == "ama_kodjo"
    assert data["role"] == "fidele"  # rôle par défaut


def test_creer_user_refuse_sans_token(client):
    response = client.post(
        "/api/v1/users",
        json={"nom": "X", "prenom": "Y", "identifiant": "xy", "mot_de_passe": "test1234"},
    )
    assert response.status_code == 401


def test_creer_user_refuse_admin_paroisse(client, admin_paroisse_headers):
    """Seul le super_admin gère les utilisateurs, pas admin_paroisse."""
    response = client.post(
        "/api/v1/users",
        json={"nom": "X", "prenom": "Y", "identifiant": "xy2", "mot_de_passe": "test1234"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403


def test_creer_user_identifiant_duplique(client, super_admin_headers, make_user):
    make_user(identifiant="deja_pris")

    response = client.post(
        "/api/v1/users",
        json={
            "nom": "Autre",
            "prenom": "Personne",
            "identifiant": "deja_pris",
            "mot_de_passe": "motdepasse123",
        },
        headers=super_admin_headers,
    )
    assert response.status_code == 409


def test_liste_users_super_admin(client, super_admin_headers, make_user):
    make_user(identifiant="user_liste_1")
    make_user(identifiant="user_liste_2")

    response = client.get("/api/v1/users", headers=super_admin_headers)
    assert response.status_code == 200
    identifiants = [u["identifiant"] for u in response.json()]
    assert "user_liste_1" in identifiants
    assert "user_liste_2" in identifiants


def test_liste_users_refuse_fidele(client, make_user):
    make_user(identifiant="fidele_users", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    token = _login(client, "fidele_users", "motdepasse123")

    response = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_modifier_role_super_admin(client, super_admin_headers, make_user):
    user = make_user(identifiant="futur_admin", role=RoleEnum.fidele)

    response = client.put(
        f"/api/v1/users/{user.id}/role",
        json={"role": "admin_paroisse"},
        headers=super_admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin_paroisse"


def test_modifier_role_utilisateur_inexistant(client, super_admin_headers):
    response = client.put(
        "/api/v1/users/999999/role",
        json={"role": "admin_paroisse"},
        headers=super_admin_headers,
    )
    assert response.status_code == 404


def test_modifier_role_refuse_admin_paroisse(client, admin_paroisse_headers, make_user):
    user = make_user(identifiant="cible_role")

    response = client.put(
        f"/api/v1/users/{user.id}/role",
        json={"role": "resp_musical"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403