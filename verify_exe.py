# -*- coding: utf-8 -*-
"""对打包好的 exe 做完整验收测试（全部通过真实 GUI 操作完成）。

流程：
  1. 造一张内容已知的 PNG
  2. 启动 exe，确认主窗口出现
  3. 在「加密」模式选图片 -> 执行操作 -> 等到「成功」对话框
  4. 切到「解密」模式，分别填加密图和密钥 -> 执行操作 -> 等到「成功」
  5. 逐像素比对解密结果与原图；并确认产物不在 %TEMP%\\_MEI 里

用法：python verify_exe.py [exe路径]
退出码 0 = 全部通过。
"""
import ctypes
import os
import sys
import time
import glob
import subprocess
import tempfile

import numpy as np
import pyautogui
pyautogui.FAILSAFE = False
import win32clipboard
import win32con
import win32gui
import win32process
from PIL import Image

EXE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else r"H:\project\pixe\dist\图片加密解密工具1.0.0.exe")
EXE_DIR = os.path.dirname(EXE)
APP = os.path.basename(EXE)
ENC_DIR = os.path.join(EXE_DIR, "媒体", "已加密")
DEC_DIR = os.path.join(EXE_DIR, "媒体", "已解密")
WORK = os.path.join(tempfile.gettempdir(), "pixe_verify")
os.makedirs(WORK, exist_ok=True)

# GUI 客户区坐标（实测自真实控件，见 tools/ 下的界面探针输出）
C_MEDIA_ENTRY = (254, 186)
C_KEY_ENTRY = (254, 332)
C_MEDIA_BROWSE = (490, 186)
C_KEY_BROWSE = (490, 332)
C_DECRYPT_RADIO = (148, 270)
C_RUN_ENCRYPT = (199, 392)
C_RUN_DECRYPT = (199, 443)

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print("  [%s] %s%s" % ("通过" if ok else "未通过", name, (" — " + detail) if detail else ""))
    return bool(ok)


def set_clipboard(text):
    for _ in range(5):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            win32clipboard.CloseClipboard()
            return True
        except Exception:  # noqa: BLE001
            time.sleep(0.3)
    return False


def app_windows(pid=None):
    res = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            if t:
                _, p = win32process.GetWindowThreadProcessId(h)
                if pid is None or p == pid:
                    res.append((h, t, p))
        return True

    win32gui.EnumWindows(cb, None)
    return res


def wait_dialog(pid, main_h, timeout=90):
    """等「成功 / 操作失败 / 错误」对话框，返回 (句柄, 标题)。"""
    for i in range(timeout):
        time.sleep(1)
        for h, t, _ in app_windows(pid):
            if h != main_h and t in ("成功", "操作失败", "错误"):
                return h, t, i + 1
    return None, None, timeout


def close_window(h):
    try:
        win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
        time.sleep(1)
    except Exception:  # noqa: BLE001
        pass


def force_foreground(hwnd):
    """把窗口强制带到前台。

    直接调 SetForegroundWindow 会被系统的前台锁拒绝（返回 0），
    标准做法是先把当前前台线程的输入队列用 AttachThreadInput 接过来再设置。
    否则窗口可能被别的窗口挡住，后续的鼠标点击会落到别人身上。
    """
    user32 = ctypes.windll.user32
    try:
        fg = user32.GetForegroundWindow()
        t1 = user32.GetWindowThreadProcessId(fg, None)
        t2 = user32.GetWindowThreadProcessId(hwnd, None)
        if t1 != t2:
            user32.AttachThreadInput(t1, t2, True)
        user32.ShowWindow(hwnd, 9)          # SW_RESTORE
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        if t1 != t2:
            user32.AttachThreadInput(t1, t2, False)
    except Exception as e:  # noqa: BLE001
        print("      ! 置顶失败：%s" % e)
    time.sleep(0.5)


def paste_into(ox, oy, x, y, text, label):
    """往 Tk 输入框里填内容：先清空再粘贴（避免与已有内容拼接）。"""
    set_clipboard(text)
    pyautogui.click(ox + x, oy + y)
    time.sleep(0.7)
    pyautogui.press("end")
    pyautogui.press("backspace", presses=300, interval=0.003)
    time.sleep(0.4)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.8)
    print("      已填入 %s：%s" % (label, text))


def wait_native_dialog(pid, timeout=20):
    """等 tkinter 弹出来的原生文件对话框（class #32770）。"""
    for _ in range(timeout * 2):
        for h, t, _ in app_windows(pid):
            if win32gui.GetClassName(h) == "#32770" and t:
                return h, t
        time.sleep(0.5)
    return None, None


def pick_file_via_dialog(ox, oy, bx, by, path, label, pid, main_h=None):
    """点「浏览...」，在原生对话框里粘贴完整路径并回车。原生对话框对中文路径更稳。"""
    if main_h:
        force_foreground(main_h)
    set_clipboard(path)
    pyautogui.click(ox + bx, oy + by)
    h, t = wait_native_dialog(pid)
    if not h:
        print("      ! %s 的原生对话框没出现，退回直接填输入框" % label)
        paste_into(ox, oy, bx - 220, by, path, label)
        return False
    time.sleep(1)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.8)
    pyautogui.press("enter")
    for _ in range(20):
        time.sleep(0.5)
        if not win32gui.IsWindow(h):
            break
    print("      已通过「浏览...」选择 %s：%s" % (label, path))
    time.sleep(0.5)
    return True


