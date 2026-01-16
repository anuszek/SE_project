import face_recognition
import numpy as np
import base64  
import io      

class FaceServices:
    
    @staticmethod
    def get_encoding_from_image(file_storage):
        """Retrieves file, finds face and returns encoding."""
        # Load the image
        image = face_recognition.load_image_file(file_storage)
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            return None 
        
        # Return encoding of the first face
        return face_recognition.face_encodings(image, face_locations)[0]

    @staticmethod
    def handle_base64_image(base64_string):
        """
        Converts a Base64 string to a file-like object.
        This is probably the missing method!
        """
        # Remove "data:image/jpeg;base64," header if present
        if "," in base64_string:
            header, encoded = base64_string.split(",", 1)
        else:
            encoded = base64_string

        try:
            # Decode text to bytes
            image_data = base64.b64decode(encoded)
            # Return as "in-memory file"
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