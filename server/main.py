import warnings 
warnings.filterwarnings("ignore", category=UserWarning, module='face_recognition_models')
import os
import atexit
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.helpers import refresh_expired_qr_codes
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

    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5000","http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })

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
    # DATABASE TABLE CREATION
    # ----------------------------------------
    with app.app_context():
        # 1. IMPORT MODELS
        # Important: We must import classes from all model files,
        # so SQLAlchemy knows about their existence before create_all().
        
        from app.models.employee import Employee
        from app.models.employee_face import FaceCredential
        from app.models.qr_code import QRCredential  # Remember, the class is named QRCredential
        from app.models.access_log import AccessLog
        
        # 2. TABLE CREATION
        # SQLAlchemy will scan imported models and create missing tables
        db.create_all()

        # Logging for confirmation
        print("-" * 50)
        print(f"Connected to DB at: {db_path}")
        print("Detected tables:", db.metadata.tables.keys())
        print("-" * 50)

    # ----------------------------------------
    # REGISTER BLUEPRINTS
    # ----------------------------------------
    # You will add route registration here later, e.g.:
    from app.routes.employees import employees_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(employees_bp, url_prefix="/api/employees")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # ----------------------------------------
    # SCHEDULER
    # ----------------------------------------
    scheduler = BackgroundScheduler()

    # Run scheduler only when NOT in TESTING mode
    if not app.config.get("TESTING", False):
        def _cleanup_job():
            """Job: cleaning expired and inactive QR codes every 24 hours."""
            with app.app_context():
                try:
                    refreshed = refresh_expired_qr_codes()
                    print(f"[QR Cleanup Job] Refreshed: {len(refreshed)} employees")
                except Exception as e:
                    print(f"[QR Cleanup Job] Error: {str(e)}")

        # Add job: run every 24 hours
        scheduler.add_job(
            _cleanup_job,
            'interval',
            hours=24,
            id='cleanup_qr_job',
            replace_existing=True
        )

        # Start scheduler
        scheduler.start()
        print("[Scheduler] Started QR cleanup job (every 24h)")

        # Shutdown scheduler when the application exits
        atexit.register(lambda: scheduler.shutdown(wait=False))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)