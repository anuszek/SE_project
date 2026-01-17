import sys
import os
import pytest
import warnings
from sqlalchemy.exc import LegacyAPIWarning

warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")

warnings.filterwarnings("ignore", category=LegacyAPIWarning)

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*datetime.datetime.utcnow.*")

warnings.filterwarnings("ignore", category=DeprecationWarning)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.db import db
from main import create_app 

@pytest.fixture
def app():
    """
    Fixture for creating a Flask application for testing.
    Sets up an in-memory SQLite database.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        from app.models.employee import Employee
        from app.models.employee_face import FaceCredential
        from app.models.qr_code import QRCredential
        from app.models.access_log import AccessLog

        db.create_all()

        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """
    Fixture for test API client.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    Fixture for CLI commands.
    """
    return app.test_cli_runner()