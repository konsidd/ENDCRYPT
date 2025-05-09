import numpy as np
import cv2
import argparse

def create_test_pattern():
    """
    Create a test pattern image that will clearly show encryption differences
    """
    # Create a 256x256 RGB image with white background
    img = np.ones((256, 256, 3), dtype=np.uint8) * 255
    
    # Add a grid pattern
    for i in range(0, 256, 32):
        # Vertical lines
        cv2.line(img, (i, 0), (i, 255), (0, 0, 0), 1)
        # Horizontal lines
        cv2.line(img, (0, i), (255, i), (0, 0, 0), 1)
    
    # Add color squares in corners
    # Red square (top-left)
    cv2.rectangle(img, (10, 10), (50, 50), (255, 0, 0), -1)
    # Green square (top-right)
    cv2.rectangle(img, (206, 10), (246, 50), (0, 255, 0), -1)
    # Blue square (bottom-left)
    cv2.rectangle(img, (10, 206), (50, 246), (0, 0, 255), -1)
    # Yellow square (bottom-right)
    cv2.rectangle(img, (206, 206), (246, 246), (255, 255, 0), -1)
    
    # Add gradients
    # Gradient from left to right in the center
    for i in range(100, 156):
        cv2.line(img, (50, i), (205, i), (i-100, 0, 255-(i-100)), 1)
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'Test Pattern', (70, 80), font, 1, (0, 0, 0), 2)
    cv2.putText(img, 'EndCrypt', (80, 180), font, 1, (0, 0, 0), 2)
    
    # Add circles of varying sizes
    cv2.circle(img, (128, 128), 25, (255, 0, 255), -1)  # Magenta
    cv2.circle(img, (128, 128), 15, (0, 255, 255), -1)  # Cyan
    
    return img

def main():
    parser = argparse.ArgumentParser(description='Generate a test pattern image for encryption testing')
    parser.add_argument('--output', default='test_pattern.png', help='Output image filename')
    args = parser.parse_args()
    
    # Create the test pattern
    test_img = create_test_pattern()
    
    # Save the image
    cv2.imwrite(args.output, test_img)
    print(f"Test pattern image saved as {args.output}")

if __name__ == "__main__":
    main()