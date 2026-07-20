from datetime import datetime, timedelta
from app.enums.roles import RoleEnum
from tests.conftest import _login


def _date_heure_future():
    return (datetime.now() + timedelta(days=7)).isoformat()


def _creer_programme(client, headers, paroisse_id, titre="Culte du dimanche"):
    return client.post(
        "/api/v1/programmes",
        json={
            "titre": titre,
            "type_culte": "Messe du dimanche",
            "predicateur": "Pasteur Jean",
            "date_heure": _date_heure_future(),
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def test_liste_programmes_publique(client, admin_paroisse_headers, paroisse):
    _creer_programme(client, admin_paroisse_headers, paroisse.id, titre="Programme visible")

    response = client.get("/api/v1/programmes")
    assert response.status_code == 200
    assert any(p["titre"] == "Programme visible" for p in response.json())


def test_liste_programmes_filtre_paroisse(client, admin_paroisse_headers, paroisse, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Autre", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    _creer_programme(client, admin_paroisse_headers, paroisse.id, titre="Programme A")

    response = client.get(f"/api/v1/programmes?paroisse_id={autre.id}")
    assert response.status_code == 200
    assert all(p["titre"] != "Programme A" for p in response.json())


def test_creer_programme_admin_paroisse(client, admin_paroisse_headers, paroisse):
    response = _creer_programme(client, admin_paroisse_headers, paroisse.id)
    assert response.status_code == 201
    assert response.json()["publie"] is False


def test_creer_programme_refuse_autre_paroisse(client, admin_paroisse_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Autre Paroisse", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    response = _creer_programme(client, admin_paroisse_headers, autre.id)
    assert response.status_code == 403


def test_creer_programme_refuse_resp_musical(client, make_user, paroisse):
    make_user(
        identifiant="resp_musical_prog",
        role=RoleEnum.resp_musical,
        paroisse_id=paroisse.id,
        mot_de_passe="motdepasse123",
    )
    token = _login(client, "resp_musical_prog", "motdepasse123")

    response = _creer_programme(client, {"Authorization": f"Bearer {token}"}, paroisse.id)
    assert response.status_code == 403


def test_detail_programme_inexistant(client):
    response = client.get("/api/v1/programmes/999999")
    assert response.status_code == 404


def test_modifier_programme_sa_paroisse(client, admin_paroisse_headers, paroisse):
    creer_resp = _creer_programme(client, admin_paroisse_headers, paroisse.id)
    programme_id = creer_resp.json()["id"]

    response = client.put(
        f"/api/v1/programmes/{programme_id}",
        json={"publie": True},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 200
    assert response.json()["publie"] is True


def test_modifier_programme_refuse_autre_paroisse(client, admin_paroisse_headers, super_admin_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Paroisse B", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    # Le super_admin crée le programme pour l'autre paroisse
    creer_resp = _creer_programme(client, super_admin_headers, autre.id)
    programme_id = creer_resp.json()["id"]

    # L'admin_paroisse (d'une paroisse différente) tente de le modifier
    response = client.put(
        f"/api/v1/programmes/{programme_id}",
        json={"publie": True},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403


def test_supprimer_programme(client, admin_paroisse_headers, paroisse):
    creer_resp = _creer_programme(client, admin_paroisse_headers, paroisse.id)
    programme_id = creer_resp.json()["id"]

    response = client.delete(
        f"/api/v1/programmes/{programme_id}", headers=admin_paroisse_headers
    )
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/programmes/{programme_id}")
    assert get_resp.status_code == 404


def test_supprimer_programme_inexistant(client, admin_paroisse_headers):
    response = client.delete("/api/v1/programmes/999999", headers=admin_paroisse_headers)
    assert response.status_code == 404