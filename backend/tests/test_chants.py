from app.enums.roles import RoleEnum
from tests.conftest import _login


def _creer_chant(client, headers, numero="CH-001", titre="Amazing Grace"):
    return client.post(
        "/api/v1/chants",
        json={"numero": numero, "titre": titre, "categorie": "chant"},
        headers=headers,
    )


def test_liste_chants_publique(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    _creer_chant(client, headers, numero="CH-100", titre="Chant public")

    response = client.get("/api/v1/chants")
    assert response.status_code == 200
    assert any(c["numero"] == "CH-100" for c in response.json())


def test_creer_chant_resp_musical(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    response = _creer_chant(client, headers, numero="CH-200")

    assert response.status_code == 201
    assert response.json()["numero"] == "CH-200"


def test_creer_chant_refuse_fidele(client, make_user):
    make_user(identifiant="fidele_chant", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    token = _login(client, "fidele_chant", "motdepasse123")

    response = _creer_chant(
        client, {"Authorization": f"Bearer {token}"}, numero="CH-300"
    )
    assert response.status_code == 403


def test_creer_chant_numero_duplique(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    _creer_chant(client, headers, numero="CH-400")

    response = _creer_chant(client, headers, numero="CH-400", titre="Autre titre")
    assert response.status_code == 409


def test_detail_chant_inexistant(client):
    response = client.get("/api/v1/chants/999999")
    assert response.status_code == 404


def test_modifier_chant(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    creer_resp = _creer_chant(client, headers, numero="CH-500")
    chant_id = creer_resp.json()["id"]

    response = client.put(
        f"/api/v1/chants/{chant_id}",
        json={"titre": "Titre modifié"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["titre"] == "Titre modifié"


def test_modifier_chant_inexistant(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    response = client.put(
        "/api/v1/chants/999999",
        json={"titre": "Peu importe"},
        headers=headers,
    )
    assert response.status_code == 404