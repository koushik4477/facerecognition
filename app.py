import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Load known faces from the 'known' folder
known_face_encodings = []
known_face_names = []
known_images_path = "known"  # Folder where known images are stored

# Load known images
for filename in os.listdir(known_images_path):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join(known_images_path, filename)
        image = face_recognition.load_image_file(image_path)
        
        # Get face locations
        face_locations = face_recognition.face_locations(image)
        
        # Ensure we have faces detected
        if face_locations:
            # Compute face encodings for all detected faces
            encodings = face_recognition.face_encodings(image, face_locations)
            for encoding in encodings:
                known_face_encodings.append(encoding)
                known_face_names.append(filename.rsplit(".", 1)[0])  # Store name without extension

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify_face', methods=['POST'])
def verify_face():
    try:
        # Check if there are known faces registered
        if not known_face_encodings:
            return jsonify({"error": "No known faces have been registered."})

        data = request.get_json()
        img_data = data['image']
        
        # Decode the base64 image string
        img_bytes = base64.b64decode(img_data)
        pil_image = Image.open(BytesIO(img_bytes)).convert("RGB")
        image = np.array(pil_image)
        
        # Convert the image to RGB (already in RGB from PIL, no conversion needed)
        rgb_image = image  # Directly use the RGB image

        # Get face locations in the uploaded image
        face_locations = face_recognition.face_locations(rgb_image)

        if not face_locations:
            return jsonify({"result": "No faces detected"})

        # Compute the face encodings for the detected faces
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        if not face_encodings:
            return jsonify({"result": "Unable to encode face(s)"})

        results = []
        for i, face_encoding in enumerate(face_encodings):
            # Calculate distances from known faces
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            
            # Use a threshold of 0.6 for face recognition
            if distances[best_match_index] < 0.6:
                name = known_face_names[best_match_index]
                distance = float(distances[best_match_index])
            else:
                name = "Unknown"
                distance = float(distances[best_match_index])
            
            # Return face location, name, and distance
            results.append({
               
                "name": name,
                
            })

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
