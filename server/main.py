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

    os.makedirs(app.instance_path, exist_ok=True)

    db_path = os.path.join(app.instance_path, "access_system.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your-secret-key"

    db.init_app(app)
    migrate.init_app(app, db)

    # ----------------------------------------
    # DATABASE TABLE CREATION
    # ----------------------------------------
    with app.app_context():
        
        from app.models.employee import Employee
        from app.models.employee_face import FaceCredential
        from app.models.qr_code import QRCredential  
        from app.models.access_log import AccessLog
        
        db.create_all()

        print("-" * 50)
        print(f"Connected to DB at: {db_path}")
        print("Detected tables:", db.metadata.tables.keys())
        print("-" * 50)

    # ----------------------------------------
    # REGISTER BLUEPRINTS
    # ----------------------------------------
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

    if not app.config.get("TESTING", False):
        def _cleanup_job():
            """Job: cleaning expired and inactive QR codes every 24 hours."""
            with app.app_context():
                try:
                    refreshed = refresh_expired_qr_codes()
                    print(f"[QR Cleanup Job] Refreshed: {len(refreshed)} employees")
                except Exception as e:
                    print(f"[QR Cleanup Job] Error: {str(e)}")

        scheduler.add_job(
            _cleanup_job,
            'interval',
            hours=24,
            id='cleanup_qr_job',
            replace_existing=True
        )
        
        def _clear_logs_job():
            """Job: clearing expired access logs every 24 hours."""
            with app.app_context():
                try:
                    deleted = clear_expired_logs()
                    print(f"[Log Cleanup Job] Deleted: {deleted} old logs")
                except Exception as e:
                    print(f"[Log Cleanup Job] Error: {str(e)}")

        scheduler.add_job(
            _clear_logs_job,
            'interval',
            hours=24,
            id='clear_logs_job',
            replace_existing=True
        )

        scheduler.start()
        print("[Scheduler] Started QR cleanup job (every 24h)")

        atexit.register(lambda: scheduler.shutdown(wait=False))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, use_reloader=False)