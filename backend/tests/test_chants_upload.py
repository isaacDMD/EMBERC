"""
Test bout-en-bout de l'upload audio pour les chants :
upload-url -> PUT réel vers R2 -> confirm-upload -> POST /chants -> GET.

⚠️ Envoie un vrai petit fichier à Cloudflare R2 et le supprime ensuite.
Nécessite des credentials R2 valides dans .env.
"""
import uuid
import httpx
import pytest

from app.services import storage


def _petit_fichier_audio_test() -> bytes:
    """Faux contenu audio — suffisant pour tester le flux d'upload."""
    return b"ID3" + b"\x00" * 100

@pytest.mark.integration
def test_upload_chant_bout_en_bout(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    nom_fichier = f"test_{uuid.uuid4().hex[:8]}.mp3"

    # 1. Demande d'URL présignée
    resp = client.post(
        "/api/v1/chants/upload-url",
        json={"nom_fichier": nom_fichier, "content_type": "audio/mpeg"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    upload_url, key = data["upload_url"], data["key"]

    try:
        # 2. Upload réel vers R2 (hors de l'app FastAPI)
        put_resp = httpx.put(
            upload_url,
            content=_petit_fichier_audio_test(),
            headers={"Content-Type": "audio/mpeg"},
            timeout=30,
        )
        assert put_resp.status_code == 200, put_resp.text

        # 3. Confirmation
        confirm_resp = client.post(
            "/api/v1/chants/confirm-upload",
            json={"key": key},
            headers=headers,
        )
        assert confirm_resp.status_code == 200, confirm_resp.text
        confirm_data = confirm_resp.json()
        assert confirm_data["taille_octets"] > 0
        fichier_audio_url = confirm_data["fichier_audio_url"]

        # 4. Création du chant
        creer_resp = client.post(
            "/api/v1/chants",
            json={
                "numero": f"TEST-{uuid.uuid4().hex[:6]}",
                "titre": "Chant de test upload",
                "fichier_audio_url": fichier_audio_url,
            },
            headers=headers,
        )
        assert creer_resp.status_code == 201, creer_resp.text
        chant = creer_resp.json()
        assert chant["fichier_audio_url"] == fichier_audio_url

        # 5. Relecture
        get_resp = client.get(f"/api/v1/chants/{chant['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json()["fichier_audio_url"] == fichier_audio_url

    finally:
        storage.delete_object(key)  # on ne laisse rien traîner sur R2


def test_upload_chant_refuse_mauvais_type(client, resp_musical_token):
    headers = {"Authorization": f"Bearer {resp_musical_token}"}
    resp = client.post(
        "/api/v1/chants/upload-url",
        json={"nom_fichier": "test.pdf", "content_type": "application/pdf"},
        headers=headers,
    )
    assert resp.status_code == 400


def test_upload_chant_refuse_sans_token(client):
    resp = client.post(
        "/api/v1/chants/upload-url",
        json={"nom_fichier": "test.mp3", "content_type": "audio/mpeg"},
    )
    assert resp.status_code == 401