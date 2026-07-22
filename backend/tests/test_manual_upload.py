"""
Script manuel de vérification bout-en-bout de l'upload (hors suite pytest).
Usage : python scripts/manual_upload_test.py --identifiant superadmin --mot-de-passe ***
Nécessite un serveur FastAPI lancé localement et un fichier de test disponible.
"""
import argparse
import requests

BASE_URL = "http://localhost:8000/api/v1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--identifiant", required=True)
    parser.add_argument("--mot-de-passe", required=True)
    parser.add_argument("--fichier", default="scripts/fixtures/test.jpeg")
    args = parser.parse_args()

    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "identifiant": args.identifiant,
        "mot_de_passe": args.mot_de_passe,
    })
    resp.raise_for_status()
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.post(f"{BASE_URL}/medias/upload-url", headers=headers, json={
        "nom_fichier": "test.jpeg",
        "content_type": "image/jpeg",
        "type_media": "image",
        "paroisse_id": 1,
    })
    resp.raise_for_status()
    data = resp.json()
    upload_url, key = data["upload_url"], data["key"]
    print("Presigned URL obtenue, key =", key)

    with open(args.fichier, "rb") as f:
        put_resp = requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"})
    put_resp.raise_for_status()
    print("Statut upload:", put_resp.status_code)

    resp = requests.post(f"{BASE_URL}/medias/confirm-upload", headers=headers, json={
        "key": key,
        "type_media": "image",
    })
    resp.raise_for_status()
    confirm_data = resp.json()
    print("URL publique finale:", confirm_data["url_media"])
    print("Taille:", confirm_data["taille_octets"], "octets")


if __name__ == "__main__":
    main()