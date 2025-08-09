import numpy as np
import os
from PIL import Image
import pickle

def decrypt_image(encrypted_path, key_path, output_path):
    # 打开加密图片并转换为RGB模式
    encrypted_img = Image.open(encrypted_path).convert('RGB')
    width, height = encrypted_img.size
    
    # 加载密钥
    with open(key_path, 'rb') as f:
        indices = pickle.load(f)
    
    # 创建恢复索引
    recover_indices = [0] * len(indices)
    for original_idx, new_idx in enumerate(indices):
        recover_indices[new_idx] = original_idx
    
    # 将加密图片转换为numpy数组并恢复像素顺序
    pixels = np.array(encrypted_img)
    flat_encrypted = pixels.reshape(-1, 3)
    decrypted_flat = flat_encrypted[recover_indices]
    decrypted_pixels = decrypted_flat.reshape(height, width, 3)
    
    # 保存解密后的图片
    decrypted_img = Image.fromarray(decrypted_pixels.astype('uint8'))
    decrypted_img.save(output_path)
    return True

if __name__ == "__main__":
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置解密文件路径
    encrypted_path = os.path.join(script_dir, 'encrypted.png')
    key_path = os.path.join(script_dir, 'secret.key')
    output_path = os.path.join(script_dir, 'decrypted.png')
    
    # 执行解密
    if decrypt_image(encrypted_path, key_path, output_path):
        print(f"解密完成！解密图片已保存至: {output_path}")
    else:
        print("解密失败，请检查文件是否存在")