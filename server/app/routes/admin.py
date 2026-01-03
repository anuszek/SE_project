from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models.access_log import AccessLog
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

@admin_bp.route('/raport', methods=['POST'])
def generate_raport():
    """
    Generuje raport zdarzeń z bazy access_logs.
    Oczekuje JSON: { "date_from": "...", "date_to": "...", "entry_type": "...", "employee_id": ... }
    """
    if not request.is_json:
        return jsonify({"error": "Wymagany format JSON"}), 400
    
    data = request.get_json()
    date_from_str = data.get('date_from')
    date_to_str = data.get('date_to')
    entry_type = data.get('entry_type', 'all')  # domyślnie 'all'
    employee_id = data.get('employee_id')

    # 1. Budujemy podstawowe zapytanie z Joinem, żeby mieć dane pracownika
    # Używamy db.session.query, bo łączymy dwie tabele
    query = db.session.query(AccessLog, Employee).join(Employee, AccessLog.employee_id == Employee.id)

    # 2. Filtrowanie po dacie
    try:
        if date_from_str:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            query = query.filter(AccessLog.timestamp >= date_from)
        
        if date_to_str:
            # Ustawiamy koniec dnia na 23:59:59
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(AccessLog.timestamp <= date_to)
    except ValueError:
        return jsonify({"error": "Nieprawidłowy format daty. Użyj RRRR-MM-DD"}), 400

    # 3. Filtrowanie po pracowniku
    if employee_id:
        query = query.filter(AccessLog.employee_id == employee_id)

    # 4. Filtrowanie po typie wejścia
    
    if entry_type == 'access':
        query = query.filter(AccessLog.status == 'granted')
    elif entry_type == 'denied':
        query = query.filter(AccessLog.status == 'denied')

    # 5. Wykonanie zapytania i sortowanie od najnowszych
    results = query.order_by(AccessLog.timestamp.desc()).all()

    # 6. Mapowanie wyników do czytelnego formatu
    raport_list = []
    for log, emp in results:
        raport_list.append({
            "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "employee_id": log.employee_id,
            "full_name": f"{emp.first_name} {emp.last_name}",
            "email": emp.email,
            "status": log.status,
            
        })

    return jsonify({
        "status": "success",
        "count": len(raport_list),
        "filters": {
            "date_from": date_from_str,
            "date_to": date_to_str,
            "entry_type": entry_type,
            "employee_id": employee_id
        },
        "data": raport_list
    }), 200
    