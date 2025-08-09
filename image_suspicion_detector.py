import numpy as np
from PIL import Image
import scipy.fftpack as fft
from scipy.ndimage import sobel
import os

class ImageSuspicionDetector:
    def __init__(self):
        # 配置参数
        self.color_variance_threshold = 10.0  # 纯色图方差阈值
        self.entropy_threshold = 7.8  # 熵值阈值
        self.repeat_pattern_threshold = 0.9  # 重复模式阈值
        self.freq_domain_threshold = 0.3  # 频域能量分布阈值
        self.min_normal_size = 10  # 最小正常尺寸
        self.max_normal_aspect_ratio = 10.0  # 最大正常长宽比

    def load_image(self, image_path):
        """加载图像并转换为RGB格式"""
        try:
            img = Image.open(image_path).convert('RGB')
            return img
        except Exception as e:
            print(f"加载图像失败: {e}")
            return None

    def check_size_format(self, img):
        """检查图像尺寸和格式是否异常"""
        width, height = img.size

        # 检查尺寸是否异常小
        if width < self.min_normal_size or height < self.min_normal_size:
            return True, "图像尺寸异常小"

        # 检查长宽比是否异常
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > self.max_normal_aspect_ratio:
            return True, "图像长宽比异常"

        return False, "尺寸和格式正常"

    def check_solid_color(self, img):
        """检测是否为纯色图"""
        pixels = np.array(img)
        # 计算RGB三个通道的方差
        variance = np.var(pixels, axis=(0, 1))
        avg_variance = np.mean(variance)

        if avg_variance < self.color_variance_threshold:
            return True, f"纯色图嫌疑 (方差: {avg_variance:.2f})"
        return False, f"非纯色图 (方差: {avg_variance:.2f})"

    def calculate_entropy(self, img):
        """计算图像信息熵"""
        pixels = np.array(img)
        # 将图像转换为灰度图以简化熵计算
        gray = np.mean(pixels, axis=2).astype(np.uint8)
        # 计算直方图
        hist, _ = np.histogram(gray, bins=256, range=(0, 255), density=True)
        # 计算熵
        entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0]))
        return entropy

    def analyze_texture(self, img):
        """分析图像纹理特征"""
        pixels = np.array(img).astype(np.float32)
        gray = np.mean(pixels, axis=2)

        # 计算边缘梯度
        dx = sobel(gray, axis=0)
        dy = sobel(gray, axis=1)
        gradient_magnitude = np.sqrt(dx**2 + dy**2)

        # 计算梯度统计特征
        gradient_mean = np.mean(gradient_magnitude)
        gradient_std = np.std(gradient_magnitude)

        # 检测重复模式
        has_repeat_pattern = self._detect_repeat_pattern(pixels)

        return {
            'gradient_mean': gradient_mean,
            'gradient_std': gradient_std,
            'has_repeat_pattern': has_repeat_pattern
        }

    def _detect_repeat_pattern(self, pixels, block_size=8):
        """检测图像中的重复模式"""
        height, width, _ = pixels.shape
        max_blocks_x = width // block_size
        max_blocks_y = height // block_size

        if max_blocks_x < 2 or max_blocks_y < 2:
            return False

        # 提取块并计算哈希值
        block_hashes = []
        for y in range(max_blocks_y):
            for x in range(max_blocks_x):
                block = pixels[y*block_size:(y+1)*block_size, x*block_size:(x+1)*block_size]
                block_hash = hash(block.tobytes())
                block_hashes.append(block_hash)

        # 检查重复率
        unique_hashes = set(block_hashes)
        repeat_ratio = 1.0 - len(unique_hashes) / len(block_hashes)
        return repeat_ratio > self.repeat_pattern_threshold

    def analyze_frequency_domain(self, img):
        """分析图像频域特征"""
        pixels = np.array(img)
        gray = np.mean(pixels, axis=2).astype(np.float32)

        # 执行2D傅里叶变换
        f = fft.fft2(gray)
        fshift = fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)

        # 计算低频和高频能量
        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2

        # 低频区域（中心区域）
        low_freq_region = magnitude_spectrum[crow-10:crow+11, ccol-10:ccol+11]
        low_freq_energy = np.sum(low_freq_region)

        # 高频区域（除去低频区域的部分）
        high_freq_energy = np.sum(magnitude_spectrum) - low_freq_energy

        # 计算高低频能量比
        total_energy = low_freq_energy + high_freq_energy
        if total_energy == 0:
            freq_ratio = 0
        else:
            freq_ratio = high_freq_energy / total_energy

        return freq_ratio

    def detect_suspicion(self, image_path):
        """综合检测图像可疑程度"""
        img = self.load_image(image_path)
        if img is None:
            return False, "无法加载图像", {}

        result = {
            'suspicious': False,
            'reasons': [],
            'details': {}
        }

        # 1. 尺寸与格式校验
        size_suspicious, size_reason = self.check_size_format(img)
        result['details']['size_check'] = {'suspicious': size_suspicious, 'reason': size_reason}
        if size_suspicious:
            result['suspicious'] = True
            result['reasons'].append(size_reason)

        # 2. 纯色图检测
        solid_suspicious, solid_reason = self.check_solid_color(img)
        result['details']['solid_color'] = {'suspicious': solid_suspicious, 'reason': solid_reason}
        if solid_suspicious:
            result['suspicious'] = True
            result['reasons'].append(solid_reason)
            # 纯色图直接判定为可疑
            return result['suspicious'], '; '.join(result['reasons']), result['details']

        # 3. 熵值分析
        entropy = self.calculate_entropy(img)
        result['details']['entropy'] = entropy
        if entropy >= self.entropy_threshold:
            result['details']['entropy_suspicious'] = True
            result['reasons'].append(f"高熵值 ({entropy:.2f} bits)")
        else:
            result['details']['entropy_suspicious'] = False

        # 4. 纹理分析
        texture_info = self.analyze_texture(img)
        result['details']['texture'] = texture_info
        if texture_info['has_repeat_pattern']:
            result['suspicious'] = True
            result['reasons'].append("存在重复模式")

        # 5. 频域分析
        freq_ratio = self.analyze_frequency_domain(img)
        result['details']['frequency_ratio'] = freq_ratio
        freq_suspicious = freq_ratio > self.freq_domain_threshold
        result['details']['frequency_suspicious'] = freq_suspicious
        if freq_suspicious:
            result['reasons'].append(f"频域能量分布异常 (高低频比: {freq_ratio:.2f})")

        # 综合判定
        if not result['suspicious']:
            # 检查熵值和频域特征组合
            if entropy >= self.entropy_threshold and freq_suspicious:
                result['suspicious'] = True
                result['reasons'].append("高熵值+频域能量分布异常，疑似加密测试图")
            # 检查尺寸异常和重复模式组合
            elif size_suspicious and texture_info['has_repeat_pattern']:
                result['suspicious'] = True
                result['reasons'].append("异常尺寸+重复模式，疑似可疑图")

        if not result['reasons']:
            result['reasons'].append("未发现可疑特征")

        return result['suspicious'], '; '.join(result['reasons']), result['details']

# 测试函数
if __name__ == "__main__":
    detector = ImageSuspicionDetector()
    test_image = "test_image.png"  # 替换为实际测试图像路径
    if os.path.exists(test_image):
        suspicious, reasons, details = detector.detect_suspicion(test_image)
        print(f"是否可疑: {suspicious}")
        print(f"原因: {reasons}")
        print(f"详细信息: {details}")
    else:
        print(f"测试图像 {test_image} 不存在")