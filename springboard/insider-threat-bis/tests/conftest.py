import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import Config  # noqa: E402


def _artefacts_present() -> bool:
    required = ["gb.pkl", "scaler.pkl", "feature_columns.pkl", "baselines.pkl"]
    return (
        all((Config.MODEL_DIR / f).exists() for f in required)
        and Config.FEATURES_CSV.exists()
    )


needs_model = pytest.mark.skipif(
    not _artefacts_present(),
    reason="model artefacts missing — run `python scripts/bootstrap.py` first",
)


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    from app import create_app  # noqa: PLC0415

    class TestConfig(Config):
        TESTING = True
        # Isolated database so tests never touch the developer's cases/audit log.
        SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///{tmp_path_factory.mktemp('db') / 'test.db'}"
        )
        SEED_ANALYSTS = {
            "admin": ("admin-pw", "admin"),
            "analyst": ("analyst-pw", "analyst"),
            "viewer": ("viewer-pw", "viewer"),
        }

    return create_app(TestConfig)


@pytest.fixture()
def client(app):
    return app.test_client()


def _token(client, username, password):
    res = client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]


@pytest.fixture()
def analyst_headers(client):
    return {"Authorization": f"Bearer {_token(client, 'analyst', 'analyst-pw')}"}


@pytest.fixture()
def viewer_headers(client):
    return {"Authorization": f"Bearer {_token(client, 'viewer', 'viewer-pw')}"}


@pytest.fixture()
def admin_headers(client):
    return {"Authorization": f"Bearer {_token(client, 'admin', 'admin-pw')}"}


@pytest.fixture(scope="session")
def sample_user(app):
    from app.ml import engine as eng  # noqa: PLC0415

    with app.app_context():
        engine = eng.get_engine()
        return engine.users().iloc[0]["user"]
