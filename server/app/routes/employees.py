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

@employees_bp.route('/<int:employee_id>/delete', methods=['DELETE'])
def delete_employee(employee_id):
    """Usuwa pracownika i jego dane biometryczne"""
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({"message": "Employee deleted"}), 200

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

@employees_bp.route('/all', methods=['GET'])
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
