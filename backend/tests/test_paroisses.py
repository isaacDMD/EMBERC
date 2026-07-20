from app.enums.roles import RoleEnum


def test_liste_paroisses_publique(client, paroisse):
    response = client.get("/api/v1/paroisses")
    assert response.status_code == 200
    noms = [p["nom"] for p in response.json()]
    assert "Paroisse Test" in noms


def test_detail_paroisse_publique(client, paroisse):
    response = client.get(f"/api/v1/paroisses/{paroisse.id}")
    assert response.status_code == 200
    assert response.json()["nom"] == "Paroisse Test"


def test_detail_paroisse_inexistante(client):
    response = client.get("/api/v1/paroisses/999999")
    assert response.status_code == 404


def test_creer_paroisse_super_admin(client, super_admin_headers):
    response = client.post(
        "/api/v1/paroisses",
        json={"nom": "Nouvelle Paroisse", "ville": "Kara"},
        headers=super_admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nom"] == "Nouvelle Paroisse"
    assert data["actif"] is True


def test_creer_paroisse_refuse_sans_role(client, admin_paroisse_headers):
    """Un admin_paroisse ne peut PAS créer de nouvelle paroisse (réservé au super_admin)."""
    response = client.post(
        "/api/v1/paroisses",
        json={"nom": "Paroisse Interdite"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403


def test_creer_paroisse_refuse_sans_token(client):
    response = client.post("/api/v1/paroisses", json={"nom": "Sans Auth"})
    assert response.status_code == 401


def test_modifier_paroisse_super_admin(client, super_admin_headers, paroisse):
    response = client.put(
        f"/api/v1/paroisses/{paroisse.id}",
        json={"ville": "Sokodé"},
        headers=super_admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["ville"] == "Sokodé"


def test_modifier_sa_propre_paroisse_admin_paroisse(client, admin_paroisse_headers, paroisse):
    """admin_paroisse peut modifier SA paroisse."""
    response = client.put(
        f"/api/v1/paroisses/{paroisse.id}",
        json={"description": "Mise à jour par l'admin de paroisse"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Mise à jour par l'admin de paroisse"


def test_modifier_autre_paroisse_refuse_admin_paroisse(client, admin_paroisse_headers, db):
    """Isolation par paroisse : admin_paroisse ne peut PAS modifier une AUTRE paroisse."""
    from app.models.paroisse import Paroisse

    autre_paroisse = Paroisse(nom="Autre Paroisse", actif=True)
    db.add(autre_paroisse)
    db.commit()
    db.refresh(autre_paroisse)

    response = client.put(
        f"/api/v1/paroisses/{autre_paroisse.id}",
        json={"ville": "Interdit"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 403


def test_modifier_paroisse_refuse_fidele(client, make_user, paroisse):
    from tests.conftest import _login

    make_user(identifiant="fidele_test", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    token = _login(client, "fidele_test", "motdepasse123")

    response = client.put(
        f"/api/v1/paroisses/{paroisse.id}",
        json={"ville": "Interdit"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403