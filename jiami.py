import numpy as np
import os
from PIL import Image
import random
import pickle

def encrypt_image(input_path, output_image_path, key_path):
    # 打开图片并转换为RGB模式
    img = Image.open(input_path).convert('RGB')
    width, height = img.size
    
    # 获取所有像素坐标的索引
    pixel_count = width * height
    indices = list(range(pixel_count))
    
    # 随机打乱索引顺序
    random.shuffle(indices)
    
    # 保存密钥到文件
    with open(key_path, 'wb') as f:
        pickle.dump(indices, f)
    
    # 将图片转换为numpy数组并打乱像素
    pixels = np.array(img)
    flat_pixels = pixels.reshape(-1, 3)
    encrypted_flat = flat_pixels[indices]
    encrypted_pixels = encrypted_flat.reshape(height, width, 3)
    
    # 保存加密后的图片
    encrypted_img = Image.fromarray(encrypted_pixels.astype('uint8'))
    encrypted_img.save(output_image_path)

// 示例用法
if __name__ == "__main__":
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 加密示例：使用绝对路径处理所有文件
    input_path = os.path.join(script_dir, 'ceshi.png')
    output_image_path = os.path.join(script_dir, 'encrypted.png')
    key_path = os.path.join(script_dir, 'secret.key')
    encrypt_image(input_path, output_image_path, key_path)
    print(f"加密完成！文件已保存至: {script_dir}")
    # 解密示例：使用encrypted.png和secret.key恢复原始图片
    # decrypt_image('encrypted.png', 'secret.key', 'decrypted.png')
    # print("解密完成！生成解密图片decrypted.png")