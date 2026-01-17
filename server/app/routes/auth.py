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

@auth_bp.route('/face', methods=['POST'])
def verify_face_only():
    if not request.is_json:
        return jsonify({"error": "Wymagany format JSON"}), 400
    
    data = request.get_json()
    image_input_base64 = data.get('image')
    employee_id = data.get('employee_id')

    if not image_input_base64 or not employee_id:
        return jsonify({'error': 'Brak zdjęcia lub ID pracownika'}), 400

    # 1. Pobierz wzorzec twarzy dla podanego ID pracownika
    face_record = FaceCredential.query.filter_by(employee_id=employee_id).first()
    
    if not face_record:
        return jsonify({"error": "Brak wzorca twarzy dla tego pracownika"}), 404

    # 2. Przetworzenie przesłanego zdjęcia
    try:
        image_stream = FaceServices.handle_base64_image(image_input_base64)
        
        # Obliczamy encoding z przesłanego zdjęcia
        uploaded_encoding = FaceServices.get_encoding_from_image(image_stream)

        if uploaded_encoding is None:
            return jsonify({
                "status": "denied", 
                "message": "Nie wykryto twarzy na przesłanym zdjęciu"
            }), 400
        
        # Pobieramy też surowe bajty zdjęcia (potrzebne do zapisu w bazie, jeśli weryfikacja się uda)
        uploaded_image_bytes = FaceServices.get_image_bytes(image_stream)
            
    except Exception as e:
        return jsonify({"error": f"Błąd przetwarzania obrazu: {str(e)}"}), 500

    
    # 3. Weryfikacja wieloetapowa (Główne -> Slot 1 -> Slot 2)
    is_match = False
    
    # A. Sprawdź zdjęcie GŁÓWNE
    if FaceServices.compare_faces(face_record.face_encoding, uploaded_encoding):
        is_match = True
    
    # B. Jeśli nie pasuje, sprawdź SLOT 1 (jeśli istnieje)
    elif face_record.face_encoding_addidional_1 is not None:
        if FaceServices.compare_faces(face_record.face_encoding_addidional_1, uploaded_encoding):
            is_match = True
            
    # C. Jeśli dalej nie pasuje, sprawdź SLOT 2 (jeśli istnieje)
    elif face_record.face_encoding_addidional_2 is not None:
        if FaceServices.compare_faces(face_record.face_encoding_addidional_2, uploaded_encoding):
            is_match = True

    # 4. Obsługa wyniku
    if is_match:
        employee = Employee.query.get(employee_id)

        # --- DYNAMICZNA AKTUALIZACJA TWARZY ---
        try:
            # Konwertujemy encoding na bajty dla bazy
            new_encoding_bytes = FaceServices.encoding_to_bytes(uploaded_encoding)
            
            # Wywołujemy metodę modelu (logika: puste miejsce lub najstarsze)
            update_msg = face_record.register_dynamic_entry(new_encoding_bytes, uploaded_image_bytes)
            print(f"[INFO] Face update: {update_msg}")
            
        except Exception as e:
            print(f"[WARNING] Failed to update dynamic face data: {e}")
            # Nie przerywamy logowania, bo pracownik został rozpoznany

        # Logowanie wejścia
        try:
            log = AccessLog(
                employee_id=employee_id,
                status="granted",
                verification_method="face"
            )
            db.session.add(log)
            db.session.commit() # Commit zatwierdzi też zmiany w face_credential
        except Exception as log_error:
            print(f"[WARNING] Failed to log access: {log_error}")
            db.session.rollback()

        return jsonify({
            "status": "granted",
            "message": f"Dostęp przyznany. Witaj, {employee.first_name}!",
            "employee_id": employee.id
        }), 200
    else:
        # Logowanie odmowy
        try:
            log = AccessLog(
                employee_id=employee_id,
                status="denied",
                verification_method="face",
                image = image_input_base64
            )
            db.session.add(log)
            db.session.commit()
        except Exception as log_error:
            print(f"[WARNING] Failed to log access denial: {log_error}")

        return jsonify({
            "status": "denied",
            "message": "Weryfikacja biometryczna nieudana. Twarz nie pasuje."
        }), 401