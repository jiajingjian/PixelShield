import os
import sys
print("Testing image encryption/decryption module loading...")

try:
    from encryption import encrypt_image
    print("[OK] encryption loaded successfully")
except Exception as e:
    print(f"[FAIL] encryption load failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from decryption import decrypt_image
    print("[OK] decryption loaded successfully")
except Exception as e:
    print(f"[FAIL] decryption load failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from opencv_accelerator import check_opencv_accel_available
    print("[OK] opencv_accelerator loaded successfully")
    print(f"OpenCV hardware acceleration available: {check_opencv_accel_available()}")
except Exception as e:
    print(f"[FAIL] opencv_accelerator load failed: {e}")
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
