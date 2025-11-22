import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# GLOBAL DB object
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """
    Main Flask application factory.
    Sets up the app, database, and blueprints.
    """

    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance/ folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Path: server/instance/access_system.db
    db_path = os.path.join(app.instance_path, "access_system.db")

    # SQLite database config
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your-secret-key"

    # Init DB + migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # ----------------------------------------
    # IMPORT MODELS (so SQLAlchemy knows them)
    # Only import models that exist under `app/models`
    # ----------------------------------------
    try:
        from app.models.employee import Employee
    except Exception:
        Employee = None

    try:
        from app.models.access_log import AccessLog
    except Exception:
        AccessLog = None

    # ----------------------------------------
    # REGISTER BLUEPRINTS
    # (add real ones later)
    # ----------------------------------------
    # Import blueprints from `app/routes` (if present)
    try:
        from app.routes.verify import verify_bp
    except Exception:
        verify_bp = None

    try:
        from app.routes.employees import employees_bp
    except Exception:
        employees_bp = None

    try:
        from app.routes.auth import auth_bp
    except Exception:
        auth_bp = None

    if verify_bp is not None:
        app.register_blueprint(verify_bp, url_prefix="/api/verify")
    if employees_bp is not None:
        app.register_blueprint(employees_bp, url_prefix="/api/employees")
    if auth_bp is not None:
        app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # ----------------------------------------
    # Create DB if it does not exist
    # ----------------------------------------
    with app.app_context():
        if not os.path.exists(db_path):
            print("Creating SQLite database...")
            db.create_all()

    return app


# Run directly (useful locally / Lovable dev server)
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
