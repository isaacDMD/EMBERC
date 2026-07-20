import os
import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

load_dotenv()

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://emberc_test:emberc_test_pass@localhost:5433/emberc_test_db",
)

from app.database import Base
import app.models  # noqa: F401 — enregistre tous les modèles sur Base.metadata
from app.main import app
from app.dependencies import get_db
from app.auth.security import hash_password
from app.enums.roles import RoleEnum
from app.models.user import User
from app.models.paroisse import Paroisse

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crée toutes les tables une fois pour la session de tests, les supprime à la fin."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """
    Isolation par test : chaque test tourne dans une transaction externe
    qui est annulée (rollback) à la fin, même si le code applicatif fait
    ses propres db.commit(). Pattern classique SQLAlchemy (savepoints imbriqués).
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """TestClient FastAPI avec get_db surchargé pour utiliser la session transactionnelle."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def paroisse(db):
    p = Paroisse(nom="Paroisse Test", ville="Lomé", actif=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def make_user(db):
    """Factory : crée un utilisateur avec rôle/paroisse/mot de passe personnalisables."""
    def _make_user(
        identifiant="user_test",
        role=RoleEnum.fidele,
        paroisse_id=None,
        mot_de_passe="motdepasse123",
    ):
        user = User(
            nom="Test",
            prenom="User",
            identifiant=identifiant,
            email=None,
            mot_de_passe=hash_password(mot_de_passe),
            role=role,
            paroisse_id=paroisse_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _make_user


def _login(client, identifiant, mot_de_passe):
    response = client.post(
        "/api/v1/auth/login",
        json={"identifiant": identifiant, "mot_de_passe": mot_de_passe},
    )
    return response.json()["access_token"]


@pytest.fixture
def super_admin_headers(client, make_user):
    make_user(identifiant="super_test", role=RoleEnum.super_admin, mot_de_passe="motdepasse123")
    token = _login(client, "super_test", "motdepasse123")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_paroisse_headers(client, make_user, paroisse):
    make_user(
        identifiant="admin_test",
        role=RoleEnum.admin_paroisse,
        paroisse_id=paroisse.id,
        mot_de_passe="motdepasse123",
    )
    token = _login(client, "admin_test", "motdepasse123")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def resp_musical_token(client, make_user):
    make_user(
        identifiant="resp_musical_test",
        role=RoleEnum.resp_musical,
        mot_de_passe="motdepasse123",
    )
    return _login(client, "resp_musical_test", "motdepasse123")