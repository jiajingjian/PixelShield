import os
import sys
from datetime import datetime


def _resolve_default_content_dir():
    """解析默认「媒体」目录。

    - 开发时：使用项目根目录（本文件在 src/ 下，所以取上一层），
      让 媒体 目录始终待在项目根，和软著材料里的截图一致。
    - 打包成 exe 后：使用 exe 所在目录。绝不能使用 __file__，
      因为在 PyInstaller onefile 模式下 __file__ 指向 %TEMP%\\_MEIxxxx，
      该临时目录会在程序退出时被删除，用户加密/解密的结果会一起消失。
    - 如果 exe 所在目录不可写（例如放在 Program Files 或只读介质），
      回退到「文档」目录下的 媒体 目录。
    """
    if getattr(sys, 'frozen', False):
        bases = [os.path.dirname(os.path.abspath(sys.executable))]
    else:
        bases = [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
    bases.append(os.path.join(os.path.expanduser('~'), 'Documents'))

    for base in bases:
        target = os.path.join(base, '媒体')
        try:
            os.makedirs(target, exist_ok=True)
            probe = os.path.join(target, '.write_probe')
            with open(probe, 'w', encoding='utf-8') as f:
                f.write('')
            os.remove(probe)
            return target
        except OSError:
            continue

    return os.path.join(os.path.expanduser('~'), 'Documents', '媒体')


DEFAULT_CONTENT_DIR = _resolve_default_content_dir()

_content_dir = DEFAULT_CONTENT_DIR

ENCRYPTED_DIR = os.path.join(_content_dir, '已加密')
DECRYPTED_DIR = os.path.join(_content_dir, '已解密')

def ensure_directory_exists(directory):
    """确保目录存在"""
    directory = os.path.normpath(directory)  # 规范化路径
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f"创建目录失败 {directory}: {e}")

ensure_directory_exists(_content_dir)
ensure_directory_exists(ENCRYPTED_DIR)
ensure_directory_exists(DECRYPTED_DIR)


def set_content_directory(directory):
    """设置content目录"""
    global _content_dir
    _content_dir = os.path.normpath(directory)  # 规范化路径
    ensure_directory_exists(_content_dir)
    global ENCRYPTED_DIR, DECRYPTED_DIR
    ENCRYPTED_DIR = os.path.join(_content_dir, '已加密')
    DECRYPTED_DIR = os.path.join(_content_dir, '已解密')
    ensure_directory_exists(ENCRYPTED_DIR)
    ensure_directory_exists(DECRYPTED_DIR)


def get_content_directory():
    """获取content目录"""
    return _content_dir


def get_encrypted_directory():
    """获取已加密目录"""
    return ENCRYPTED_DIR


def get_decrypted_directory():
    """获取已解密目录"""
    return DECRYPTED_DIR


def create_output_directory(base_name):
    """创建输出目录"""
    output_dir = os.path.join(_content_dir, base_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def get_timestamp():
    """获取当前时间戳，格式：年月日时分秒"""
    return datetime.now().strftime('%Y%m%d%H%M%S')


def generate_encrypted_filename(original_name):
    """生成加密后的文件名"""
    name, ext = os.path.splitext(original_name)
    timestamp = get_timestamp()
    return f"{name}_加密_{timestamp}{ext}"


def generate_decrypted_filename(original_name):
    """生成解密后的文件名"""
    name, ext = os.path.splitext(original_name)
    timestamp = get_timestamp()
    return f"{name}_解密_{timestamp}{ext}"
