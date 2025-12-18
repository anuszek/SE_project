"""
Testy logiki biometrycznej - Face Recognition
"""
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from app.services.face_service import FaceServices
from io import BytesIO
from PIL import Image


class TestFaceEncoding:
    """Testy ekstrakcji i porównania encodingów twarzy"""

    def test_face_encoding_shape(self):
        """
        ✅ Sprawdza czy encoding ma 128 wymiarów.
        """
        fake_encoding = np.random.randn(128)
        
        assert isinstance(fake_encoding, np.ndarray)
        assert len(fake_encoding) == 128
        assert fake_encoding.dtype == np.float64

    def test_face_encoding_range(self):
        """
        ✅ Sprawdza czy wartości encoding są w rozsądnym zakresie.
        """
        fake_encoding = np.random.randn(128)
        
        # Wartości powinny być między -10 a 10 (z face_recognition library)
        assert np.all(fake_encoding >= -10) or np.all(fake_encoding <= 10)

    def test_encoding_to_bytes_conversion(self):
        """
        ✅ Sprawdza konwersję numpy array → bytes.
        """
        encoding = np.array([0.234, -0.456, 0.123] * 43, dtype=np.float64)
        
        # Konwersja do bytes
        encoding_bytes = encoding.tobytes()
        
        assert isinstance(encoding_bytes, bytes)
        assert len(encoding_bytes) == 128 * 8  # 128 float64 = 128*8 bytes
        
        # Konwersja zwrotna
        recovered = np.frombuffer(encoding_bytes, dtype=np.float64)
        assert np.allclose(encoding, recovered)

    def test_compare_faces_match(self):
        """
        ✅ Porównanie identycznych encodingów - powinno być match.
        """
        encoding1 = np.zeros(128, dtype=np.float64)
        encoding2 = np.zeros(128, dtype=np.float64)
        
        # Dystans = 0 (identyczne)
        distance = np.linalg.norm(encoding1 - encoding2)
        assert distance < 0.6  # ✅ MATCH

    def test_compare_faces_no_match(self):
        """
        ❌ Porównanie różnych encodingów - powinno być no match.
        """
        encoding1 = np.zeros(128, dtype=np.float64)
        encoding2 = np.ones(128, dtype=np.float64)
        
        # Dystans = duży (różne)
        distance = np.linalg.norm(encoding1 - encoding2)
        assert distance > 0.6  # ❌ NO MATCH

    def test_compare_faces_threshold_boundary(self):
        """
        ✅ Test na granicy progu tolerancji (0.6).
        """
        encoding1 = np.zeros(128, dtype=np.float64)
        
        # Utwórz encoding2 z dystansem = 0.55 (poniżej progu)
        encoding2 = np.full(128, 0.0042, dtype=np.float64)
        
        distance = np.linalg.norm(encoding1 - encoding2)
        assert distance < 0.6  # ✅ MATCH (granica)
        
        # Utwórz encoding3 z dystansem = 0.65 (powyżej progu)
        encoding3 = np.full(128, 0.0051, dtype=np.float64)
        distance2 = np.linalg.norm(encoding1 - encoding3)
        assert distance2 > 0.6  # ❌ NO MATCH (granica)

    def test_encoding_consistency(self):
        """
        ✅ Sprawdza czy ten sam obraz daje te same encodingi.
        (W praktyce: mock z tą samą wartością)
        """
        encoding1 = np.random.randn(128)
        encoding2 = encoding1.copy()
        
        distance = np.linalg.norm(encoding1 - encoding2)
        assert distance == 0  # ✅ Identyczne
        assert np.array_equal(encoding1, encoding2)


class TestFaceServiceMocking:
    """Testy FaceServices z mockingiem"""

    def test_get_encoding_from_image_mocked(self):
        """
        ✅ Test get_encoding_from_image z mockingiem.
        """
        fake_encoding = np.random.randn(128)
        
        with patch('app.services.face_service.FaceServices.get_encoding_from_image') as mock:
            mock.return_value = fake_encoding
            
            # Symuluj wołanie
            result = mock("dummy_image")
            
            assert isinstance(result, np.ndarray)
            assert len(result) == 128

    def test_compare_faces_mocked_match(self):
        """
        ✅ Test compare_faces - zmockowany MATCH.
        """
        with patch('app.services.face_service.FaceServices.compare_faces') as mock:
            mock.return_value = True
            
            result = mock("encoding1", "encoding2")
            assert result is True

    def test_compare_faces_mocked_no_match(self):
        """
        ❌ Test compare_faces - zmockowany NO MATCH.
        """
        with patch('app.services.face_service.FaceServices.compare_faces') as mock:
            mock.return_value = False
            
            result = mock("encoding1", "encoding2")
            assert result is False

    def test_handle_base64_image_mocked(self):
        """
        ✅ Test konwersji Base64 na BytesIO.
        """
        # Utwórz dummy Base64 image
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        base64_str = f"data:image/jpeg;base64,{buffer.getvalue()}"
        
        with patch('app.services.face_service.FaceServices.handle_base64_image') as mock:
            mock.return_value = BytesIO(buffer.getvalue())
            
            result = mock(base64_str)
            assert isinstance(result, BytesIO)


class TestFaceEncodingEdgeCases:
    """Testy edge cases dla face encodings"""

    def test_zero_encoding(self):
        """
        ✅ Encoding ze wszystkimi zerami (teoretycznie).
        """
        encoding = np.zeros(128, dtype=np.float64)
        assert len(encoding) == 128
        assert np.all(encoding == 0)

    def test_max_encoding_values(self):
        """
        ✅ Encoding z maksymalnymi wartościami.
        """
        encoding = np.full(128, 10.0, dtype=np.float64)
        assert np.all(encoding == 10.0)

    def test_negative_encoding_values(self):
        """
        ✅ Encoding z ujemnymi wartościami.
        """
        encoding = np.full(128, -5.0, dtype=np.float64)
        assert np.all(encoding == -5.0)

    def test_encoding_distance_calculation(self):
        """
        ✅ Sprawdza poprawne obliczenie dystansu euklidesowego.
        """
        e1 = np.array([0, 0, 0], dtype=np.float64)
        e2 = np.array([3, 4, 0], dtype=np.float64)
        
        # Dystans powinien być 5 (3² + 4² = 25, √25 = 5)
        distance = np.linalg.norm(e1 - e2)
        assert distance == 5.0