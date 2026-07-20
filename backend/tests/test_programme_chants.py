from datetime import datetime, timedelta
from app.enums.roles import RoleEnum
from tests.conftest import _login


def _creer_programme(client, headers, paroisse_id, titre="Culte test"):
    return client.post(
        "/api/v1/programmes",
        json={
            "titre": titre,
            "date_heure": (datetime.now() + timedelta(days=3)).isoformat(),
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def _creer_chant(client, headers, numero):
    return client.post(
        "/api/v1/chants",
        json={"numero": numero, "titre": "Chant test", "categorie": "chant"},
        headers=headers,
    )


def test_ajouter_chant_au_programme(client, admin_paroisse_headers, resp_musical_token, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    resp_musical_headers = {"Authorization": f"Bearer {resp_musical_token}"}
    chant_id = _creer_chant(client, resp_musical_headers, "PC-001").json()["id"]

    response = client.post(
        f"/api/v1/programmes/{programme_id}/chants",
        json={"chant_id": chant_id, "ordre": 1},
        headers=resp_musical_headers,
    )
    assert response.status_code == 201
    chants = response.json()
    assert len(chants) == 1
    assert chants[0]["chant_id"] == chant_id
    assert chants[0]["ordre"] == 1


def test_liste_chants_programme_publique(client, admin_paroisse_headers, resp_musical_token, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    resp_musical_headers = {"Authorization": f"Bearer {resp_musical_token}"}
    chant_id = _creer_chant(client, resp_musical_headers, "PC-002").json()["id"]
    client.post(
        f"/api/v1/programmes/{programme_id}/chants",
        json={"chant_id": chant_id, "ordre": 1},
        headers=resp_musical_headers,
    )

    response = client.get(f"/api/v1/programmes/{programme_id}/chants")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_ajouter_chant_programme_inexistant(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    chant_id = _creer_chant(client, headers, "PC-003").json()["id"]

    response = client.post(
        "/api/v1/programmes/999999/chants",
        json={"chant_id": chant_id, "ordre": 1},
        headers=headers,
    )
    assert response.status_code == 404


def test_ajouter_chant_inexistant_au_programme(client, admin_paroisse_headers, resp_musical_token, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    headers = {"Authorization": f"Bearer {resp_musical_token}"}

    response = client.post(
        f"/api/v1/programmes/{programme_id}/chants",
        json={"chant_id": 999999, "ordre": 1},
        headers=headers,
    )
    assert response.status_code == 400


def test_modifier_ordre_chant(client, admin_paroisse_headers, resp_musical_token, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    chant_id = _creer_chant(client, headers, "PC-004").json()["id"]
    client.post(
        f"/api/v1/programmes/{programme_id}/chants",
        json={"chant_id": chant_id, "ordre": 1},
        headers=headers,
    )

    response = client.put(
        f"/api/v1/programmes/{programme_id}/chants/{chant_id}",
        json={"ordre": 5},
        headers=headers,
    )
    assert response.status_code == 200
    chants = response.json()
    assert chants[0]["ordre"] == 5


def test_modifier_ordre_association_inexistante(client, admin_paroisse_headers, resp_musical_token, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    chant_id = _creer_chant(client, headers, "PC-005").json()["id"]

    response = client.put(
        f"/api/v1/programmes/{programme_id}/chants/{chant_id}",
        json={"ordre": 1},
        headers=headers,
    )
    assert response.status_code == 404


def test_retirer_chant_du_programme(client, admin_paroisse_headers, resp_musical_token, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    chant_id = _creer_chant(client, headers, "PC-006").json()["id"]
    client.post(
        f"/api/v1/programmes/{programme_id}/chants",
        json={"chant_id": chant_id, "ordre": 1},
        headers=headers,
    )

    response = client.delete(
        f"/api/v1/programmes/{programme_id}/chants/{chant_id}", headers=headers
    )
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/programmes/{programme_id}/chants")
    assert get_resp.json() == []


def test_retirer_chant_refuse_fidele(client, admin_paroisse_headers, resp_musical_token, make_user, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    resp_musical_headers = {"Authorization": f"Bearer {resp_musical_token}"}
    chant_id = _creer_chant(client, resp_musical_headers, "PC-007").json()["id"]
    client.post(
        f"/api/v1/programmes/{programme_id}/chants",
        json={"chant_id": chant_id, "ordre": 1},
        headers=resp_musical_headers,
    )

    make_user(identifiant="fidele_pc", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    fidele_token = _login(client, "fidele_pc", "motdepasse123")

    response = client.delete(
        f"/api/v1/programmes/{programme_id}/chants/{chant_id}",
        headers={"Authorization": f"Bearer {fidele_token}"},
    )
    assert response.status_code == 403