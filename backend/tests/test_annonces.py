from datetime import date, timedelta
from app.enums.roles import RoleEnum
from tests.conftest import _login


def _creer_annonce(client, headers, paroisse_id, titre="Annonce test"):
    return client.post(
        "/api/v1/annonces",
        json={
            "titre": titre,
            "contenu": "Contenu de l'annonce",
            "date_debut": str(date.today()),
            "date_fin": str(date.today() + timedelta(days=7)),
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def test_creer_annonce_admin_paroisse(client, admin_paroisse_headers, paroisse):
    response = _creer_annonce(client, admin_paroisse_headers, paroisse.id)
    assert response.status_code == 201
    data = response.json()
    assert data["titre"] == "Annonce test"
    assert data["publie"] is False


def test_creer_annonce_auteur_id_automatique(client, admin_paroisse_headers, paroisse, db):
    from app.models.user import User

    response = _creer_annonce(client, admin_paroisse_headers, paroisse.id)
    auteur_id = response.json()["auteur_id"]

    admin = db.query(User).filter(User.identifiant == "admin_test").first()
    assert auteur_id == admin.id


def test_creer_annonce_refuse_autre_paroisse(client, admin_paroisse_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Autre Paroisse Annonce", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    response = _creer_annonce(client, admin_paroisse_headers, autre.id)
    assert response.status_code == 403


def test_creer_annonce_refuse_fidele(client, make_user, paroisse):
    make_user(identifiant="fidele_annonce", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    token = _login(client, "fidele_annonce", "motdepasse123")

    response = _creer_annonce(client, {"Authorization": f"Bearer {token}"}, paroisse.id)
    assert response.status_code == 403


def test_liste_annonces_filtre_paroisse(client, admin_paroisse_headers, paroisse):
    _creer_annonce(client, admin_paroisse_headers, paroisse.id, titre="Annonce filtrée")

    response = client.get(f"/api/v1/annonces?paroisse_id={paroisse.id}")
    assert response.status_code == 200
    assert any(a["titre"] == "Annonce filtrée" for a in response.json())


def test_liste_annonces_actives_seulement(client, admin_paroisse_headers, paroisse):
    client.post(
        "/api/v1/annonces",
        json={
            "titre": "Annonce expirée",
            "contenu": "Périmée",
            "date_debut": str(date.today() - timedelta(days=10)),
            "date_fin": str(date.today() - timedelta(days=1)),
            "paroisse_id": paroisse.id,
        },
        headers=admin_paroisse_headers,
    )
    _creer_annonce(client, admin_paroisse_headers, paroisse.id, titre="Annonce active")

    response = client.get(f"/api/v1/annonces?actives_seulement=true&paroisse_id={paroisse.id}")
    titres = [a["titre"] for a in response.json()]
    assert "Annonce active" in titres
    assert "Annonce expirée" not in titres


def test_detail_annonce_inexistante(client):
    response = client.get("/api/v1/annonces/999999")
    assert response.status_code == 404


def test_modifier_annonce_sa_paroisse(client, admin_paroisse_headers, paroisse):
    annonce_id = _creer_annonce(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.put(
        f"/api/v1/annonces/{annonce_id}",
        json={"important": True},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 200
    assert response.json()["important"] is True


def test_modifier_annonce_refuse_autre_paroisse(client, admin_paroisse_headers, super_admin_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Paroisse D", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    annonce_id = _creer_annonce(client, super_admin_headers, autre.id).json()["id"]

    response = client.put(
        f"/api/v1/annonces/{annonce_id}",
        json={"important": True},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403


def test_supprimer_annonce(client, admin_paroisse_headers, paroisse):
    annonce_id = _creer_annonce(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.delete(f"/api/v1/annonces/{annonce_id}", headers=admin_paroisse_headers)
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/annonces/{annonce_id}")
    assert get_resp.status_code == 404