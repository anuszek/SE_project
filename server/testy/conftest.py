import sys
import os
import pytest
import warnings

# --- UKRYWANIE OSTRZEŻEŃ ---
warnings.filterwarnings("ignore", category=UserWarning, module='face_recognition_models')
warnings.filterwarnings("ignore", category=DeprecationWarning, module='sqlalchemy')
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Naprawa ścieżek
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.db import db
from main import create_app 

@pytest.fixture
def app():
    # Tworzymy instancję aplikacji
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        # IMPORTUJEMY MODELE TUTAJ - to kluczowe dla db.create_all()
        # Dzięki temu SQLAlchemy wie, jakie tabele stworzyć w sqlite :memory:
        from app.models.employee import Employee
        from app.models.employee_face import FaceCredential
        from app.models.qr_code import QRCredential
        from app.models.access_log import AccessLog

        db.create_all()

        yield app
        
        # Sprzątanie po testach
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture dla klienta testowego API."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture dla komend CLI (jeśli używasz)."""
    return app.test_cli_runner()