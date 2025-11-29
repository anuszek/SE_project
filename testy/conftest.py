# tests/conftest.py
import pytest
from app.utils.db import db
# Zamiast importować create_app z main.py, lepiej przenieść create_app do app/__init__.py
# Ale jeśli masz go w main.py, zaimportuj go stąd:
from main import create_app 

@pytest.fixture
def app():
    """Tworzy instancję aplikacji w trybie testowym."""
    app = create_app()
    
    # Ustawiamy konfigurację testową
    app.config.update({
        "TESTING": True,
        # Baza w pamięci RAM - super szybka i czysta
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", 
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    # Tworzymy tabele w bazie RAM
    with app.app_context():
        db.create_all()
        yield app
        # Po testach usuwamy tabele
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Klient HTTP do odpytywania naszego API."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner do komend CLI (opcjonalne)."""
    return app.test_cli_runner()