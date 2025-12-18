import base64
import json
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.models.employee import Employee
from app.models.employee_face import FaceCredential
from app.models.qr_code import QRCredential
from app.models.access_log import AccessLog
from app.utils.db import db


class TestEmployeeRegistration:
    """Testy rejestracji pracownika"""

    def test_register_employee_success(self, client):
        """
        ✅ Rejestracja pracownika z zdjęciem.
        Powinno: dodać pracownika, wygenerować QR, zapisać encoding twarzy.
        """
        real_image_path = "../faces_test/face.jpg"
        
        with open(real_image_path, "rb") as img_file:
            file_content = img_file.read()
            base64_string = base64.b64encode(file_content).decode('utf-8')
            full_base64_string = f"data:image/jpeg;base64,{base64_string}"

        # Mock encoding (128-wymiarowy wektor)
        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc:
            mock_get_enc.return_value = fake_encoding
            
            payload = {
                'first_name': 'Jan',
                'last_name': 'Kowalski',
                'email': 'jan.kowalski@test.com',
                'department': 'IT',
                'position': 'Developer',
                'image': full_base64_string
            }
            
            response = client.post('/api/employees/register', json=payload)

        assert response.status_code == 201
        json_data = response.get_json()
        
        assert json_data['success'] is True
        assert 'employee_id' in json_data
        assert 'qr_code' in json_data
        assert json_data['first_name'] == 'Jan'
        assert json_data['last_name'] == 'Kowalski'

        # Sprawdź czy pracownik jest w bazie
        employee = Employee.query.filter_by(email='jan.kowalski@test.com').first()
        assert employee is not None
        assert employee.first_name == 'Jan'

        # Sprawdź czy FaceCredential został zapisany
        face_cred = FaceCredential.query.filter_by(employee_id=employee.id).first()
        assert face_cred is not None
        assert face_cred.face_encoding is not None

        # Sprawdź czy QR został wygenerowany
        qr_cred = QRCredential.query.filter_by(employee_id=employee.id).first()
        assert qr_cred is not None

    def test_register_employee_missing_fields(self, client):
        """
        ❌ Rejestracja bez wymaganych pól.
        Powinno: zwrócić 400 error.
        """
        payload = {
            'first_name': 'Jan',
            # Brakuje: last_name, email, image
        }
        
        response = client.post('/api/employees/register', json=payload)

        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data or 'message' in json_data

    def test_register_employee_no_image(self, client):
        """
        ❌ Rejestracja bez zdjęcia.
        Powinno: zwrócić 400 error.
        """
        payload = {
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan@test.com',
            # Brakuje: image
        }
        
        response = client.post('/api/employees/register', json=payload)

        assert response.status_code == 400

    def test_register_duplicate_email(self, client):
        """
        ❌ Rejestracja z duplikowanym emailem.
        Powinno: zwrócić 409 Conflict.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            payload = {
                'first_name': 'Jan',
                'last_name': 'Kowalski',
                'email': 'duplicate@test.com',
                'image': full_base64
            }
            
            # Pierwsza rejestracja - OK
            response1 = client.post('/api/employees/register', json=payload)
            assert response1.status_code == 201
            
            # Druga rejestracja z tym samym emailem - ERROR
            response2 = client.post('/api/employees/register', json=payload)
            assert response2.status_code == 409


class TestQRVerification:
    """Testy weryfikacji QR code"""

    def test_verify_qr_success(self, client):
        """
        ✅ Weryfikacja poprawnego QR code.
        Powinno: zwrócić employee_id i status='valid'.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            # 1️⃣ REJESTRACJA
            reg_payload = {
                'first_name': 'Anna',
                'last_name': 'Nowak',
                'email': 'anna.nowak@test.com',
                'image': full_base64
            }
            reg_resp = client.post('/api/employees/register', json=reg_payload)
            assert reg_resp.status_code == 201
            
            qr_code = reg_resp.get_json()['qr_code']
            employee_id = reg_resp.get_json()['employee_id']

        # 2️⃣ WERYFIKACJA QR
        verify_qr_payload = {'qr_code': qr_code}
        response = client.post('/api/employees/verify/qr', json=verify_qr_payload)

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'valid'
        assert json_data['employee_id'] == employee_id
        assert json_data['first_name'] == 'Anna'

    def test_verify_qr_missing_code(self, client):
        """
        ❌ Weryfikacja QR bez kodu.
        Powinno: zwrócić 400 error.
        """
        response = client.post('/api/employees/verify/qr', json={})

        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data

    def test_verify_qr_invalid_code(self, client):
        """
        ❌ Weryfikacja nieistniejącego QR code.
        Powinno: zwrócić 404 error.
        """
        payload = {'qr_code': 'INVALID-QR-CODE-12345'}
        response = client.post('/api/employees/verify/qr', json=payload)

        assert response.status_code == 404
        json_data = response.get_json()
        assert 'error' in json_data

    def test_verify_qr_creates_access_log(self, client):
        """
        ✅ Weryfikacja QR zapisuje log dostępu.
        Powinno: dodać rekord do AccessLog.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            # Rejestracja
            reg_payload = {
                'first_name': 'Maria',
                'last_name': 'Kowalczyk',
                'email': 'maria@test.com',
                'image': full_base64
            }
            reg_resp = client.post('/api/employees/register', json=reg_payload)
            qr_code = reg_resp.get_json()['qr_code']
            employee_id = reg_resp.get_json()['employee_id']

        # Weryfikacja QR
        verify_payload = {'qr_code': qr_code}
        response = client.post('/api/employees/verify/qr', json=verify_payload)
        assert response.status_code == 200

        # Sprawdź AccessLog
        log = AccessLog.query.filter_by(
            employee_id=employee_id,
            verification_method='qr'
        ).first()
        assert log is not None
        assert log.status == 'granted'


class TestFaceVerification:
    """Testy weryfikacji twarzy"""

    def test_verify_face_success(self, client):
        """
        ✅ Pełny proces: Rejestracja -> QR -> Face verification.
        Powinno: zwrócić status='granted'.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
             patch('app.services.face_service.FaceServices.compare_faces') as mock_compare:
            
            mock_get_enc.return_value = fake_encoding
            mock_compare.return_value = True  # ✅ Twarze się zgadzają
            
            # 1️⃣ REJESTRACJA
            reg_payload = {
                'first_name': 'Piotr',
                'last_name': 'Lewandowski',
                'email': 'piotr@test.com',
                'image': full_base64
            }
            reg_resp = client.post('/api/employees/register', json=reg_payload)
            assert reg_resp.status_code == 201
            employee_id = reg_resp.get_json()['employee_id']
            qr_code = reg_resp.get_json()['qr_code']

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
             patch('app.services.face_service.FaceServices.compare_faces') as mock_compare:
            
            mock_get_enc.return_value = fake_encoding
            mock_compare.return_value = True
            
            # 2️⃣ WERYFIKACJA QR
            verify_qr_payload = {'qr_code': qr_code}
            qr_resp = client.post('/api/employees/verify/qr', json=verify_qr_payload)
            assert qr_resp.status_code == 200

            # 3️⃣ WERYFIKACJA FACE
            verify_face_payload = {
                'employee_id': employee_id,
                'image': full_base64
            }
            face_resp = client.post('/api/employees/verify/face', json=verify_face_payload)

        assert face_resp.status_code == 200
        json_data = face_resp.get_json()
        assert json_data['status'] == 'granted'
        assert 'Dostęp przyznany' in json_data['message']

    def test_verify_face_no_match(self, client):
        """
        ❌ Weryfikacja twarzy - twarz się NIE zgadza.
        Powinno: zwrócić status='denied' i 401.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc:
            mock_get_enc.return_value = fake_encoding
            
            # Rejestracja
            reg_payload = {
                'first_name': 'Tomasz',
                'last_name': 'Szymański',
                'email': 'tomasz@test.com',
                'image': full_base64
            }
            reg_resp = client.post('/api/employees/register', json=reg_payload)
            employee_id = reg_resp.get_json()['employee_id']

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
             patch('app.services.face_service.FaceServices.compare_faces') as mock_compare:
            
            mock_get_enc.return_value = fake_encoding
            mock_compare.return_value = False  # ❌ Twarze się NIE zgadzają
            
            # Weryfikacja FACE - powinno być DENIED
            verify_face_payload = {
                'employee_id': employee_id,
                'image': full_base64
            }
            response = client.post('/api/employees/verify/face', json=verify_face_payload)

        assert response.status_code == 401
        json_data = response.get_json()
        assert json_data['status'] == 'denied'
        assert 'nieudana' in json_data['message'].lower() or 'not recognized' in json_data['message'].lower()

    def test_verify_face_missing_employee_id(self, client):
        """
        ❌ Weryfikacja twarzy bez employee_id.
        Powinno: zwrócić 400 error.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        payload = {
            'image': full_base64
            # Brakuje: employee_id
        }
        
        response = client.post('/api/employees/verify/face', json=payload)

        assert response.status_code == 400

    def test_verify_face_missing_image(self, client):
        """
        ❌ Weryfikacja twarzy bez zdjęcia.
        Powinno: zwrócić 400 error.
        """
        payload = {
            'employee_id': 1
            # Brakuje: image
        }
        
        response = client.post('/api/employees/verify/face', json=payload)

        assert response.status_code == 400

    def test_verify_face_creates_access_log_granted(self, client):
        """
        ✅ Weryfikacja twarzy - SUCCESS, zapisuje log.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            reg_payload = {
                'first_name': 'Katarzyna',
                'last_name': 'Wójcik',
                'email': 'katarzyna@test.com',
                'image': full_base64
            }
            reg_resp = client.post('/api/employees/register', json=reg_payload)
            employee_id = reg_resp.get_json()['employee_id']

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
             patch('app.services.face_service.FaceServices.compare_faces') as mock_compare:
            
            mock_get_enc.return_value = fake_encoding
            mock_compare.return_value = True
            
            verify_payload = {
                'employee_id': employee_id,
                'image': full_base64
            }
            response = client.post('/api/employees/verify/face', json=verify_payload)
            assert response.status_code == 200

        # Sprawdź AccessLog
        log = AccessLog.query.filter_by(
            employee_id=employee_id,
            verification_method='face',
            status='granted'
        ).first()
        assert log is not None

    def test_verify_face_creates_access_log_denied(self, client):
        """
        ✅ Weryfikacja twarzy - FAIL, zapisuje log z status='denied'.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            reg_payload = {
                'first_name': 'Magdalena',
                'last_name': 'Zalewska',
                'email': 'magdalena@test.com',
                'image': full_base64
            }
            reg_resp = client.post('/api/employees/register', json=reg_payload)
            employee_id = reg_resp.get_json()['employee_id']

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock_get_enc, \
             patch('app.services.face_service.FaceServices.compare_faces') as mock_compare:
            
            mock_get_enc.return_value = fake_encoding
            mock_compare.return_value = False  # ❌ ODMOWA
            
            verify_payload = {
                'employee_id': employee_id,
                'image': full_base64
            }
            response = client.post('/api/employees/verify/face', json=verify_payload)
            assert response.status_code == 401

        # Sprawdź AccessLog
        log = AccessLog.query.filter_by(
            employee_id=employee_id,
            verification_method='face',
            status='denied'
        ).first()
        assert log is not None


