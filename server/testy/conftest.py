import sys
import os
import pytest
import warnings # <--- Dodaj import

# --- UKRYWANIE OSTRZEŻEŃ ---
# Ignoruj błędy starych bibliotek, na które nie mamy wpływu
warnings.filterwarnings("ignore", category=UserWarning, module='face_recognition_models')
warnings.filterwarnings("ignore", category=DeprecationWarning, module='sqlalchemy')
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")
warnings.filterwarnings("ignore", category=DeprecationWarning)
# ---------------------------

# Naprawa ścieżek (to już miałeś)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.db import db
from main import create_app 

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()