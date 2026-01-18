from datetime import datetime
import base64
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from app.models.access_log import AccessLog
from app.utils.db import db
from app.models.employee import Employee

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/logs', methods=['GET'])
def get_access_logs():
    """
    Retrieves access logs with optional limit parameter.
    """
    try:
        limit = request.args.get('limit', default=10, type=int)
        
        logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(limit).all()
        
        logs_data = []
        for log in logs:
            employee = Employee.query.get(log.employee_id) if log.employee_id else None
            
            log_dict = {
                "id": log.id,
                "employee_id": log.employee_id,
                "employee_name": f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
                "status": log.status,
                "verification_method": log.verification_method,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            }
            
            # Include image for denied face access attempts
            if log.image:
                img_base64 = base64.b64encode(log.image).decode('utf-8')
                log_dict['image'] = f'data:image/jpeg;base64,{img_base64}'
            else:
                log_dict['image'] = None
                
            logs_data.append(log_dict)
        
        return jsonify({
            "success": True,
            "logs": logs_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    """
    Returns statistics for the dashboard.
    """
    try:
        from datetime import datetime, timedelta
        
        total_employees = Employee.query.count()
        
        today = datetime.utcnow().date()
        today_access = AccessLog.query.filter(
            AccessLog.timestamp >= today
        ).count()
        
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

@admin_bp.route('/raport', methods=['POST'])
def generate_raport():
    """
    Generates an event report from the access_logs database.
    """
    if not request.is_json:
        return jsonify({"error": "JSON format required"}), 400
    
    data = request.get_json()
    date_from_str = data.get('date_from')
    date_to_str = data.get('date_to')
    entry_type = data.get('entry_type', 'all')
    employee_id = data.get('employee_id')

    query = db.session.query(AccessLog, Employee).join(Employee, AccessLog.employee_id == Employee.id)

    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            query = query.filter(AccessLog.timestamp >= date_from)
        
        if date_to_str:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(AccessLog.timestamp <= date_to)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if employee_id:
        query = query.filter(AccessLog.employee_id == employee_id)

    
    if entry_type == 'access':
        query = query.filter(AccessLog.status == 'granted')
    elif entry_type == 'denied':
        query = query.filter(AccessLog.status == 'denied')

    results = query.order_by(AccessLog.timestamp.desc()).all()

    raport_list = []
    for log, emp in results:
        entry = {
            "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "employee_id": log.employee_id,
            "full_name": f"{emp.first_name} {emp.last_name}",
            "email": emp.email,
            "verification_method": log.verification_method,
            "image": None,
            "status": log.status,
        }
        
        if log.image:
            img_base64 = base64.b64encode(log.image).decode('utf-8')
            entry['image'] = f'data:image/jpeg;base64,{img_base64}'
        else:
            entry['image'] = None
            
        raport_list.append(entry)

    employee_stats = None
    if employee_id:
        stats_query = db.session.query(AccessLog).filter(AccessLog.employee_id == employee_id)
        
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            stats_query = stats_query.filter(AccessLog.timestamp >= date_from)
        
        if date_to_str:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            stats_query = stats_query.filter(AccessLog.timestamp <= date_to)
        
        total_entries = stats_query.count()
        
        successful_entries = stats_query.filter(AccessLog.status == 'granted').count()
        
        failed_face_verifications = stats_query.filter(
            AccessLog.status == 'denied',
            AccessLog.verification_method == 'face'
        ).count()
        
        unique_days = db.session.query(
            func.count(func.distinct(func.date(AccessLog.timestamp)))
        ).filter(
            AccessLog.employee_id == employee_id,
            AccessLog.status == 'granted'
        )
        
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            unique_days = unique_days.filter(AccessLog.timestamp >= date_from)
        
        if date_to_str:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            unique_days = unique_days.filter(AccessLog.timestamp <= date_to)
        
        unique_days_count = unique_days.scalar() or 0
        
        success_percentage = 0
        if total_entries > 0:
            success_percentage = round((successful_entries / total_entries) * 100, 2)
        
        employee_stats = {
            "total_entries": total_entries,
            "successful_entries": successful_entries,
            "unique_working_days": unique_days_count,
            "failed_face_verifications": failed_face_verifications,
            "success_percentage": success_percentage
        }

    response_data = {
        "status": "success",
        "count": len(raport_list),
        "filters": {
            "date_from": date_from_str,
            "date_to": date_to_str,
            "entry_type": entry_type,
            "employee_id": employee_id
        },
        "data": raport_list
    }
    
    if employee_stats:
        response_data["employee_stats"] = employee_stats
    
    return jsonify(response_data), 200
    
