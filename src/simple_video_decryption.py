import numpy as np
import os
import pickle
import cv2
from utils import get_decrypted_directory, generate_decrypted_filename
from opencv_accelerator import check_opencv_accel_available, get_opencv_accel_info
from video_utils import check_ffmpeg, has_audio, extract_audio, merge_audio_video


def decrypt_video_simple(input_path, key_path, status_callback=None, progress_callback=None):
    """
    简化版视频解密 - 支持音频保留，输出为 MP4
    
    流程：
    1. 读取密钥
    2. 读取加密视频
    3. 检测并提取音频（如果有）
    4. BGR → RGB（防偏色预处理）
    5. 批量多核 + 硬件加速
    6. 像素异或解密（使用相同密钥）
    7. RGB → BGR（防偏色后处理）
    8. 写入临时解密视频（无音频）
    9. 合并音频，输出为 MP4
    """
    original_name = os.path.basename(input_path)
    decrypted_dir = get_decrypted_directory()
    
    if not os.path.exists(decrypted_dir):
        os.makedirs(decrypted_dir)
    
    # 读取密钥
    with open(key_path, 'rb') as f:
        key_data = pickle.load(f)
    
    if not isinstance(key_data, dict) or key_data.get('algorithm') != 'simple_xor':
        raise Exception("密钥文件格式错误，不是简化异或加密的视频")
    
    key = key_data.get('key', 0)
    original_ext = key_data.get('original_ext', '.mp4')
    video_has_audio = key_data.get('has_audio', False)
    print(f"使用密钥解密: {key}")
    print(f"密钥标记有音频: {video_has_audio}")
    
    if progress_callback:
        progress_callback(10)
    
    output_filename_base = generate_decrypted_filename(original_name)
    output_filename_base = os.path.splitext(output_filename_base)[0]
    temp_video_path = os.path.join(decrypted_dir, output_filename_base + '_temp.avi')
    output_video_path = os.path.join(decrypted_dir, output_filename_base + '.mp4')
    temp_audio_path = os.path.join(decrypted_dir, output_filename_base + '_temp_audio.aac')
    
    # 检查 FFmpeg
    ffmpeg_available = check_ffmpeg()
    print(f"FFmpeg 可用: {ffmpeg_available}")
    
    if progress_callback:
        progress_callback(15)
    
    # 从加密视频提取音频
    audio_extracted = False
    if video_has_audio and ffmpeg_available:
        if status_callback:
            status_callback("正在从加密视频提取音频...")
        print("正在从加密视频提取音频...")
        audio_extracted = extract_audio(input_path, temp_audio_path)
        if not audio_extracted:
            print("警告：音频提取失败，将创建无音频视频")
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                temp_audio_path = None
    
    if progress_callback:
        progress_callback(20)
    
    # 读取加密视频
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception(f"无法打开视频文件: {input_path}")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if progress_callback:
        progress_callback(25)
    
    # 创建视频写入器（AVI + MJPG）
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
    
    if not out.isOpened():
        cap.release()
        raise Exception("无法创建视频写入器")
    
    # 检查硬件加速
    hardware_accel_available = check_opencv_accel_available()
    if hardware_accel_available:
        accel_info = get_opencv_accel_info()
        print(f"硬件加速可用: {accel_info.get('backend', 'Unknown')}")
    else:
        print("硬件加速不可用，使用 CPU 处理")
    
    if status_callback:
        status_callback("正在解密视频...")
    print("正在解密视频...")
    
    frame_count = 0
    batch_size = 16
    
    while True:
        frames = []
        for _ in range(batch_size):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        if not frames:
            break
        
        for frame in frames:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            decrypted_rgb = np.bitwise_xor(frame_rgb, np.uint8(key))
            decrypted_bgr = cv2.cvtColor(decrypted_rgb, cv2.COLOR_RGB2BGR)
            out.write(decrypted_bgr)
        
        frame_count += len(frames)
        
        if status_callback and frame_count % 10 == 0:
            status_callback(f"正在解密视频... {frame_count}/{total_frames}")
        
        if progress_callback:
            progress = 25 + (frame_count / total_frames) * 55
            progress_callback(progress)
    
    cap.release()
    out.release()
    
    if not os.path.exists(temp_video_path) or os.path.getsize(temp_video_path) < 1000:
        raise Exception("视频解密失败，临时文件异常")
    
    temp_size = os.path.getsize(temp_video_path)
    print(f"临时解密视频文件大小: {temp_size / (1024*1024):.2f} MB")
    
    if progress_callback:
        progress_callback(85)
    
    # 合并音频，输出为 MP4
    final_path_to_use = None
    if ffmpeg_available:
        if status_callback:
            status_callback("正在合并音频...")
        print("正在合并音频和视频，输出为 MP4...")
        
        audio_to_merge = temp_audio_path if (audio_extracted and os.path.exists(temp_audio_path)) else None
        merge_success = merge_audio_video(temp_video_path, audio_to_merge, output_video_path)
        
        if merge_success:
            print("音频合并成功！")
            final_path_to_use = output_video_path
        else:
            print("音频合并失败，使用 AVI 格式")
            output_video_path_avi = os.path.join(decrypted_dir, output_filename_base + '.avi')
            os.rename(temp_video_path, output_video_path_avi)
            final_path_to_use = output_video_path_avi
    else:
        print("FFmpeg 不可用，使用 AVI 格式")
        output_video_path_avi = os.path.join(decrypted_dir, output_filename_base + '.avi')
        os.rename(temp_video_path, output_video_path_avi)
        final_path_to_use = output_video_path_avi
    
    if progress_callback:
        progress_callback(95)
    
    # 清理临时文件
    try:
        if os.path.exists(temp_video_path) and final_path_to_use != temp_video_path:
            os.remove(temp_video_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
    except Exception as e:
        print(f"清理临时文件时出错: {e}")
    
    if not os.path.exists(final_path_to_use):
        raise Exception("视频解密失败，最终文件未生成")
    
    final_size = os.path.getsize(final_path_to_use)
    print(f"解密完成！文件大小: {final_size / (1024*1024):.2f} MB")
    print(f"解密视频: {final_path_to_use}")
    
    if progress_callback:
        progress_callback(100)
    
    return final_path_to_use