def run_operation(pid, main_h, xy, label):
    """点一次「执行操作」并等结果对话框；没反应才补点一次（避免重复执行）。"""
    ox, oy = win32gui.ClientToScreen(main_h, (0, 0))
    for attempt in (1, 2):
        force_foreground(main_h)
        pyautogui.click(ox + xy[0], oy + xy[1])
        h, t, secs = wait_dialog(pid, main_h, timeout=20)
        if h:
            print("      %s：第 %d 次点击后有响应（第 %s 秒）" % (label, attempt, secs))
            return h, t
        print("      %s：第 %d 次点击后 20 秒无响应，重试" % (label, attempt))
    return None, None


def main():
    # ---------- 准备测试图 ----------
    src = os.path.join(WORK, "acceptance_input.png")
    a = np.zeros((96, 128, 3), dtype="uint8")
    a[:, :, 0] = 210
    a[:48, :, 1] = 130
    a[:, :64, 2] = 70
    Image.fromarray(a).save(src)
    print("测试图：%s (%d bytes)" % (src, os.path.getsize(src)))

    subprocess.run(["taskkill", "/F", "/IM", APP], capture_output=True)
    time.sleep(2)

    before_enc = set(glob.glob(os.path.join(ENC_DIR, "*")))
    before_dec = set(glob.glob(os.path.join(DEC_DIR, "*")))

    print("\n[1] 启动 exe")
    subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
         "-Arguments @{CommandLine='\"%s\"'}" % EXE], capture_output=True)

    main_win = None
    for i in range(90):
        time.sleep(1)
        for h, t, p in app_windows():
            if "加密解密工具" in t:
                main_win = (h, t, p, i + 1)
                break
        if main_win:
            break
    if not check("exe 能启动并出现主窗口", main_win, str(main_win[1] if main_win else "90 秒内没出现")):
        return 1

    h, title, pid, secs = main_win
    print("      主窗口 pid=%s，第 %s 秒出现" % (pid, secs))
    time.sleep(3)
    ox, oy = win32gui.ClientToScreen(h, (0, 0))
    pyautogui.screenshot(os.path.join(WORK, "A_main.png"))

    # ---------- 加密 ----------
    print("\n[2] 加密流程")
    pick_file_via_dialog(ox, oy, *C_MEDIA_BROWSE, src, "图片路径", pid, main_h=h)
    dh, dtitle = run_operation(pid, h, C_RUN_ENCRYPT, "加密")
    pyautogui.screenshot(os.path.join(WORK, "B_encrypted.png"))
    check("加密弹出「成功」对话框", dtitle == "成功", "实际对话框：%r" % (dtitle,))
    close_window(dh)

    new_enc = sorted(set(glob.glob(os.path.join(ENC_DIR, "*"))) - before_enc)
    enc_img = [f for f in new_enc if f.endswith(".png")]
    enc_key = [f for f in new_enc if f.endswith(".key")]
    check("生成了加密图和密钥文件", bool(enc_img and enc_key),
          "%s | %s" % (os.path.basename(enc_img[0]) if enc_img else "-",
                       os.path.basename(enc_key[0]) if enc_key else "-"))
    if not (enc_img and enc_key):
        return 1
    print("      加密图 %d bytes，密钥 %d bytes" % (os.path.getsize(enc_img[0]), os.path.getsize(enc_key[0])))

    # ---------- 解密 ----------
    print("\n[3] 解密流程")
    pyautogui.click(ox + C_DECRYPT_RADIO[0], oy + C_DECRYPT_RADIO[1])
    time.sleep(1.5)
    pyautogui.screenshot(os.path.join(WORK, "C_decrypt_mode.png"))
    pick_file_via_dialog(ox, oy, *C_MEDIA_BROWSE, enc_img[0], "图片路径", pid, main_h=h)
    pick_file_via_dialog(ox, oy, *C_KEY_BROWSE, enc_key[0], "密钥路径", pid, main_h=h)
    dh2, dtitle2 = run_operation(pid, h, C_RUN_DECRYPT, "解密")
    pyautogui.screenshot(os.path.join(WORK, "D_decrypted.png"))
    check("解密弹出「成功」对话框", dtitle2 == "成功", "实际对话框：%r" % (dtitle2,))
    close_window(dh2)

    new_dec = sorted(set(glob.glob(os.path.join(DEC_DIR, "*"))) - before_dec)
    check("生成了解密结果文件", bool(new_dec), "; ".join(os.path.basename(f) for f in new_dec))

    if new_dec:
        original = np.array(Image.open(src).convert("RGB"))
        recovered = np.array(Image.open(new_dec[0]).convert("RGB"))
        same_shape = original.shape == recovered.shape
        identical = same_shape and np.array_equal(original, recovered)
        check("解密结果与原图逐像素一致", identical,
              "shape %s vs %s" % (original.shape, recovered.shape) if not same_shape
              else ("完全一致" if identical else "最大差异 %d" % int(np.abs(original.astype(int) - recovered.astype(int)).max())))

    # ---------- 输出位置 ----------
    print("\n[4] 产物位置")
    mei_hits = []
    for d in glob.glob(os.path.join(tempfile.gettempdir(), "_MEI*")):
        for r, _, files in os.walk(d):
            for f in files:
                if f.endswith((".png", ".key")):
                    mei_hits.append(os.path.join(r, f))
    check("产物没有落在会被删除的 %TEMP%\\_MEI 临时目录", not mei_hits, "; ".join(mei_hits[:3]))
    check("产物保存在 exe 同目录的 媒体\\ 下", os.path.isdir(ENC_DIR) and os.path.isdir(DEC_DIR), ENC_DIR)

    subprocess.run(["taskkill", "/F", "/IM", APP], capture_output=True)

    print("\n" + "=" * 64)
    passed = sum(1 for _, ok, _ in results if ok)
    print("验收结果：%d/%d 通过" % (passed, len(results)))
    for name, ok, detail in results:
        print("  %s %s" % ("PASS" if ok else "FAIL", name))
    print("=" * 64)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
