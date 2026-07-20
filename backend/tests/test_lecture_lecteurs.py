from datetime import datetime, timedelta


def _creer_programme(client, headers, paroisse_id):
    return client.post(
        "/api/v1/programmes",
        json={
            "titre": "Culte pour lecteurs",
            "date_heure": (datetime.now() + timedelta(days=4)).isoformat(),
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def _creer_lecture(client, headers, programme_id, paroisse_id):
    return client.post(
        "/api/v1/lectures",
        json={
            "reference": "Matthieu 5:1-12",
            "date_lecture": (datetime.now() + timedelta(days=4)).isoformat(),
            "programme_id": programme_id,
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def test_assigner_lecteur(client, admin_paroisse_headers, paroisse, make_user):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]
    lecteur = make_user(identifiant="lecteur_1", paroisse_id=paroisse.id)

    response = client.post(
        f"/api/v1/lectures/{lecture_id}/lecteurs",
        json={"lecteur_id": lecteur.id, "langue": "fr"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 201
    lecteurs = response.json()
    assert len(lecteurs) == 1
    assert lecteurs[0]["lecteur_id"] == lecteur.id
    assert lecteurs[0]["langue"] == "fr"


def test_assigner_plusieurs_lecteurs_langues_differentes(client, admin_paroisse_headers, paroisse, make_user):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]
    lecteur_fr = make_user(identifiant="lecteur_fr", paroisse_id=paroisse.id)
    lecteur_ewe = make_user(identifiant="lecteur_ewe", paroisse_id=paroisse.id)

    client.post(
        f"/api/v1/lectures/{lecture_id}/lecteurs",
        json={"lecteur_id": lecteur_fr.id, "langue": "fr"},
        headers=admin_paroisse_headers,
    )
    response = client.post(
        f"/api/v1/lectures/{lecture_id}/lecteurs",
        json={"lecteur_id": lecteur_ewe.id, "langue": "ewe"},
        headers=admin_paroisse_headers,
    )

    assert response.status_code == 201
    lecteurs = response.json()
    assert len(lecteurs) == 2
    langues = {l["langue"] for l in lecteurs}
    assert langues == {"fr", "ewe"}


def test_assigner_lecteur_lecture_inexistante(client, admin_paroisse_headers, make_user, paroisse):
    lecteur = make_user(identifiant="lecteur_orphan", paroisse_id=paroisse.id)

    response = client.post(
        "/api/v1/lectures/999999/lecteurs",
        json={"lecteur_id": lecteur.id, "langue": "fr"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 404


def test_assigner_lecteur_invalide(client, admin_paroisse_headers, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]

    response = client.post(
        f"/api/v1/lectures/{lecture_id}/lecteurs",
        json={"lecteur_id": 999999, "langue": "fr"},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 400


def test_liste_lecteurs_lecture(client, admin_paroisse_headers, paroisse, make_user):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]
    lecteur = make_user(identifiant="lecteur_liste", paroisse_id=paroisse.id)
    client.post(
        f"/api/v1/lectures/{lecture_id}/lecteurs",
        json={"lecteur_id": lecteur.id, "langue": "fr"},
        headers=admin_paroisse_headers,
    )

    response = client.get(f"/api/v1/lectures/{lecture_id}/lecteurs")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_retirer_lecteur(client, admin_paroisse_headers, paroisse, make_user):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]
    lecteur = make_user(identifiant="lecteur_retrait", paroisse_id=paroisse.id)
    assoc_resp = client.post(
        f"/api/v1/lectures/{lecture_id}/lecteurs",
        json={"lecteur_id": lecteur.id, "langue": "fr"},
        headers=admin_paroisse_headers,
    )
    assoc_id = assoc_resp.json()[0]["id"]

    response = client.delete(
        f"/api/v1/lectures/{lecture_id}/lecteurs/{assoc_id}", headers=admin_paroisse_headers
    )
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/lectures/{lecture_id}/lecteurs")
    assert get_resp.json() == []


def test_retirer_lecteur_association_inexistante(client, admin_paroisse_headers, paroisse):
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_id = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]

    response = client.delete(
        f"/api/v1/lectures/{lecture_id}/lecteurs/999999", headers=admin_paroisse_headers
    )
    assert response.status_code == 404


def test_retirer_lecteur_mauvaise_lecture(client, admin_paroisse_headers, paroisse, make_user):
    """L'assoc_id existe mais n'appartient pas à cette lecture_id."""
    programme_id = _creer_programme(client, admin_paroisse_headers, paroisse.id).json()["id"]
    lecture_1 = _creer_lecture(client, admin_paroisse_headers, programme_id, paroisse.id).json()["id"]
    lecture_2 = client.post(
        "/api/v1/lectures",
        json={
            "reference": "Autre référence",
            "date_lecture": "2026-08-01T10:00:00",
            "programme_id": programme_id,
            "paroisse_id": paroisse.id,
        },
        headers=admin_paroisse_headers,
    ).json()["id"]

    lecteur = make_user(identifiant="lecteur_croise", paroisse_id=paroisse.id)
    assoc_resp = client.post(
        f"/api/v1/lectures/{lecture_1}/lecteurs",
        json={"lecteur_id": lecteur.id, "langue": "fr"},
        headers=admin_paroisse_headers,
    )
    assoc_id = assoc_resp.json()[0]["id"]

    # Tente de retirer via lecture_2, alors que l'assoc appartient à lecture_1
    response = client.delete(
        f"/api/v1/lectures/{lecture_2}/lecteurs/{assoc_id}", headers=admin_paroisse_headers
    )
    assert response.status_code == 404