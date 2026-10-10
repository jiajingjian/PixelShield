import os
import subprocess


def check_ffmpeg():
    """检查 FFmpeg 是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False


def extract_audio(input_video, output_audio):
    """从视频中提取音频"""
    if not check_ffmpeg():
        return False
    
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-vn',
        '-acodec', 'copy',
        output_audio
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=300)
        return os.path.exists(output_audio) and os.path.getsize(output_audio) > 100
    except Exception:
        return False


def has_audio(input_video):
    """检查视频是否有音频"""
    if not check_ffmpeg():
        return False
    
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'stream=codec_type',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_video
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return 'audio' in result.stdout.strip()
    except Exception:
        return False


def merge_audio_video(video_path, audio_path, output_path):
    """合并视频和音频，输出为 MP4"""
    if not check_ffmpeg():
        return False
    
    if audio_path and os.path.exists(audio_path):
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-map', '0:v:0',
            '-map', '1:a:0?',
            '-shortest',
            output_path
        ]
    else:
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            output_path
        ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=600)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"合并音频视频失败: {e}")
        return False
