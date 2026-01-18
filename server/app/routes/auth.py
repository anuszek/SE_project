from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models.access_log import AccessLog
from app.utils.db import db
from app.models.employee import Employee
from app.models.employee_face import FaceCredential
from app.models.qr_code import QRCredential
from app.services.face_service import FaceServices
from app.services.qr_service import QRService

auth_bp= Blueprint('auth', __name__)

@auth_bp.route('/qr', methods=['POST'])
def verify_qr_only():
    """
    Verifies the provided QR code data.
    """
    if not request.is_json:
        return jsonify({"error": "JSON format required"}), 400
    
    data = request.get_json()
    qr_code_data = data.get('qr_code')

    if not qr_code_data:
        return jsonify({'error': 'QR code is required'}), 400
    
    qr_record = QRCredential.query.filter_by(qr_code_data=qr_code_data).first()
    
    if not qr_record or not QRService.validate_qr_code(qr_code_data):
        
        try:
            log = AccessLog(
                employee_id = "Bad QR", 
                status="denied",
                verification_method="QR"
            )
            db.session.add(log)
            db.session.commit()
        except Exception as log_error:
            print(f"[WARNING] Failed to log access: {log_error}")

        return jsonify({
            "status": "denied",
            "message": "Invalid or expired QR code."
        }), 401

    employee = Employee.query.get(qr_record.employee_id)
    
    if not employee:
        return jsonify({"error": "Data consistency error: no employee found for this code"}), 500

    return jsonify({
        "status": "valid",
        "message": "QR code is valid. Proceed to face verification.",
        "employee_id": employee.id,
        "first_name": employee.first_name 
    }), 200

@auth_bp.route('/face', methods=['POST'])
def verify_face_only():
    """
    Verifies the provided face image against stored face encodings.
    """
    if not request.is_json:
        return jsonify({"error": "JSON format required"}), 400
    
    data = request.get_json()
    image_input_base64 = data.get('image')
    employee_id = data.get('employee_id')

    if not image_input_base64 or not employee_id:
        return jsonify({'error': 'Image or employee ID is required'}), 400

    face_record = FaceCredential.query.filter_by(employee_id=employee_id).first()
    
    if not face_record:
        return jsonify({"error": "No face pattern found for this employee"}), 404

    try:
        image_stream = FaceServices.handle_base64_image(image_input_base64)
        
        uploaded_encoding = FaceServices.get_encoding_from_image(image_stream)

        uploaded_image_bytes = FaceServices.get_image_bytes(image_stream)

        if uploaded_encoding is None:
            try:
                log = AccessLog(
                    employee_id=employee_id,
                    status="denied",
                    verification_method="Face",
                    image = uploaded_image_bytes
                )
                db.session.add(log)
                db.session.commit()
            except Exception as log_error:
                print(f"[WARNING] Failed to log access denial: {log_error}")
                db.session.rollback()
        
            return jsonify({
                "status": "denied", 
                "message": "No face detected in the uploaded image"
            }), 400
            
    except Exception as e:
        return jsonify({"error": f"Image processing error: {str(e)}"}), 500

    
    is_match = False
    
    if FaceServices.compare_faces(face_record.face_encoding, uploaded_encoding):
        is_match = True
    
    elif face_record.face_encoding_addidional_1 is not None:
        if FaceServices.compare_faces(face_record.face_encoding_addidional_1, uploaded_encoding):
            is_match = True
            
    elif face_record.face_encoding_addidional_2 is not None:
        if FaceServices.compare_faces(face_record.face_encoding_addidional_2, uploaded_encoding):
            is_match = True

    if is_match:
        employee = Employee.query.get(employee_id)

        try:
            new_encoding_bytes = FaceServices.encoding_to_bytes(uploaded_encoding)
            
            update_msg = face_record.register_dynamic_entry(new_encoding_bytes, uploaded_image_bytes)
            print(f"[INFO] Face update: {update_msg}")
            
        except Exception as e:
            print(f"[WARNING] Failed to update dynamic face data: {e}")

        try:
            log = AccessLog(
                employee_id=employee_id,
                status="granted",
                verification_method="QR + Face"
            )
            db.session.add(log)
            db.session.commit()
        except Exception as log_error:
            print(f"[WARNING] Failed to log access: {log_error}")
            db.session.rollback()

        return jsonify({
            "status": "granted",
            "message": f"Access granted. Welcome, {employee.first_name}!",
            "employee_id": employee.id
        }), 200
    else:
        try:
            log = AccessLog(
                employee_id=employee_id,
                status="denied",
                verification_method="Face",
                image = uploaded_image_bytes
            )
            db.session.add(log)
            db.session.commit()
        except Exception as log_error:
            print(f"[WARNING] Failed to log access denial: {log_error}")
            db.session.rollback()

        return jsonify({
            "status": "denied",
            "message": "Biometric verification failed. Face does not match."
        }), 401