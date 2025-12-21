import sys
import os
import pytest
import warnings
from sqlalchemy.exc import LegacyAPIWarning

# --- KONFIGURACJA IGNOROWANIA OSTRZEŻEŃ ---
# Ignoruj ostrzeżenia o przestarzałym pkg_resources (z face_recognition)
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")

# Ignoruj ostrzeżenia o Query.get() (SQLAlchemy Legacy)
warnings.filterwarnings("ignore", category=LegacyAPIWarning)

# Ignoruj ostrzeżenia o datetime.utcnow() (Python 3.12+)
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*datetime.datetime.utcnow.*")

# Ogólne ignorowanie DeprecationWarning dla czystości konsoli
warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- RESZTA PLIKU ---

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
    """Fixture dla komend CLI."""
    return app.test_cli_runner()