from app.enums.roles import RoleEnum
from tests.conftest import _login


def _creer_actualite(client, headers, paroisse_id, titre="Actualité test"):
    return client.post(
        "/api/v1/actualites",
        json={
            "titre": titre,
            "resume": "Un résumé court",
            "contenu": "Le contenu complet de l'actualité",
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def test_creer_actualite_admin_paroisse(client, admin_paroisse_headers, paroisse):
    response = _creer_actualite(client, admin_paroisse_headers, paroisse.id)
    assert response.status_code == 201
    assert response.json()["titre"] == "Actualité test"


def test_creer_actualite_auteur_id_automatique(client, admin_paroisse_headers, paroisse, db):
    from app.models.user import User

    response = _creer_actualite(client, admin_paroisse_headers, paroisse.id)
    auteur_id = response.json()["auteur_id"]

    admin = db.query(User).filter(User.identifiant == "admin_test").first()
    assert auteur_id == admin.id


def test_creer_actualite_refuse_autre_paroisse(client, admin_paroisse_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Autre Paroisse Actu", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    response = _creer_actualite(client, admin_paroisse_headers, autre.id)
    assert response.status_code == 403


def test_creer_actualite_refuse_fidele(client, make_user, paroisse):
    make_user(identifiant="fidele_actu", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    token = _login(client, "fidele_actu", "motdepasse123")

    response = _creer_actualite(client, {"Authorization": f"Bearer {token}"}, paroisse.id)
    assert response.status_code == 403


def test_liste_actualites_filtre_paroisse(client, admin_paroisse_headers, paroisse):
    _creer_actualite(client, admin_paroisse_headers, paroisse.id, titre="Actu filtrée")

    response = client.get(f"/api/v1/actualites?paroisse_id={paroisse.id}")
    assert response.status_code == 200
    assert any(a["titre"] == "Actu filtrée" for a in response.json())


def test_detail_actualite_inexistante(client):
    response = client.get("/api/v1/actualites/999999")
    assert response.status_code == 404


def test_modifier_actualite_sa_paroisse(client, admin_paroisse_headers, paroisse):
    actualite_id = _creer_actualite(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.put(
        f"/api/v1/actualites/{actualite_id}",
        json={"publie": True},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 200
    assert response.json()["publie"] is True


def test_modifier_actualite_refuse_autre_paroisse(client, admin_paroisse_headers, super_admin_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Paroisse E", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    actualite_id = _creer_actualite(client, super_admin_headers, autre.id).json()["id"]

    response = client.put(
        f"/api/v1/actualites/{actualite_id}",
        json={"publie": True},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403


def test_supprimer_actualite(client, admin_paroisse_headers, paroisse):
    actualite_id = _creer_actualite(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.delete(f"/api/v1/actualites/{actualite_id}", headers=admin_paroisse_headers)
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/actualites/{actualite_id}")
    assert get_resp.status_code == 404