from flask import Flask, request, jsonify, send_from_directory
import os
import base64
import numpy as np
import cv2
from PIL import Image
import io
import math
import tempfile
from encryption_utils import encrypt_image, decrypt_image, calculate_entropy, calculate_psnr, get_pixel_distribution

app = Flask(__name__, static_folder='static')

# Ensure upload directory exists
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/process-image', methods=['POST'])
def process_image():
    try:
        # Get parameters
        encryption_level = int(request.form.get('level', 2))
        encryption_key = float(request.form.get('key', 0.67))
        
        # Calculate iterations based on level (2 iterations per level)
        iterations = encryption_level * 2

        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file provided'})

        file = request.files['image']
        
        # Read image directly from memory
        in_memory_file = file.read()
        npimg = np.frombuffer(in_memory_file, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'success': False, 'message': 'Invalid image file'})

        # Convert to RGB and resize
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (256, 256))

        # Encryption & Decryption
        encrypted_img = encrypt_image(img, encryption_key, iterations)
        decrypted_img = decrypt_image(encrypted_img, encryption_key, iterations)

        # Metrics
        original_entropy = calculate_entropy(img)
        encrypted_entropy = calculate_entropy(encrypted_img)
        decrypted_entropy = calculate_entropy(decrypted_img)

        encrypted_psnr = calculate_psnr(img, encrypted_img)
        decrypted_psnr = calculate_psnr(img, decrypted_img)
        
        # Get pixel distribution (fixed to use the new function)
        pixel_distribution = get_pixel_distribution(encrypted_img)

        # Encode to base64
        def img_to_base64(image):
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.png', image)
            return 'data:image/png;base64,' + base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'success': True,
            'originalImage': img_to_base64(img),
            'encryptedImage': img_to_base64(encrypted_img),
            'decryptedImage': img_to_base64(decrypted_img),
            'metrics': {
                'originalEntropy': round(original_entropy, 2),
                'encryptedEntropy': round(encrypted_entropy, 2),
                'decryptedEntropy': round(decrypted_entropy, 2),
                'encryptedPSNR': round(encrypted_psnr, 2) if math.isfinite(encrypted_psnr) else None,
                'decryptedPSNR': round(decrypted_psnr, 2) if math.isfinite(decrypted_psnr) else None,
                'pixelDistribution': pixel_distribution
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)