class TestAccessLogEndpoints:
    """Testy endpointów dostępu do logów"""

    def test_get_access_logs(self, client):
        """
        ✅ Pobieranie logów dostępu.
        Powinno: zwrócić listę wszystkich logów.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            # Rejestracja 2 pracowników
            for i in range(2):
                payload = {
                    'first_name': f'Pracownik{i}',
                    'last_name': f'Test{i}',
                    'email': f'pracownik{i}@test.com',
                    'image': full_base64
                }
                client.post('/api/employees/register', json=payload)

        # Pobierz logi
        response = client.get('/api/employees/admin/logs')

        assert response.status_code == 200
        json_data = response.get_json()
        assert 'logs' in json_data or isinstance(json_data, list)

    def test_get_admin_stats(self, client):
        """
        ✅ Pobieranie statystyk dashboardu.
        Powinno: zwrócić total_employees, today_access, itp.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            payload = {
                'first_name': 'StatTest',
                'last_name': 'Worker',
                'email': 'stat@test.com',
                'image': full_base64
            }
            client.post('/api/employees/register', json=payload)

        response = client.get('/api/employees/admin/stats')

        assert response.status_code == 200
        json_data = response.get_json()
        assert 'total_employees' in json_data
        assert 'today_access' in json_data


class TestGetAllEmployees:
    """Testy pobierania listy pracowników"""

    def test_get_all_employees(self, client):
        """
        ✅ Pobieranie listy wszystkich pracowników.
        """
        real_image_path = "../faces_test/face.jpg"
        with open(real_image_path, "rb") as img_file:
            base64_str = base64.b64encode(img_file.read()).decode('utf-8')
            full_base64 = f"data:image/jpeg;base64,{base64_str}"

        fake_encoding = np.zeros(128, dtype=np.float64)

        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            # Dodaj 3 pracowników
            for i in range(3):
                payload = {
                    'first_name': f'Emp{i}',
                    'last_name': f'Ployee{i}',
                    'email': f'emp{i}@test.com',
                    'image': full_base64
                }
                client.post('/api/employees/register', json=payload)

        response = client.get('/api/employees')

        assert response.status_code == 200
        json_data = response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) >= 3

    def test_get_all_employees_empty(self, client):
        """
        ✅ Pobieranie listy pracowników, gdy baza jest pusta.
        """
        response = client.get('/api/employees')

        assert response.status_code == 200
        json_data = response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) == 0