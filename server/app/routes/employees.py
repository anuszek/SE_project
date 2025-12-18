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

# Stałe walidacyjne
MIN_NAME_LEN = 3
MAX_EMAIL_LEN = 300

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/register', methods=['POST'])
def register_employee():
    """
    Rejestracja pracownika (BEZ QR).
    Tylko Dane Osobowe + Twarz.
    """
    if not request.is_json:
        return jsonify({"error": "Wymagany format JSON"}), 400
    
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    image_base64 = data.get('image')

    if not first_name or not last_name or not email or not image_base64:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Walidacja Regex
    # email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    # name_pattern = r"^[A-Za-z0-9_.'-]+$"

    # if (
    #     not re.match(email_pattern, email) or
    #     not re.match(name_pattern, first_name) or
    #     not re.match(name_pattern, last_name) or
    #     len(email) > MAX_EMAIL_LEN or
    #     len(first_name) < MIN_NAME_LEN or
    #     len(last_name) < MIN_NAME_LEN
    # ):
    #     return jsonify({"message": "Invalid data format"}), 400

    # Przetwarzanie zdjęcia
    try:
        image_stream = FaceServices.handle_base64_image(image_base64)
        if image_stream is None:
             return jsonify({"error": "Invalid Base64 image"}), 400

        face_encoding_np = FaceServices.get_encoding_from_image(image_stream)
        if face_encoding_np is None:
            return jsonify({"error": "No face detected"}), 400
        
        face_bytes = FaceServices.encoding_to_bytes(face_encoding_np)

    except Exception as e:
        return jsonify({"error": f"Image error: {str(e)}"}), 500

    # Zapis do bazy
    try:
        new_id = get_next_available_id()
        qr_code_data, expires_at = QRService.generate_credential()

        new_employee = Employee(
            id=new_id,   
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        db.session.add(new_employee)
        db.session.flush()

        new_face = FaceCredential(
            employee_id=new_employee.id, 
            face_encoding=face_bytes,
            face_image_path="memory"
        )
        db.session.add(new_face)
        db.session.flush()

        new_qr = QRCredential(
            employee_id=new_employee.id,
            qr_code_data=qr_code_data,
            expires_at=expires_at,
            is_active=True
        )
        db.session.add(new_qr)
        db.session.commit()

        return jsonify({
            "message": "Employee registered successfully",
            "employee_id": new_employee.id,
            "qr_code": qr_code_data,
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@employees_bp.route('/verify/qr', methods=['POST'])
def verify_qr_only():
    if not request.is_json:
        return jsonify({"error": "Wymagany format JSON"}), 400
    
    data = request.get_json()
    qr_code_data = data.get('qr_code')

    if not qr_code_data:
        return jsonify({'error': 'Brak kodu QR'}), 400
    
    # 1. Sprawdź, czy kod QR istnieje i jest aktywny
    qr_record = QRCredential.query.filter_by(qr_code_data=qr_code_data).first()
    
    if not qr_record or not QRService.validate_qr_code(qr_code_data):
        
        try:
            log = AccessLog(
                employee_id = "unknown", 
                status="denied",
                verification_method="qr"
            )
            db.session.add(log)
            db.session.commit()
        except Exception as log_error:
            print(f"[WARNING] Failed to log access: {log_error}")

        return jsonify({
            "status": "denied",
            "message": "Nieprawidłowy lub wygasły kod QR."
        }), 401

    # Pobieramy dane pracownika
    employee = Employee.query.get(qr_record.employee_id)
    
    if not employee:
        return jsonify({"error": "Błąd spójności danych: brak pracownika dla tego kodu"}), 500

    # Zwracamy sukces i ID pracownika, żeby frontend wiedział, kogo weryfikować twarzą
    try:
        log = AccessLog(
            employee_id=employee.id,
            status="granted",
            verification_method="qr"
        )
        db.session.add(log)
        db.session.commit()
    except Exception as log_error:
        print(f"[WARNING] Failed to log access: {log_error}")

    return jsonify({
        "status": "valid",
        "message": "Kod QR poprawny. Przejdź do weryfikacji twarzy.",
        "employee_id": employee.id,
        "first_name": employee.first_name 
    }), 200

@employees_bp.route('/verify/face', methods=['POST'])
def verify_face_only():
    if not request.is_json:
        return jsonify({"error": "Wymagany format JSON"}), 400
    
    data = request.get_json()
    image_input_base64 = data.get('image')
    employee_id = data.get('employee_id') # To musimy dostać z frontendu (wynik poprzedniego requestu)

    if not image_input_base64 or not employee_id:
        return jsonify({'error': 'Brak zdjęcia lub ID pracownika'}), 400

    # 1. Pobierz wzorzec twarzy dla podanego ID pracownika
    face_record = FaceCredential.query.filter_by(employee_id=employee_id).first()
    
    if not face_record:
        # Można tu zwrócić 404 lub 400, zależy od logiki (np. pracownik ma QR, ale nie ma skanu twarzy)
        return jsonify({"error": "Brak wzorca twarzy dla tego pracownika"}), 404

    # 2. Przetworzenie przesłanego zdjęcia
    try:
        image_stream = FaceServices.handle_base64_image(image_input_base64)
        uploaded_encoding = FaceServices.get_encoding_from_image(image_stream)

        if uploaded_encoding is None:
            return jsonify({
                "status": "denied", 
                "message": "Nie wykryto twarzy na przesłanym zdjęciu"
            }), 400
            
    except Exception as e:
        return jsonify({"error": f"Błąd przetwarzania obrazu: {str(e)}"}), 500

    
    is_match = FaceServices.compare_faces(face_record.face_encoding, uploaded_encoding)
    
    if is_match:
        employee = Employee.query.get(employee_id)

        try:
            log = AccessLog(
                employee_id=employee_id,
                status="granted",
                verification_method="face"
            )
            db.session.add(log)
            db.session.commit()
        except Exception as log_error:
            print(f"[WARNING] Failed to log access: {log_error}")

        return jsonify({
            "status": "granted",
            "message": f"Dostęp przyznany. Witaj, {employee.first_name}!",
            "employee_id": employee.id
        }), 200
    else:

        try:
            log = AccessLog(
                employee_id=employee_id,
                status="denied",
                verification_method="face"
            )
            db.session.add(log)
            db.session.commit()
        except Exception as log_error:
            print(f"[WARNING] Failed to log access denial: {log_error}")

        return jsonify({
            "status": "denied",
            "message": "Weryfikacja biometryczna nieudana. Twarz nie pasuje."
        }), 401
        
@employees_bp.route('/admin/clean_qr', methods=['POST', 'GET'])
def admin_clean_qr():
    """
    Wywołanie: usuń nieaktywne i odśwież wygasłe. Zabezpiecz w produkcji (token/IP).
    """

    # opcjonalnie: najpierw usuń nieaktywne, potem odśwież wygasłe
    deleted = delete_inactive_qr_codes()
    refreshed = refresh_expired_qr_codes()
    return {"deleted": deleted, "refreshed": refreshed}, 200

@employees_bp.route('/<int:employee_id>/qr', methods=['GET'])
def get_employee_qr_data(employee_id):
    """Zwraca QR code dla pracownika"""
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    qr = QRCredential.query.filter_by(employee_id=employee_id, is_active=True).first()
    if not qr:
        return jsonify({"error": "No active QR code"}), 404

    return jsonify({
        "qr_code": qr.qr_code_data,
        "expires_at": qr.expires_at.isoformat() if qr.expires_at else None
    }), 200

@employees_bp.route('/access-log/create', methods=['POST'])
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
@employees_bp.route('/admin/logs', methods=['GET'])
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
@employees_bp.route('/admin/stats', methods=['GET'])
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

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Usuwa pracownika i jego dane biometryczne"""
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({"message": "Employee deleted"}), 200

@employees_bp.route('/', methods=['GET'])
def get_all_employees():
    """Pobiera listę wszystkich pracowników"""
    employees = Employee.query.all()
    return jsonify([{
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "created_at": emp.created_at
    } for emp in employees]), 200
