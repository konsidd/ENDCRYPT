# ENDCRYPT Image Encryption using Arnold Cat Map and Chaotic Maps
How It Works
1. Arnold Cat Map is applied to scramble the pixel positions of the image.
2. A chaotic sequence is generated using:
   - Logistic map
   - Sine map
3. The scrambled image is encrypted using a bitwise XOR with the chaotic sequence.
4. Decryption reverses the process using the same key and iteration settings.
Files
- input.bmp: Original image input
- encrypted.jpg: Encrypted output (random-like visual)
- decrypted.jpg: Decrypted image (matches original)
- image_encryption.py: Python script for encryption and decryption
Requirements
• Python 3
• OpenCV (cv2)
• NumPy
• Matplotlib
Install dependencies:
pip install numpy opencv-python matplotlib
Usage
Run the script:
python image_encryption.py
The script reads input.bmp, performs encryption with a predefined key and saves:
- encrypted.jpg
- decrypted.jpg
Key Parameter
- The encryption key used is 0.67.
- The number of Arnold Cat Map iterations is set to 2.
Notes
- The image must be resized to a square (e.g., 256x256).
- The encryption is symmetric; the same key is used for decryption.
