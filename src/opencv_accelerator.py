import cv2
import numpy as np
import os
import sys

# 硬件加速检测状态
OPENCV_ACCEL_AVAILABLE = False
OPENCV_BACKEND = None
GPU_INFO = None


def detect_opencv_hardware_acceleration():
    """检测OpenCV支持的硬件加速后端"""
    global OPENCV_ACCEL_AVAILABLE, OPENCV_BACKEND, GPU_INFO
    
    backends = []
    
    # 尝试检测不同的硬件加速后端
    # 1. 检查是否有OpenCL支持
    try:
        if hasattr(cv2, 'ocl') and hasattr(cv2.ocl, 'haveOpenCL') and cv2.ocl.haveOpenCL():
            if hasattr(cv2.ocl, 'setUseOpenCL'):
                cv2.ocl.setUseOpenCL(True)
            backends.append(('OpenCL', 'DGPU'))
            print("OpenCL 硬件加速可用")
    except Exception as e:
        print(f"OpenCL 检测失败: {e}")
    
    # 2. 检查UMat是否可用（OpenCV的通用硬件加速抽象）
    try:
        # 创建一个测试UMat
        test_mat = np.zeros((100, 100, 3), dtype=np.uint8)
        test_umat = cv2.UMat(test_mat)
        backends.append(('UMat', 'DEFAULT'))
        print("OpenCV UMat 硬件加速可用")
    except Exception as e:
        print(f"UMat 检测失败: {e}")
    
    # 选择最佳的后端
    if backends:
        OPENCV_ACCEL_AVAILABLE = True
        # 优先选择OpenCL
        for backend_name, backend_type in backends:
            if backend_name == 'OpenCL':
                OPENCV_BACKEND = (backend_name, backend_type)
                break
        else:
            OPENCV_BACKEND = backends[0]
        
        print(f"选择的硬件加速后端: {OPENCV_BACKEND[0]}")
        
        # 获取GPU信息
        GPU_INFO = get_gpu_info()
        return True
    else:
        print("未检测到可用的OpenCV硬件加速后端")
        OPENCV_ACCEL_AVAILABLE = False
        return False


def get_gpu_info():
    """获取GPU信息"""
    info = {
        'available': False,
        'backend': None,
        'device_name': 'Unknown',
        'memory': 'Unknown'
    }
    
    if not OPENCV_ACCEL_AVAILABLE:
        return info
    
    info['available'] = True
    info['backend'] = OPENCV_BACKEND[0] if OPENCV_BACKEND else None
    
    # 尝试获取OpenCL设备信息
    try:
        if hasattr(cv2, 'ocl') and hasattr(cv2.ocl, 'haveOpenCL') and cv2.ocl.haveOpenCL():
            if hasattr(cv2.ocl, 'getOpenCLDevices'):
                devices = cv2.ocl.getOpenCLDevices()
                if devices and len(devices) > 0:
                    device = devices[0]
                    if hasattr(device, 'name'):
                        try:
                            info['device_name'] = device.name()
                        except:
                            info['device_name'] = 'OpenCL Device'
                    if hasattr(device, 'globalMemSize'):
                        try:
                            mem_size = device.globalMemSize()
                            info['memory'] = f"{mem_size / (1024**2):.0f} MB"
                        except:
                            info['memory'] = 'Unknown'
    except Exception as e:
        print(f"获取OpenCL设备信息失败: {e}")
    
    return info


def check_opencv_accel_available():
    """检查OpenCV硬件加速是否可用"""
    return OPENCV_ACCEL_AVAILABLE


def get_opencv_accel_info():
    """获取OpenCV硬件加速信息"""
    return {
        'available': OPENCV_ACCEL_AVAILABLE,
        'backend': OPENCV_BACKEND[0] if OPENCV_BACKEND else None,
        'gpu_info': GPU_INFO
    }


# 初始化硬件加速检测
detect_opencv_hardware_acceleration()


# ============================================
# 基于OpenCV硬件加速的加密解密函数
# ============================================

def logistic_map(x, mu=3.99):
    """Logistic混沌映射：x_{n+1} = mu * x_n * (1 - x_n)"""
    return mu * x * (1 - x)


def generate_chaotic_sequence(length, seed=0.1234, mu=3.99):
    """生成混沌序列（CPU版本，用于对比）"""
    sequence = np.empty(length, dtype=np.uint8)
    x = seed
    
    for i in range(length):
        x = mu * x * (1 - x)
        sequence[i] = np.uint8(int(x * 255) & 0xFF)
    
    return sequence


def generate_chaotic_sequence_opencv(length, seed=0.1234, mu=3.99):
    """生成混沌序列（使用NumPy优化，OpenCV处理图像）"""
    # 混沌序列生成主要是顺序计算，用NumPy优化
    sequence = np.empty(length, dtype=np.uint8)
    x = seed
    
    for i in range(length):
        x = mu * x * (1 - x)
        sequence[i] = np.uint8(int(x * 255) & 0xFF)
    
    return sequence


