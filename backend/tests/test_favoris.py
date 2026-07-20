from tests.conftest import _login


def _headers_fidele(client, make_user, identifiant="fidele_favoris"):
    make_user(identifiant=identifiant, mot_de_passe="motdepasse123")
    token = _login(client, identifiant, "motdepasse123")
    return {"Authorization": f"Bearer {token}"}


def test_ajouter_favori(client, make_user):
    headers = _headers_fidele(client, make_user)

    response = client.post(
        "/api/v1/favoris",
        json={"type_favoris": "chant", "item_id": 1},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type_favoris"] == "chant"
    assert data["item_id"] == 1


def test_ajouter_favori_sans_token(client):
    response = client.post(
        "/api/v1/favoris", json={"type_favoris": "chant", "item_id": 1}
    )
    assert response.status_code == 401


def test_ajouter_favori_duplique_refuse(client, make_user):
    headers = _headers_fidele(client, make_user)
    client.post(
        "/api/v1/favoris",
        json={"type_favoris": "media", "item_id": 5},
        headers=headers,
    )

    response = client.post(
        "/api/v1/favoris",
        json={"type_favoris": "media", "item_id": 5},
        headers=headers,
    )
    assert response.status_code == 409


def test_meme_item_types_differents_autorise(client, make_user):
    """La contrainte unique porte sur (user_id, type_favoris, item_id) : même item_id
    mais type_favoris différent doit être autorisé."""
    headers = _headers_fidele(client, make_user)
    r1 = client.post(
        "/api/v1/favoris",
        json={"type_favoris": "chant", "item_id": 7},
        headers=headers,
    )
    r2 = client.post(
        "/api/v1/favoris",
        json={"type_favoris": "annonce", "item_id": 7},
        headers=headers,
    )
    assert r1.status_code == 201
    assert r2.status_code == 201


def test_liste_favoris_utilisateur(client, make_user):
    headers = _headers_fidele(client, make_user)
    client.post(
        "/api/v1/favoris",
        json={"type_favoris": "chant", "item_id": 10},
        headers=headers,
    )
    client.post(
        "/api/v1/favoris",
        json={"type_favoris": "evenement", "item_id": 11},
        headers=headers,
    )

    response = client.get("/api/v1/favoris", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_liste_favoris_filtre_type(client, make_user):
    headers = _headers_fidele(client, make_user)
    client.post(
        "/api/v1/favoris",
        json={"type_favoris": "chant", "item_id": 20},
        headers=headers,
    )
    client.post(
        "/api/v1/favoris",
        json={"type_favoris": "article", "item_id": 21},
        headers=headers,
    )

    response = client.get("/api/v1/favoris?type_favoris=chant", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type_favoris"] == "chant"


def test_liste_favoris_isolee_par_utilisateur(client, make_user):
    headers_a = _headers_fidele(client, make_user, identifiant="user_favoris_a")
    headers_b = _headers_fidele(client, make_user, identifiant="user_favoris_b")

    client.post(
        "/api/v1/favoris",
        json={"type_favoris": "chant", "item_id": 30},
        headers=headers_a,
    )

    response_b = client.get("/api/v1/favoris", headers=headers_b)
    assert response_b.json() == []


def test_retirer_favori(client, make_user):
    headers = _headers_fidele(client, make_user)
    favori_id = client.post(
        "/api/v1/favoris",
        json={"type_favoris": "chant", "item_id": 40},
        headers=headers,
    ).json()["id"]

    response = client.delete(f"/api/v1/favoris/{favori_id}", headers=headers)
    assert response.status_code == 204

    liste = client.get("/api/v1/favoris", headers=headers)
    assert liste.json() == []


def test_retirer_favori_inexistant(client, make_user):
    headers = _headers_fidele(client, make_user)
    response = client.delete("/api/v1/favoris/999999", headers=headers)
    assert response.status_code == 404


def test_retirer_favori_dun_autre_utilisateur_404(client, make_user):
    """Sécurité : retirer le favori d'un autre user doit renvoyer 404, pas 403
    (pour ne pas révéler l'existence de la ressource — cf. principe du projet)."""
    headers_a = _headers_fidele(client, make_user, identifiant="proprietaire_favori")
    headers_b = _headers_fidele(client, make_user, identifiant="intrus_favori")

    favori_id = client.post(
        "/api/v1/favoris",
        json={"type_favoris": "chant", "item_id": 50},
        headers=headers_a,
    ).json()["id"]

    response = client.delete(f"/api/v1/favoris/{favori_id}", headers=headers_b)
    assert response.status_code == 404

    # Le favori existe toujours pour le propriétaire
    liste_a = client.get("/api/v1/favoris", headers=headers_a)
    assert len(liste_a.json()) == 1