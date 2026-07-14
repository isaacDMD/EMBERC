import os
import uuid
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL")

R2_ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Types MIME autorisés par catégorie de média (réutilisable pour chants/médias)
ALLOWED_CONTENT_TYPES = {
    "audio": {"audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg"},
    "video": {"video/mp4", "video/webm", "video/quicktime"},
    "image": {"image/jpeg", "image/png", "image/webp"},
    "document": {"application/pdf"},
}

# Taille max en octets par catégorie
MAX_SIZE_BYTES = {
    "audio": 50 * 1024 * 1024,      # 50 Mo
    "video": 500 * 1024 * 1024,     # 500 Mo
    "image": 10 * 1024 * 1024,      # 10 Mo
    "document": 20 * 1024 * 1024,   # 20 Mo
}


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT_URL,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def generate_object_key(dossier: str, nom_fichier_original: str) -> str:
    """
    Construit une clé unique pour éviter les collisions.
    Ex: medias/3f9a2b1c-....-mp3, chants/audio/....
    """
    extension = ""
    if "." in nom_fichier_original:
        extension = "." + nom_fichier_original.rsplit(".", 1)[-1].lower()
    return f"{dossier}/{uuid.uuid4().hex}{extension}"


def generate_presigned_upload_url(key: str, content_type: str, expires_in: int = 1200) -> str:
    """
    Génère une URL présignée valable `expires_in` secondes (20 min par défaut)
    permettant un PUT direct du client vers R2.
    """
    client = _get_s3_client()
    return client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": R2_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )


def build_public_url(key: str) -> str:
    return f"{R2_PUBLIC_URL}/{key}"


def delete_object(key: str) -> None:
    client = _get_s3_client()
    client.delete_object(Bucket=R2_BUCKET_NAME, Key=key)


def extract_key_from_url(url: str) -> str:
    """Retire le préfixe R2_PUBLIC_URL pour retrouver la clé stockée en base."""
    return url.replace(f"{R2_PUBLIC_URL}/", "", 1)

def get_object_size(key: str) -> int | None:
    """
        Interoge R2 pour connaitre la taille réelle de l'objet
        Retourne None si l'objet n'existe pas (upload pas terminé ou echoué)
    """

    client = _get_s3_client()
    try:
        response = client.head_object(Bucket = R2_BUCKET_NAME, Key=key)
        return response["ContentLength"]
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            return None
        raise

