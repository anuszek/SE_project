from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models.access_log import AccessLog
from sqlalchemy.exc import IntegrityError
import re
from app.utils.db import db
from app.models.employee import Employee
from app.models.employee_face import FaceCredential
from app.models.qr_code import QRCredential
from app.services.face_service import FaceServices
from app.services.qr_service import QRService
from app.utils.helpers import delete_inactive_qr_codes, get_next_available_id, refresh_expired_qr_codes

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/clean_qr', methods=['POST', 'GET'])
def admin_clean_qr():
    """
    Wywołanie: usuń nieaktywne i odśwież wygasłe. Zabezpiecz w produkcji (token/IP).
    """

    # opcjonalnie: najpierw usuń nieaktywne, potem odśwież wygasłe
    deleted = delete_inactive_qr_codes()
    refreshed = refresh_expired_qr_codes()
    return {"deleted": deleted, "refreshed": refreshed}, 200

@admin_bp.route('/access-log/create', methods=['POST'])
def create_access_log():
    """Zapisuje log dostępu do bazy danych"""
    try:
        data = request.get_json()
        
        employee_id = data.get('employee_id')
        status = data.get('status')  # 'granted' lub 'denied'
        verification_method = data.get('verification_method')  # 'face' lub 'qr'
        
        if not all([employee_id, status, verification_method]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Stwórz nowy log
        log = AccessLog(
            employee_id=employee_id,
            status=status,
            verification_method=verification_method
        )
        
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Access log recorded",
            "log_id": log.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/logs', methods=['GET'])
def get_access_logs():
    """Pobiera wszystkie logi dostępu"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        
        logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(limit).all()
        
        logs_data = []
        for log in logs:
            employee = Employee.query.get(log.employee_id) if log.employee_id else None
            
            logs_data.append({
                "id": log.id,
                "employee_id": log.employee_id,
                "employee_name": f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
                "status": log.status,
                "verification_method": log.verification_method,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            })
        
        return jsonify({
            "success": True,
            "logs": logs_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    """Zwraca statystyki dla dashboardu"""
    try:
        from datetime import datetime, timedelta
        
        total_employees = Employee.query.count()
        
        # Logi z dzisiaj
        today = datetime.utcnow().date()
        today_access = AccessLog.query.filter(
            AccessLog.timestamp >= today
        ).count()
        
        # Dzisiejsze odmowy dostępu
        today_denied = AccessLog.query.filter(
            AccessLog.timestamp >= today,
            AccessLog.status == 'denied'
        ).count()
        
        return jsonify({
            "success": True,
            "total_employees": total_employees,
            "active_employees": total_employees,
            "today_access": today_access,
            "today_denied": today_denied,
            "pending_verifications": 0
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500