from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.utils.db import db
from app.models.employee import Employee
from app.models.employee_face import FaceCredential
from app.models.qr_code import QRCredential
from app.services.face_service import FaceServices
from app.services.qr_service import QRService
from app.utils.helpers import  get_next_available_id

MIN_NAME_LEN = 3
MAX_EMAIL_LEN = 300

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/register', methods=['POST'])
def register_employee():
    """
    Registers a new employee with biometric data.
    """
    if not request.is_json:
        return jsonify({"error": "JSON format required"}), 400
    
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    image_base64 = data.get('image')

    if not first_name or not last_name or not email or not image_base64:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # --- PRZETWARZANIE ZDJĘCIA ---
    try:
        # 1. Konwersja Base64 -> Stream
        image_stream = FaceServices.handle_base64_image(image_base64)
        if image_stream is None:
             return jsonify({"error": "Invalid Base64 image"}), 400

        # 2. Wykrywanie twarzy i obliczanie encodingu
        face_encoding_np = FaceServices.get_encoding_from_image(image_stream)
        if face_encoding_np is None:
            return jsonify({"error": "No face detected"}), 400
        
        # 3. Konwersja Encodingu na bajty (do bazy)
        face_bytes = FaceServices.encoding_to_bytes(face_encoding_np)

        # 4. Pobranie surowych bajtów zdjęcia (do bazy - kolumna face_image)
        # Metoda get_image_bytes resetuje wskaźnik pliku, więc jest bezpieczna
        image_blob = FaceServices.get_image_bytes(image_stream)

    except Exception as e:
        return jsonify({"error": f"Image processing error: {str(e)}"}), 500

    # Database operations
    try:
        new_id = get_next_available_id()
        qr_code_data, expires_at = QRService.generate_credential()

        # 1. Pracownik
        new_employee = Employee(
            id=new_id,   
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        db.session.add(new_employee)
        db.session.flush() # Żeby uzyskać ID pracownika

        # 2. Dane Biometryczne (Encoding + Zdjęcie)
        new_face = FaceCredential(
            employee_id=new_employee.id, 
            face_encoding=face_bytes,  # Encoding (matematyczny opis)
            face_image=image_blob      # Fizyczne zdjęcie (bajty)
        )
        db.session.add(new_face)
        db.session.flush()

        # 3. Kod QR
        new_qr = QRCredential(
            employee_id=new_employee.id,
            qr_code_data=qr_code_data,
            expires_at=expires_at,
            is_active=True
        )
        db.session.add(new_qr)
        
        # Zatwierdzenie wszystkiego
        db.session.commit()

        return jsonify({
            "message": "Employee registered successfully",
            "employee_id": new_employee.id,
            "qr_code": new_qr.qr_code_data,
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@employees_bp.route('/all', methods=['GET'])
def get_all_employees():
    """Retrieves a list of all employees with their QR code info."""
    employees = Employee.query.all()
    return jsonify([{
        "id": emp.id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "created_at": emp.created_at,
        "qr_credential": {
            "qr_code": emp.qr_code.qr_code_data if emp.qr_code else None,
            "expires_at": emp.qr_code.expires_at if emp.qr_code else None,
            "is_active": emp.qr_code.is_active if emp.qr_code else None
        } if emp.qr_code else None
    } for emp in employees]), 200

@employees_bp.route('/<int:employee_id>/delete', methods=['DELETE'])
def delete_employee(employee_id):
    """Deletes an employee and their biometric data."""
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    db.session.delete(employee)
    db.session.commit()
    return jsonify({"message": "Employee deleted"}), 200

@employees_bp.route('/<int:employee_id>/generate_new_qr_code', methods=['POST'])
def generate_new_qr_code(employee_id):
    """Generates a completely new QR code for the employee, replacing the old one."""

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    try:
        new_code, new_exp = QRService.generate_credential()
        
        qr = employee.qr_code
        qr.qr_code_data = new_code
        qr.expires_at = new_exp
        qr.is_active = True
        
        db.session.commit()
        
        return jsonify({
            "message": "New QR code generated successfully",
            "qr_code": new_code,
            "expires_at": new_exp.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@employees_bp.route('/<int:employee_id>/switch_qr_state', methods=['POST'])
def switch_qr_state(employee_id):
    """Activates or deactivates the employee's QR code."""
    
    data = request.get_json()
    is_active = data.get('is_active')
    
    if is_active is None:
        return jsonify({"error": "Missing 'is_active' field"}), 400

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    try:
        employee.qr_code.is_active = is_active
        db.session.commit()
        return jsonify({
            "message": f"QR code is now {'active' if is_active else 'inactive'}",
            "is_active": is_active
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@employees_bp.route('/<int:employee_id>/modify_employee', methods=['PUT'])
def modify_employee(employee_id):
    """Modifies employee data."""
    if not request.is_json:
        return jsonify({"error": "JSON format required"}), 400
    
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')

    if not first_name or not last_name or not email:
        return jsonify({'error': 'Missing required fields'}), 400

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    try:
        employee.first_name = first_name
        employee.last_name = last_name
        employee.email = email
        db.session.commit()
        return jsonify({"message": "Employee modified successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500