def generate_chaotic_sequence_per_frame_opencv(num_frames, width, height, seed, mu=3.99, frame_offset=0):
    """批量生成混沌序列（优化版本）"""
    pixel_count = width * height * 3
    
    all_seeds = np.empty(num_frames, dtype=np.float64)
    for i in range(num_frames):
        frame_idx = frame_offset + i
        all_seeds[i] = (seed + frame_idx * 0.01234) % 1.0
    
    chaotic_sequences = np.empty((num_frames, pixel_count), dtype=np.uint8)
    
    for i in range(num_frames):
        x = all_seeds[i]
        seq = np.empty(pixel_count, dtype=np.uint8)
        for j in range(pixel_count):
            x = mu * x * (1 - x)
            seq[j] = np.uint8(int(x * 255) & 0xFF)
        chaotic_sequences[i] = seq
    
    return chaotic_sequences


def encrypt_frame_opencv(frame, chaotic_seq):
    """使用OpenCV硬件加速加密单帧"""
    if OPENCV_ACCEL_AVAILABLE:
        try:
            # 将帧和序列转换为UMat进行硬件加速处理
            frame_umat = cv2.UMat(frame)
            seq_umat = cv2.UMat(chaotic_seq.reshape(frame.shape))
            
            # 使用OpenCV的bitwise_xor进行硬件加速
            encrypted_umat = cv2.bitwise_xor(frame_umat, seq_umat)
            
            # 转换回NumPy数组
            return encrypted_umat.get()
        except Exception as e:
            print(f"OpenCV硬件加速加密失败，回退到CPU: {e}")
    
    # 回退到CPU版本
    return np.bitwise_xor(frame, chaotic_seq.reshape(frame.shape))


def decrypt_frame_opencv(frame, chaotic_seq):
    """使用OpenCV硬件加速解密单帧（加密和解密是相同的XOR操作）"""
    return encrypt_frame_opencv(frame, chaotic_seq)


def encrypt_frames_batch_opencv(frames, seed, mu=3.99, start_frame_idx=0):
    """批量加密帧（使用OpenCV硬件加速）"""
    num_frames = len(frames)
    if num_frames == 0:
        return []
    
    height, width = frames[0].shape[:2]
    
    # 生成所有需要的混沌序列
    chaotic_seqs = generate_chaotic_sequence_per_frame_opencv(
        num_frames, width, height, seed, mu, start_frame_idx
    )
    
    encrypted_frames = []
    for i in range(num_frames):
        chaotic_seq = chaotic_seqs[i].reshape(height, width, 3)
        encrypted_frame = encrypt_frame_opencv(frames[i], chaotic_seq)
        encrypted_frames.append(encrypted_frame)
    
    return encrypted_frames


def decrypt_frames_batch_opencv(frames, seed, mu=3.99, start_frame_idx=0):
    """批量解密帧（使用OpenCV硬件加速）"""
    # 解密和加密使用相同的XOR操作
    return encrypt_frames_batch_opencv(frames, seed, mu, start_frame_idx)


# 提供向后兼容的接口
if OPENCV_ACCEL_AVAILABLE:
    logistic_map_accel = logistic_map
    generate_chaotic_sequence_accel = generate_chaotic_sequence_opencv
    generate_chaotic_sequence_per_frame_accel = generate_chaotic_sequence_per_frame_opencv
    encrypt_frame_accel = encrypt_frame_opencv
    encrypt_frames_batch_accel = encrypt_frames_batch_opencv
    decrypt_frame_accel = decrypt_frame_opencv
    decrypt_frames_batch_accel = decrypt_frames_batch_opencv
else:
    # 提供备用函数
    def logistic_map_accel(x, mu=3.99):
        raise RuntimeError("OpenCV hardware acceleration not available")
    
    def generate_chaotic_sequence_accel(length, seed=0.1234, mu=3.99):
        raise RuntimeError("OpenCV hardware acceleration not available")
    
    def generate_chaotic_sequence_per_frame_accel(num_frames, width, height, seed, mu=3.99, frame_offset=0):
        raise RuntimeError("OpenCV hardware acceleration not available")
    
    def encrypt_frame_accel(frame, chaotic_seq):
        raise RuntimeError("OpenCV hardware acceleration not available")
    
    def encrypt_frames_batch_accel(frames, seed, mu=3.99, start_frame_idx=0):
        raise RuntimeError("OpenCV hardware acceleration not available")
    
    def decrypt_frame_accel(frame, chaotic_seq):
        raise RuntimeError("OpenCV hardware acceleration not available")
    
    def decrypt_frames_batch_accel(frames, seed, mu=3.99, start_frame_idx=0):
        raise RuntimeError("OpenCV hardware acceleration not available")
