import warnings 
warnings.filterwarnings("ignore", category=UserWarning, module='face_recognition_models')
import os
from flask import Flask
from flask_migrate import Migrate
from app.utils.db import db

# GLOBAL migrate object
migrate = Migrate()

def create_app():
    """
    Main Flask application factory.
    Sets up the app, database, and blueprints.
    """

    # ------------------------------
    # Flask app with instance folder
    # ------------------------------
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance/ folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Absolute path to SQLite DB inside instance/
    db_path = os.path.join(app.instance_path, "access_system.db")

    # Database config
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your-secret-key"

    # Initialize DB + migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # ----------------------------------------
    # KONTEKST APLIKACJI I TWORZENIE BAZY
    # ----------------------------------------
    with app.app_context():
        # 1. IMPORT MODELI
        # Ważne: Musimy zaimportować klasy ze wszystkich plików modeli,
        # żeby SQLAlchemy wiedziało o ich istnieniu przed create_all().
        
        from app.models.employee import Employee
        from app.models.employee_face import FaceCredential
        from app.models.qr_code import QRCredential  # Pamiętaj, klasa nazywa się QRCredential

        # 2. TWORZENIE TABEL
        # SQLAlchemy przeskanuje zaimportowane modele i utworzy brakujące tabele
        db.create_all()

        # Logowanie dla pewności
        print("-" * 50)
        print(f"Connected to DB at: {db_path}")
        print("Detected tables:", db.metadata.tables.keys())
        print("-" * 50)

    # ----------------------------------------
    # REGISTER BLUEPRINTS
    # ----------------------------------------
    # Tu później dodasz rejestrację tras (routes), np.:
    from app.routes.employees import employees_bp
    app.register_blueprint(employees_bp, url_prefix="/api/employees")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)