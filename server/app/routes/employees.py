from flask import Blueprint, request, jsonify
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


@employees_bp.route('/verify', methods=['POST'])
def verify_employee():
    if not request.is_json:
        return jsonify({"error": "Wymagany format JSON"}), 400
    
    data = request.get_json()
    image_input_base64 = data.get('image')
    qr_code_data = data.get('qr_code') # zmieniłem nazwę zmiennej dla jasności

    # if not image_input_base64 or not qr_code_data:
    #     return jsonify({'error': 'Missing image or qr_code'}), 400
    
    # 1. Sprawdź, czy kod QR istnieje i jest aktywny w bazie
    qr_record = QRCredential.query.filter_by(qr_code_data=qr_code_data).first()
    
    # Sprawdzanie ważności (zakładam, że QRService robi też check daty, ale tu sprawdzamy czy istnieje rekord)
    if not qr_record or not QRService.validate_qr_code(qr_code_data): 
        return jsonify({
            "status": "denied",
            "message": "Nieprawidłowy lub wygasły kod QR."
        }), 401

    # # 2. Pobierz wzorzec twarzy właściciela tego kodu QR
    # # Zakładamy relację: QRCredential -> Employee -> FaceCredential
    # # LUB po prostu szukamy po employee_id
    # face_record = FaceCredential.query.filter_by(employee_id=qr_record.employee_id).first()
    
    # if not face_record:
    #     return jsonify({"error": "Brak wzorca twarzy dla tego pracownika"}), 500

    # # 3. Przetworzenie przesłanego zdjęcia
    # try:
    #     image_stream = FaceServices.handle_base64_image(image_input_base64)
    #     uploaded_encoding = FaceServices.get_encoding_from_image(image_stream)

    #     if uploaded_encoding is None:
    #         return jsonify({"status": "denied", "message": "Nie wykryto twarzy na zdjęciu"}), 400
    # except Exception as e:
    #     return jsonify({"error": f"Processing error: {str(e)}"}), 500

    # # 4. Porównanie KONKRETNEJ pary (Weryfikacja 1:1)
    # is_match = FaceServices.compare_faces(face_record.face_encoding, uploaded_encoding)
    
    # if is_match:
    #     # Pobieramy dane pracownika do powitania
    #     employee = Employee.query.get(qr_record.employee_id)
    #     return jsonify({
    #         "status": "granted",
    #         "message": f"Dostęp przyznany. Witaj, {employee.first_name}!",
    #         "employee_id": employee.id
    #     }), 200
    # else:
    #     return jsonify({
    #         "status": "denied",
    #         "message": "Twarz nie pasuje do właściciela kodu QR."
    #     }), 401
    employee = Employee.query.get(qr_record.employee_id)
    return jsonify({
        "status": "granted",
        "message": f"Dostęp przyznany. Witaj, {employee.first_name}!",
        "employee_id": employee.id
    }), 200
        
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