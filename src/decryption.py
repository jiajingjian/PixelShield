import numpy as np
import os
from PIL import Image
import pickle
from utils import get_decrypted_directory, generate_decrypted_filename


def decrypt_image(input_path, key_path, progress_callback=None):
    """解密图片"""
    if progress_callback:
        progress_callback(5)
    
    encrypted_img = Image.open(input_path)
    encrypted_mode = encrypted_img.mode
    width, height = encrypted_img.size

    if progress_callback:
        progress_callback(10)

    with open(key_path, 'rb') as f:
        key_data = pickle.load(f)
    
    if progress_callback:
        progress_callback(20)
    
    if isinstance(key_data, dict):
        indices = key_data['indices']
        original_mode = key_data.get('original_mode', 'RGB')
        original_ext = key_data.get('original_ext', '.png')
    else:
        indices = key_data
        original_mode = 'RGB'
        original_ext = '.png'

    if progress_callback:
        progress_callback(30)

    indices_np = np.array(indices)
    recover_indices = np.empty_like(indices_np)
    recover_indices[indices_np] = np.arange(len(indices_np))

    if progress_callback:
        progress_callback(50)

    pixels = np.array(encrypted_img)
    
    if progress_callback:
        progress_callback(60)
    
    if encrypted_mode == 'RGBA':
        flat_encrypted = pixels.reshape(-1, 4)
        decrypted_flat = flat_encrypted[recover_indices]
        decrypted_pixels = decrypted_flat.reshape(height, width, 4)
    else:
        flat_encrypted = pixels.reshape(-1, 3)
        decrypted_flat = flat_encrypted[recover_indices]
        decrypted_pixels = decrypted_flat.reshape(height, width, 3)
    
    if progress_callback:
        progress_callback(70)
    
    if original_mode == 'RGBA':
        decrypted_img = Image.fromarray(decrypted_pixels.astype('uint8'), 'RGBA')
    else:
        decrypted_img = Image.fromarray(decrypted_pixels.astype('uint8'), 'RGB')
    
    if progress_callback:
        progress_callback(80)
    
    decrypted_dir = get_decrypted_directory()
    
    # 确保目录存在
    if not os.path.exists(decrypted_dir):
        os.makedirs(decrypted_dir)
    
    original_name = os.path.basename(input_path)
    output_filename = generate_decrypted_filename(original_name)
    output_filename = os.path.splitext(output_filename)[0] + original_ext
    output_image_path = os.path.join(decrypted_dir, output_filename)
    
    if original_ext.lower() in ['.jpg', '.jpeg']:
        decrypted_img.convert('RGB').save(output_image_path, 'JPEG', quality=95)
    elif original_ext.lower() == '.png':
        decrypted_img.save(output_image_path, 'PNG')
    else:
        decrypted_img.convert('RGB').save(output_image_path)
    
    if progress_callback:
        progress_callback(100)
    
    return output_image_path
