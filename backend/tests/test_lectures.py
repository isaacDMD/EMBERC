from datetime import datetime, timedelta
from app.enums.roles import RoleEnum
from tests.conftest import _login


def _creer_programme(client, headers, paroisse_id):
    return client.post(
        "/api/v1/programmes",
        json={
            "titre": "Culte pour lecture",
            "date_heure": (datetime.now() + timedelta(days=5)).isoformat(),
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def _creer_lecture(client, headers, programme_id, paroisse_id, reference="Jean 3:16"):
    return client.post(
        "/api/v1/lectures",
        json={
            "reference": reference,
            "texte": "Car Dieu a tant aimé le monde...",
            "date_lecture": (datetime.now() + timedelta(days=5)).isoformat(),
            "programme_id": programme_id,
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def test_creer_lecture_admin_paroisse(client, admin_paroisse_headers, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id)
    assert response.status_code == 201
    assert response.json()["reference"] == "Jean 3:16"


def test_creer_lecture_resp_lecteurs(client, admin_paroisse_headers, make_user, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    make_user(
        identifiant="resp_lecteurs_test",
        role=RoleEnum.resp_lecteurs,
        paroisse_id=paroisse.id,
        mot_de_passe="motdepasse123",
    )
    token = _login(client, "resp_lecteurs_test", "motdepasse123")

    response = _creer_lecture(
        client, {"Authorization": f"Bearer {token}"}, programme_id, paroisse.id
    )
    assert response.status_code == 201


def test_creer_lecture_refuse_resp_musical(client, admin_paroisse_headers, make_user, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    make_user(
        identifiant="resp_musical_lecture",
        role=RoleEnum.resp_musical,
        paroisse_id=paroisse.id,
        mot_de_passe="motdepasse123",
    )
    token = _login(client, "resp_musical_lecture", "motdepasse123")

    response = _creer_lecture(
        client, {"Authorization": f"Bearer {token}"}, programme_id, paroisse.id
    )
    assert response.status_code == 403


def test_creer_lecture_refuse_autre_paroisse(client, admin_paroisse_headers, super_admin_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Autre Paroisse Lecture", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    programme_id = _creer_programme(client, super_admin_headers, autre.id).json()["id"]

    response = _creer_lecture(client, admin_paroisse_headers, programme_id, autre.id)
    assert response.status_code == 403


def test_creer_lecture_programme_invalide(client, admin_paroisse_headers, paroisse):
    response = _creer_lecture(client, admin_paroisse_headers, 999999, paroisse.id)
    assert response.status_code == 400


def test_liste_lectures_filtre_programme(client, admin_paroisse_headers, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id, reference="Psaume 23")

    response = client.get(f"/api/v1/lectures?programme_id={programme_id}")
    assert response.status_code == 200
    assert any(l["reference"] == "Psaume 23" for l in response.json())


def test_detail_lecture_inexistante(client):
    response = client.get("/api/v1/lectures/999999")
    assert response.status_code == 404


def test_modifier_lecture_sa_paroisse(client, admin_paroisse_headers, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]

    response = client.put(
        f"/api/v1/lectures/{lecture_id}",
        json={"reference": "Jean 3:17"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 200
    assert response.json()["reference"] == "Jean 3:17"


def test_modifier_lecture_refuse_autre_paroisse(client, admin_paroisse_headers, super_admin_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Paroisse C", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    programme_id = _creer_programme(client, super_admin_headers, autre.id).json()["id"]
    lecture_id = _creer_lecture(client, super_admin_headers, programme_id, autre.id).json()["id"]

    response = client.put(
        f"/api/v1/lectures/{lecture_id}",
        json={"reference": "Interdit"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403


def test_supprimer_lecture(client, admin_paroisse_headers, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]

    response = client.delete(f"/api/v1/lectures/{lecture_id}", headers=admin_paroisse_headers)
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/lectures/{lecture_id}")
    assert get_resp.status_code == 404