from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.utils.db import db
from app.models.employee import Employee
from app.models.employee_face import FaceCredential
from app.services.face_service import FaceServices

# Tworzymy "Blueprint" - czyli moduł aplikacji
employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/register', methods=['POST'])
def register_emplyee():
    pass

@employees_bp.route('/verify', methods=['POST'])
def verify_emplyee():
    if not request.is_json:
        return jsonify({"error": "Zły format"}), 400
    data = request.get_json()
    qr_input=data.get('qr_coode') # zmianic nazwy odpwowiednie
    image_input= data.get('image')

    if not qr_input or not image_input:
        return jsonify({'error':'Bad type brakuje image albo qr'}), 400
    
    # validate qr TO-DO
    
    employee_id =1 #placeholder
    # jeli image w zlym typie dto dopiac
    employee_face_from_db= FaceCredential.query.filter(employee_id=employee_id).first()
    is_match= FaceServices.compare_faces(employee_face_from_db,image_input)
    
    if is_match:
        employee = Employee.query.get(employee_id)
        return jsonify({
            "status": "granted",
            "message": f"Dostęp przyznany. Witaj, {employee.first_name}!",
            "employee_id": employee.id
        }), 200
    else:
        # KOD QR SIĘ ZGADZA, ALE TWARZ NIE
        return jsonify({
            "status": "denied",
            "message": "Weryfikacja biometryczna nieudana. Twarz nie pasuje do kodu QR."
        }), 401