import cv2
import numpy as np

OPENCV_ACCEL_AVAILABLE = False
OPENCV_BACKEND = None
GPU_INFO = None


def detect_opencv_hardware_acceleration():
    """检测OpenCV支持的硬件加速后端"""
    global OPENCV_ACCEL_AVAILABLE, OPENCV_BACKEND, GPU_INFO

    backends = []

    try:
        if hasattr(cv2, 'ocl') and hasattr(cv2.ocl, 'haveOpenCL') and cv2.ocl.haveOpenCL():
            if hasattr(cv2.ocl, 'setUseOpenCL'):
                cv2.ocl.setUseOpenCL(True)
            backends.append(('OpenCL', 'DGPU'))
            print("OpenCL 硬件加速可用")
    except Exception as e:
        print(f"OpenCL 检测失败: {e}")

    try:
        test_mat = np.zeros((100, 100, 3), dtype=np.uint8)
        test_umat = cv2.UMat(test_mat)
        backends.append(('UMat', 'DEFAULT'))
        print("OpenCV UMat 硬件加速可用")
    except Exception as e:
        print(f"UMat 检测失败: {e}")

    if backends:
        OPENCV_ACCEL_AVAILABLE = True
        for backend_name, backend_type in backends:
            if backend_name == 'OpenCL':
                OPENCV_BACKEND = (backend_name, backend_type)
                break
        else:
            OPENCV_BACKEND = backends[0]

        print(f"选择的硬件加速后端: {OPENCV_BACKEND[0]}")

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


detect_opencv_hardware_acceleration()
