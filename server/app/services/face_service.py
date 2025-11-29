import face_recognition
import numpy as np
import io

class FaceServices:
    @staticmethod
    def get_face_ending_from_image(image_file):
        #konwersja na odpowiedni typ
        image=face_recognition.load_image_file(image_file)

        #locate face   
        face_locations=face_recognition.face_locations(image)

        if len(face_lostions) == 0:
            return None #nie znaleziono twarzy
        
        #wektor cech
        encoding = face_recognition.face_encodings(image, face_locations)[0]
        return encoding
    
    @staticmethod
    def compare_faces(known_encoding_bytes, unknown_encoding_np, tolerance=0.6):
        """
        Porównuje zapisaną twarz z nową.
        tolerance: im mniejsze, tym bardziej rygorystyczne (0.6 to standard).
        """
        # konwersaj an numpy, do fukcji muszą byc w takim type
        known_encoding = np.frombuffer(known_encoding_bytes, dtype=np.float64)
        
        # Oblicz dystans (wynik to lista bool, więc bierzemy [0])
        results = face_recognition.compare_faces([known_encoding], unknown_encoding_np, tolerance=tolerance)
        return results[0]
