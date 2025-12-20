from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models.access_log import AccessLog
from sqlalchemy.exc import IntegrityError
import re
from app.utils.db import db
from app.models.employee import Employee

admin_bp = Blueprint('admin', __name__)

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