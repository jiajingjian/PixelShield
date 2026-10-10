import numpy as np
import os
from PIL import Image
import pickle
from utils import get_encrypted_directory, generate_encrypted_filename


def encrypt_image(input_path, output_dir, progress_callback=None):
    """加密图片"""
    if progress_callback:
        progress_callback(5)
    
    img = Image.open(input_path)
    original_mode = img.mode
    width, height = img.size
    
    if progress_callback:
        progress_callback(10)
    
    pixel_count = width * height
    indices = np.arange(pixel_count)
    
    if progress_callback:
        progress_callback(20)
    
    np.random.shuffle(indices)
    
    if progress_callback:
        progress_callback(30)
    
    encrypted_dir = get_encrypted_directory()
    
    if not os.path.exists(encrypted_dir):
        os.makedirs(encrypted_dir)
    
    original_name = os.path.basename(input_path)
    original_ext = os.path.splitext(original_name)[1]
    key_name = f"{os.path.splitext(original_name)[0]}_密钥.key"
    key_path = os.path.join(encrypted_dir, key_name)
    key_data = {
        'indices': indices.tolist(),
        'original_mode': original_mode,
        'original_ext': original_ext
    }
    with open(key_path, 'wb') as f:
        pickle.dump(key_data, f)
    
    if progress_callback:
        progress_callback(40)
    
    if img.mode == 'RGBA':
        pixels = np.array(img)
        flat_pixels = pixels.reshape(-1, 4)
    else:
        img_rgb = img.convert('RGB')
        pixels = np.array(img_rgb)
        flat_pixels = pixels.reshape(-1, 3)
    
    if progress_callback:
        progress_callback(50)
    
    encrypted_flat = flat_pixels[indices]
    
    if progress_callback:
        progress_callback(70)
    
    if img.mode == 'RGBA':
        encrypted_pixels = encrypted_flat.reshape(height, width, 4)
        encrypted_img = Image.fromarray(encrypted_pixels.astype('uint8'), 'RGBA')
    else:
        encrypted_pixels = encrypted_flat.reshape(height, width, 3)
        encrypted_img = Image.fromarray(encrypted_pixels.astype('uint8'), 'RGB')
    
    if progress_callback:
        progress_callback(80)
    
    encrypted_filename = generate_encrypted_filename(original_name)
    encrypted_filename = os.path.splitext(encrypted_filename)[0] + '.png'
    encrypted_image_path = os.path.join(encrypted_dir, encrypted_filename)
    encrypted_img.save(encrypted_image_path, 'PNG')
    
    if progress_callback:
        progress_callback(100)
    
    return encrypted_image_path, key_path
