import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Login
resp = requests.post(f"{BASE_URL}/auth/login", json={
    "identifiant": "superadmin",
    "mot_de_passe": "Sedainou111002",
})
resp.raise_for_status()
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Demander l'URL présignée
resp = requests.post(f"{BASE_URL}/medias/upload-url", headers=headers, json={
    "nom_fichier": "test.jpeg",
    "content_type": "image/jpeg",
    "type_media": "image",
    "paroisse_id": 1,
})
resp.raise_for_status()
data = resp.json()
upload_url = data["upload_url"]
key = data["key"]
print("Presigned URL obtenue, key =", key)

# 3. Upload direct vers R2 (aucun passage par un shell, aucun risque d'échappement)
with open("tests/test.jpeg", "rb") as f:
    put_resp = requests.put(upload_url, data=f, headers={"Content-Type": "image/jpeg"})

print("Statut upload:", put_resp.status_code)
print("Réponse upload:", put_resp.text)
put_resp.raise_for_status()

# 4. Confirmer l'upload
resp = requests.post(f"{BASE_URL}/medias/confirm-upload", headers=headers, json={
    "key": key,
    "type_media": "image",
})
resp.raise_for_status()
confirm_data = resp.json()
print("URL publique finale:", confirm_data["url_media"])
print("Taille:", confirm_data["taille_octets"], "octets")