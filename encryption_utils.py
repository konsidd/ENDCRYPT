import cv2
import numpy as np
import math
from collections import Counter

def arnold_cat_map(image, iterations):
    """
    Apply Arnold Cat Map to shuffle pixels of the image.
    
    Args:
        image: Input image as numpy array
        iterations: Number of iterations to apply the transform
        
    Returns:
        Shuffled image
    """
    h, w, c = image.shape
    scrambled = image.copy()
    
    for _ in range(iterations):
        temp = np.zeros_like(image)
        for x in range(h):
            for y in range(w):
                # Added more complexity for higher iterations
                if iterations <= 2:
                    new_x = (2 * x + 1 * y) % h
                    new_y = (1 * x + 1 * y) % w
                elif iterations <= 4:
                    new_x = (2 * x + 3 * y) % h
                    new_y = (1 * x + 2 * y) % w
                elif iterations <= 6:
                    new_x = (3 * x + 2 * y) % h
                    new_y = (2 * x + 1 * y) % w
                else:
                    new_x = (3 * x + 5 * y) % h
                    new_y = (2 * x + 3 * y) % w
                temp[new_x, new_y] = scrambled[x, y]
        scrambled = temp.copy()
    
    return scrambled

def inverse_arnold_cat_map(image, iterations):
    """
    Apply inverse Arnold Cat Map to recover original image.
    
    Args:
        image: Shuffled image as numpy array
        iterations: Number of iterations used in encryption
        
    Returns:
        Deshuffled image
    """
    h, w, c = image.shape
    descrambled = image.copy()
    
    for _ in range(iterations):
        temp = np.zeros_like(image)
        for x in range(h):
            for y in range(w):
                # Inverse transformations corresponding to the forward ones
                if iterations <= 2:
                    new_x = (1 * x - 1 * y) % h
                    new_y = (-1 * x + 2 * y) % w
                elif iterations <= 4:
                    new_x = (2 * x - 3 * y) % h
                    new_y = (-1 * x + 2 * y) % w
                elif iterations <= 6:
                    new_x = (1 * x - 2 * y) % h
                    new_y = (-2 * x + 3 * y) % w
                else:
                    new_x = (3 * x - 5 * y) % h
                    new_y = (-2 * x + 3 * y) % w
                temp[new_x, new_y] = descrambled[x, y]
        descrambled = temp.copy()
    
    return descrambled

def logistic_map(size, key, level=1):
    """
    Generate chaotic sequence using logistic map.
    
    Args:
        size: Size of the sequence to generate
        key: Initial value (should be between 0 and 1)
        level: Security level (1-4)
        
    Returns:
        Chaotic sequence as uint8 array
    """
    # Adjust r parameter based on security level for more chaotic behavior
    r_values = {1: 3.7, 2: 3.8, 3: 3.9, 4: 3.99}
    r = r_values.get(level, 3.99)
    
    seq = np.zeros(size)
    seq[0] = key
    
    for i in range(1, size):
        seq[i] = r * seq[i-1] * (1 - seq[i-1])
    
    return (seq * 256).astype(np.uint8)

def sine_map(size, key, level=1):
    """
    Generate chaotic sequence using sine map.
    
    Args:
        size: Size of the sequence to generate
        key: Initial value (should be between 0 and 1)
        level: Security level (1-4)
        
    Returns:
        Chaotic sequence as uint8 array
    """
    # Adjust factor based on security level
    factors = {1: 0.8, 2: 0.9, 3: 0.95, 4: 1.0}
    factor = factors.get(level, 1.0)
    
    seq = np.zeros(size)
    seq[0] = key
    
    for i in range(1, size):
        seq[i] = factor * np.abs(np.sin(np.pi * seq[i-1] * (1.0 + (level * 0.1))))
    
    return (seq * 256).astype(np.uint8)

def encrypt_image(image, key, iterations):
    """
    Encrypt an image using combination of chaotic maps.
    
    Args:
        image: Input image as numpy array
        key: Encryption key (float between 0 and 1)
        iterations: Number of iterations for Arnold Cat Map
        
    Returns:
        Encrypted image
    """
    # Calculate security level from iterations
    level = (iterations + 1) // 2
    
    # Apply Arnold Cat Map for pixel shuffling
    scrambled = arnold_cat_map(image, iterations)
    
    # Generate chaotic sequences for pixel value modification
    h, w, c = scrambled.shape
    chaotic_seq1 = logistic_map(h * w * c, key, level)
    chaotic_seq2 = sine_map(h * w * c, key / 2, level)
    
    # Combine chaotic sequences
    chaotic_seq = chaotic_seq1 + chaotic_seq2
    chaotic_seq = chaotic_seq.reshape(h, w, c)
    
    # Apply XOR operation between image and chaotic sequence
    encrypted = np.bitwise_xor(scrambled, chaotic_seq)
    
    return encrypted

def decrypt_image(encrypted_image, key, iterations):
    """
    Decrypt an encrypted image.
    
    Args:
        encrypted_image: Encrypted image as numpy array
        key: Encryption key (float between 0 and 1)
        iterations: Number of iterations used in encryption
        
    Returns:
        Decrypted image
    """
    # Calculate security level from iterations
    level = (iterations + 1) // 2
    
    h, w, c = encrypted_image.shape
    
    # Generate the same chaotic sequences as in encryption
    chaotic_seq1 = logistic_map(h * w * c, key, level)
    chaotic_seq2 = sine_map(h * w * c, key / 2, level)
    
    # Combine chaotic sequences
    chaotic_seq = chaotic_seq1 + chaotic_seq2
    chaotic_seq = chaotic_seq.reshape(h, w, c)
    
    # Reverse the XOR operation
    descrambled = np.bitwise_xor(encrypted_image, chaotic_seq)
    
    # Reverse the Arnold Cat Map transform
    decrypted = inverse_arnold_cat_map(descrambled, iterations)
    
    return decrypted

def calculate_entropy(image):
    """
    Calculate Shannon entropy of an image.
    Higher entropy means more randomness (better encryption).
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Entropy value (bits/pixel)
    """
    # Flatten the image
    values = image.flatten()
    
    # Count occurrences of each pixel value
    counts = Counter(values)
    total_pixels = len(values)
    
    # Calculate entropy
    entropy = 0
    for count in counts.values():
        probability = count / total_pixels
        entropy -= probability * math.log2(probability)
    
    return entropy

def calculate_psnr(original, modified):
    """
    Calculate Peak Signal-to-Noise Ratio between two images.
    Lower PSNR for encrypted image means better encryption.
    Higher PSNR for decrypted image means better decryption.
    
    Args:
        original: Original image as numpy array
        modified: Modified image as numpy array
        
    Returns:
        PSNR value in dB
    """
    mse = np.mean((original.astype(float) - modified.astype(float)) ** 2)
    if mse == 0:
        return float('inf')  # No difference
    
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr

def get_pixel_distribution(image):
    """
    Calculate distribution of pixel values in an image.
    
    Args:
        image: Input image as numpy array
        
    Returns:
        Dictionary with low, mid, and high pixel value counts
    """
    # Flatten the image
    values = image.flatten()
    
    # Count pixel values in ranges
    low = np.sum((values >= 0) & (values <= 85))
    mid = np.sum((values > 85) & (values <= 170))
    high = np.sum((values > 170) & (values <= 255))
    
    total = len(values)
    
    return {
        'low': int(low / total * 100),
        'mid': int(mid / total * 100),
        'high': int(high / total * 100)
    }