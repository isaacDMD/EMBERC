from app.enums.roles import RoleEnum
from tests.conftest import _login


def _creer_media(client, headers, paroisse_id, titre="Média test", type_media="audio", url="https://exemple.com/fichier.mp3"):
    return client.post(
        "/api/v1/medias",
        json={
            "titre": titre,
            "type_media": type_media,
            "url_media": url,
            "paroisse_id": paroisse_id,
        },
        headers=headers,
    )


def test_creer_media_admin_paroisse(client, admin_paroisse_headers, paroisse):
    response = _creer_media(client, admin_paroisse_headers, paroisse.id)
    assert response.status_code == 201
    assert response.json()["titre"] == "Média test"


def test_creer_media_refuse_autre_paroisse(client, admin_paroisse_headers, db):
    from app.models.paroisse import Paroisse

    autre = Paroisse(nom="Autre Paroisse Media", actif=True)
    db.add(autre)
    db.commit()
    db.refresh(autre)

    response = _creer_media(client, admin_paroisse_headers, autre.id)
    assert response.status_code == 403


def test_creer_media_refuse_fidele(client, make_user, paroisse):
    make_user(identifiant="fidele_media", role=RoleEnum.fidele, mot_de_passe="motdepasse123")
    token = _login(client, "fidele_media", "motdepasse123")

    response = _creer_media(client, {"Authorization": f"Bearer {token}"}, paroisse.id)
    assert response.status_code == 403


def test_liste_medias_filtre_type(client, admin_paroisse_headers, paroisse):
    _creer_media(client, admin_paroisse_headers, paroisse.id, titre="Audio A", type_media="audio")
    _creer_media(client, admin_paroisse_headers, paroisse.id, titre="Vidéo A", type_media="video", url="https://exemple.com/v.mp4")

    response = client.get(f"/api/v1/medias?type_media=audio&paroisse_id={paroisse.id}")
    titres = [m["titre"] for m in response.json()]
    assert "Audio A" in titres
    assert "Vidéo A" not in titres


def test_detail_media_inexistant(client):
    response = client.get("/api/v1/medias/999999")
    assert response.status_code == 404


def test_modifier_media_sa_paroisse(client, admin_paroisse_headers, paroisse):
    media_id = _creer_media(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.put(
        f"/api/v1/medias/{media_id}",
        json={"publie": True},
        headers=admin_paroisse_headers,
    )
    assert response.status_code == 200
    assert response.json()["publie"] is True


def test_supprimer_media(client, admin_paroisse_headers, paroisse, monkeypatch):
    """
    delete_media appelle _supprimer_fichier_r2_si_present -> storage.delete_object,
    qui ferait un vrai appel réseau vers R2. On le neutralise ici.
    """
    from app.services import storage
    monkeypatch.setattr(storage, "delete_object", lambda key: None)

    media_id = _creer_media(client, admin_paroisse_headers, paroisse.id).json()["id"]

    response = client.delete(f"/api/v1/medias/{media_id}", headers=admin_paroisse_headers)
    assert response.status_code == 204

    get_resp = client.get(f"/api/v1/medias/{media_id}")
    assert get_resp.status_code == 404