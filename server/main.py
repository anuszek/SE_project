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
        # Importujemy tutaj, aby SQLAlchemy "zarejestrowało" klasy modeli
        # zanim wywołamy create_all().
        from app.models.employee import Employee
        # from app.models.access_log import AccessLog # <-- Odkomentuj, gdy naprawisz ten plik

        # 2. TWORZENIE TABEL
        # Bezwarunkowe wywołanie. SQLAlchemy sprawdzi metadane:
        # - Jeśli tabel nie ma -> stworzy je.
        # - Jeśli są -> zostawi je w spokoju.
        db.create_all()

        # Logowanie dla pewności
        print(f"Connected to DB at: {db_path}")
        # To pokaże, jakie tabele SQLAlchemy widzi i stworzyło
        print("Detected tables:", db.metadata.tables.keys())

    # ----------------------------------------
    # REGISTER BLUEPRINTS
    # ----------------------------------------
    # Tu możesz rejestrować blueprinty...
    # from app.routes.employees import employees_bp
    # app.register_blueprint(employees_bp, url_prefix="/api/employees")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)