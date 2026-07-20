from datetime import date, timedelta
from app.enums.roles import RoleEnum
from tests.conftest import _login


def _creer_evenement(client, headers, paroisse_id, titre="Conférence annuelle", date_debut=None, date_fin=None):
    return client.post(
        "/api/v1/evenements",
        json={
            "titre": titre,
            "description": "Un bel événement",
            "date_debut": str(date_debut or (date.today() + timedelta(days=10))),
            "date_fin": str(date_fin or (date.today() + timedelta(days=12))),
            "paroisse_id": paroisse_id,
            "lieu": "Salle principale",
        },
        headers=headers,
    )


def test_creer_evenement_admin_paroisse(client, admin_paroisse_headers, paroisse):
    response = _creer_evenement(client, admin_paroisse_headers, paroisse.id)
    assert response.status_code == 201
    assert response.json()["titre"] == "Conférence annuelle"


def test_creer_evenement_refuse_autre_paroisse(client, admin_paroisse_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Autre Paroisse Evt", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    response = _creer_evenement(client, admin_paroisse_headers, autre.id)
    assert response.status_code == 403


def test_creer_evenement_refuse_fidele(client, make_user, paroisse):
    make_user(identifiant="fidele_evt", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    token = _login(client, "fidele_evt", "motdepasse123")

    response = _creer_evenement(client, {"Authorization": f"Bearer {token}"}, paroisse.id)
    assert response.status_code == 403


def test_liste_evenements_a_venir_seulement(client, admin_paroisse_headers, paroisse):
    _creer_evenement(
        client, admin_paroisse_headers, paroisse.id,
        titre="Événement passé",
        date_debut=date.today() - timedelta(days=20),
        date_fin=date.today() - timedelta(days=18),
    )
    _creer_evenement(client, admin_paroisse_headers, paroisse.id, titre="Événement futur")

    response = client.get(f"/api/v1/evenements?a_venir_seulement=true&paroisse_id={paroisse.id}")
    titres = [e["titre"] for e in response.json()]
    assert "Événement futur" in titres
    assert "Événement passé" not in titres


def test_detail_evenement_inexistant(client):
    response = client.get("/api/v1/evenements/999999")
    assert response.status_code == 404


def test_modifier_evenement_sa_paroisse(client, admin_paroisse_headers, paroisse):
    evenement_id = _creer_evenement(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.put(
        f"/api/v1/evenements/{evenement_id}",
        json={"lieu": "Nouvelle salle"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 200
    assert response.json()["lieu"] == "Nouvelle salle"


def test_supprimer_evenement(client, admin_paroisse_headers, paroisse):
    evenement_id = _creer_evenement(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.delete(f"/api/v1/evenements/{evenement_id}", headers=admin_paroisse_headers)
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/evenements/{evenement_id}")
    assert get_resp.status_code == 404