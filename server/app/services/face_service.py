import face_recognition
import numpy as np
import base64  # <--- WAŻNE
import io      # <--- WAŻNE

class FaceServices:
    
    @staticmethod
    def get_encoding_from_image(file_storage):
        """Pobiera plik, znajduje twarz i zwraca encoding."""
        # Wczytujemy obrazek
        image = face_recognition.load_image_file(file_storage)
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return None 
        
        # Zwracamy encoding pierwszej twarzy
        return face_recognition.face_encodings(image, face_locations)[0]

    @staticmethod
    def handle_base64_image(base64_string):
        """
        Zamienia string Base64 na obiekt plikopodobny.
        To jest ta metoda, której prawdopodobnie brakuje!
        """
        # Usuwamy nagłówek "data:image/jpeg;base64," jeśli istnieje
        if "," in base64_string:
            header, encoded = base64_string.split(",", 1)
        else:
            encoded = base64_string

        try:
            # Dekodujemy tekst na bajty
            image_data = base64.b64decode(encoded)
            # Zwracamy jako "plik w pamięci"
            return io.BytesIO(image_data)
        except Exception:
            return None

    @staticmethod
    def encoding_to_bytes(encoding_np):
        return encoding_np.tobytes()

    @staticmethod
    def compare_faces(known_encoding_bytes, unknown_encoding_np, tolerance=0.6):
        known_encoding = np.frombuffer(known_encoding_bytes, dtype=np.float64)
        results = face_recognition.compare_faces([known_encoding], unknown_encoding_np, tolerance=tolerance)
        return results[0]