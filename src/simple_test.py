import os
import sys
print("Testing video encryption/decryption module loading...")

try:
    from video_utils import check_ffmpeg, has_audio
    print("[OK] video_utils loaded successfully")
    
    ffmpeg_ok = check_ffmpeg()
    print(f"FFmpeg available: {ffmpeg_ok}")
    
except Exception as e:
    print(f"[FAIL] video_utils load failed: {e}")

try:
    from simple_video_encryption import encrypt_video_simple
    print("[OK] simple_video_encryption loaded successfully")
except Exception as e:
    print(f"[FAIL] simple_video_encryption load failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from simple_video_decryption import decrypt_video_simple
    print("[OK] simple_video_decryption loaded successfully")
except Exception as e:
    print(f"[FAIL] simple_video_decryption load failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import gui
    print("[OK] gui loaded successfully")
except Exception as e:
    print(f"[FAIL] gui load failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
