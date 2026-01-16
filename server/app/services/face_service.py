import face_recognition
import numpy as np
import base64
import io

class FaceServices:
    
    @staticmethod
    def get_encoding_from_image(file_storage):
        """Pobiera plik, znajduje twarz i zwraca encoding (numpy array)."""
        # Load image file
        image = face_recognition.load_image_file(file_storage)
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return None 
        
        # Zwracamy encoding pierwszej twarzy
        return face_recognition.face_encodings(image, face_locations)[0]

    @staticmethod
    def handle_base64_image(base64_string):
        """Zamienia string Base64 na obiekt plikopodobny (BytesIO)."""
        if "," in base64_string:
            header, encoded = base64_string.split(",", 1)
        else:
            encoded = base64_string

        try:
            image_data = base64.b64decode(encoded)
            return io.BytesIO(image_data)
        except Exception:
            return None

    @staticmethod
    def encoding_to_bytes(encoding_np):
        """Konwertuje numpy array na bajty (do zapisu w bazie)."""
        return encoding_np.tobytes()

    @staticmethod
    def get_image_bytes(file_storage):
        """
        Pobiera surowe bajty z pliku zdjęcia.
        Kluczowe dla zapisu BLOB w bazie danych.
        """
        file_storage.seek(0)
        data = file_storage.read()
        file_storage.seek(0) # Reset wskaźnika, aby można było użyć pliku ponownie
        return data

    @staticmethod
    def compare_faces(known_encoding_bytes, unknown_encoding_np, tolerance=0.6):
        known_encoding = np.frombuffer(known_encoding_bytes, dtype=np.float64)
        results = face_recognition.compare_faces([known_encoding], unknown_encoding_np, tolerance=tolerance)
        return results[0]