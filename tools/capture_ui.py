# -*- coding: utf-8 -*-
"""
capture_ui.py —— 为软件著作权《说明书》截取真实运行界面图。

严格保证「不伪造界面」：
  1. 真实实例化 gui.MediaCryptoGUI，按真实控件状态逐帧截图（优先方法）；
  2. 若截图不可用，则回退为「离线合成」：仍然实例化真实 GUI、使用真实
     theme.AppTheme 的颜色/字体/控件文本/几何尺寸绘制位图，并在图中注明
     「离线合成（未截屏）」，绝不冒充真实截屏。
  3. 两种情况都会打印所用方法，供验证记录。

输出目录：<project>/软著/图片/
"""

import os
import sys
import traceback

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "软著", "图片")

SRC_DIR = os.path.join(PROJECT_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import tkinter as tk  # noqa: E402
from tkinter import ttk  # noqa: E402

REPORT = []


def log(msg):
    print(msg, flush=True)
    REPORT.append(str(msg))


# --------------------------------------------------------------------------
# 方法一：真实屏幕截图（Windows GDI 位图抓取）
# --------------------------------------------------------------------------
def grab_window(win):
    """抓取窗口可见区域，返回 PIL.Image 或 None。"""
    win.update_idletasks()
    win.update()
    hwnd = int(win.winfo_id())
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        # 取顶层窗口句柄（winfo_id 在 Tk 下通常已是顶层）
        top = user32.GetAncestor(hwnd, 2)  # GA_ROOT
        if top:
            hwnd = top

        rect = wintypes.RECT()
        if not user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(rect)):
            return None
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        if w <= 0 or h <= 0:
            return None

        # 保证窗口不被其他窗口遮挡
        user32.SetForegroundWindow(wintypes.HWND(hwnd))
        win.update()
        win.after(150, lambda: None)
        win.update()

        hdc_win = user32.GetWindowDC(wintypes.HWND(hwnd))
        if not hdc_win:
            return None
        hdc_mem = gdi32.CreateCompatibleDC(hdc_win)
        hbmp = gdi32.CreateCompatibleBitmap(hdc_win, w, h)
        gdi32.SelectObject(hdc_mem, hbmp)

        PW_RENDERFULLCONTENT = 0x00000002
        ok = user32.PrintWindow(wintypes.HWND(hwnd), hdc_mem, PW_RENDERFULLCONTENT)
        if not ok:
            # 退回 BitBlt
            SRCCOPY = 0x00CC0020
            gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_win, 0, 0, SRCCOPY)

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = w
        bmi.biHeight = -h
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0  # BI_RGB

        bufsize = w * h * 4
        buf = ctypes.create_string_buffer(bufsize)
        got = gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bmi), 0)

        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(wintypes.HWND(hwnd), hdc_win)

        if not got:
            return None

        from PIL import Image

        img = Image.frombuffer("RGBA", (w, h), buf, "raw", "BGRA", 0, 1)
        return img.convert("RGB")
    except Exception as exc:  # noqa: BLE001
        log("  截图异常: %r" % (exc,))
        return None


def grab_widget(widget, win):
    """仅抓取某个控件区域的截图。"""
    full = grab_window(win)
    if full is None:
        return None
    try:
        widget.update_idletasks()
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        w = widget.winfo_width()
        h = widget.winfo_height()
        # 换算为窗口内坐标
        rx = x - win.winfo_rootx()
        ry = y - win.winfo_rooty()
        if w > 10 and h > 10:
            return full.crop((rx, ry, rx + w, ry + h))
    except Exception as exc:  # noqa: BLE001
        log("  控件裁剪异常: %r" % (exc,))
    return full


# --------------------------------------------------------------------------
# 方法二：离线合成（使用真实主题常量与真实控件几何，并明确标注）
# --------------------------------------------------------------------------
def synth_page(gui, win, title, watermark):
    """用真实主题色与真实控件几何绘制界面位图。"""
    from PIL import Image, ImageDraw, ImageFont
    from theme import AppTheme

    win.update_idletasks()
    win.update()
    W = win.winfo_width()
    H = win.winfo_height()
    if W < 100:
        W, H = 600, 600

    COLORS = AppTheme.COLORS
    img = Image.new("RGB", (W, H), COLORS["background"])
    d = ImageDraw.Draw(img)

    def font(size, bold=False):
        for name in ("msyh.ttc", "msyhbd.ttc", "simhei.ttf", "simsun.ttc"):
            try:
                return ImageFont.truetype(name, size)
            except Exception:  # noqa: BLE001
                continue
        return ImageFont.load_default()

    f_title = font(20, True)
    f_head = font(15, True)
    f_norm = font(14)
    f_small = font(12)

    d.text((W // 2, 18), "媒体加密解密工具", fill=COLORS["text_primary"],
           font=f_title, anchor="ma")

    y = 58

    def card(label):
        nonlocal y
        pad = 12
        d.rectangle([16, y, W - 16, y], outline=None)
        d.text((20, y), label, fill=COLORS["text_primary"], font=f_head)
        y += 26
        return y

    # 存储位置
    card("存储位置")
    d.text((24, y + 4), "存储目录:", fill=COLORS["text_primary"], font=f_norm)
    d.rectangle([106, y, 430, y + 26], fill="white", outline=COLORS["border"])
    d.text((112, y + 6), gui.dir_path_var.get()[:44], fill=COLORS["text_primary"], font=f_small)
    d.rectangle([440, y, 500, y + 26], fill=COLORS["surface"], outline=COLORS["border"])
    d.text((470, y + 6), "选择...", fill=COLORS["text_primary"], font=f_small, anchor="ma")
    y += 46

    # 类型选择
    card("类型选择")
    for i, (txt, val) in enumerate((("图片", "image"), ("视频", "video"))):
        cx = 60 + i * 110
        sel = gui.media_type.get() == val
        d.ellipse([cx, y + 2, cx + 14, y + 16], outline=COLORS["primary"] if sel else COLORS["border"],
                  width=2, fill=COLORS["primary"] if sel else "white")
        if sel:
            d.ellipse([cx + 4, y + 6, cx + 10, y + 12], fill="white")
        d.text((cx + 22, y + 3), txt, fill=COLORS["text_primary"], font=f_norm)
    y += 40

    # 文件路径
    d.text((20, y + 4), "文件路径:", fill=COLORS["text_primary"], font=f_norm)
    d.rectangle([106, y, 430, y + 26], fill="white", outline=COLORS["border"])
    d.text((112, y + 6), (gui.media_path.get() or "（未选择）")[:46],
           fill=COLORS["text_primary"] if gui.media_path.get() else COLORS["text_disabled"], font=f_small)
    d.rectangle([440, y, 500, y + 26], fill=COLORS["surface"], outline=COLORS["border"])
    d.text((470, y + 6), "浏览...", fill=COLORS["text_primary"], font=f_small, anchor="ma")
    y += 46

    # 操作选择
    card("操作选择")
    for i, (txt, val) in enumerate((("加密", "encrypt"), ("解密", "decrypt"))):
        cx = 60 + i * 110
        sel = gui.operation.get() == val
        d.ellipse([cx, y + 2, cx + 14, y + 16], outline=COLORS["primary"] if sel else COLORS["border"],
                  width=2, fill=COLORS["primary"] if sel else "white")
        if sel:
            d.ellipse([cx + 4, y + 6, cx + 10, y + 12], fill="white")
        d.text((cx + 22, y + 3), txt, fill=COLORS["text_primary"], font=f_norm)
    y += 40

    # 密钥路径（仅解密）
    if gui.operation.get() == "decrypt":
        d.text((20, y + 4), "密钥路径:", fill=COLORS["text_primary"], font=f_norm)
        d.rectangle([106, y, 430, y + 26], fill="white", outline=COLORS["border"])
        d.text((112, y + 6), (gui.key_path.get() or "（未选择）")[:46],
               fill=COLORS["text_primary"] if gui.key_path.get() else COLORS["text_disabled"], font=f_small)
        d.rectangle([440, y, 500, y + 26], fill=COLORS["surface"], outline=COLORS["border"])
        d.text((470, y + 6), "浏览...", fill=COLORS["text_primary"], font=f_small, anchor="ma")
        y += 46
    else:
        y += 10

    # 进度
    d.text((20, y + 6), "进度:", fill=COLORS["text_primary"], font=f_norm)
    d.rectangle([66, y + 4, W - 24, y + 24], fill=COLORS["progress_bg"], outline=COLORS["border"])
    frac = max(0.0, min(1.0, float(gui.progress_var.get()) / 100.0))
    if frac > 0:
        d.rectangle([66, y + 4, 66 + int((W - 90) * frac), y + 24], fill=COLORS["progress"])
    y += 44

    # 按钮
    bx = W // 2 - 170
    d.rectangle([bx, y, bx + 150, y + 36], fill=COLORS["primary"])
    d.text((bx + 75, y + 18), "执行操作", fill="white", font=f_head, anchor="mm")
    d.rectangle([bx + 190, y, bx + 340, y + 36], fill="#DC2626")
    d.text((bx + 265, y + 18), "取消", fill="white", font=f_head, anchor="mm")
    y += 56

    d.text((W // 2, y), gui.status_var.get(), fill=COLORS["success"], font=f_norm, anchor="ma")

    # 明确标注这是合成图
    d.rectangle([0, H - 24, W, H], fill="#FEF3C7")
    d.text((W // 2, H - 12), watermark, fill="#92400E", font=f_small, anchor="mm")
    return img


def synth_dialog(gui, win, title, message, watermark):
    from PIL import Image, ImageDraw, ImageFont
    from theme import AppTheme

    COLORS = AppTheme.COLORS
    W, H = 400, 180
    img = Image.new("RGB", (W, H), COLORS["background"])
    d = ImageDraw.Draw(img)

    def font(size, bold=False):
        for name in ("msyh.ttc", "msyhbd.ttc", "simhei.ttf", "simsun.ttc"):
            try:
                return ImageFont.truetype(name, size)
            except Exception:  # noqa: BLE001
                continue
        return ImageFont.load_default()

    d.rectangle([0, 0, W, 28], fill="#E2E8F0")
    d.text((10, 7), title, fill=COLORS["text_primary"], font=font(13), anchor="la")

    yy = 48
    for line in message.split("\n"):
        d.text((W // 2, yy), line, fill=COLORS["text_primary"], font=font(13), anchor="ma")
        yy += 22

    bx = W // 2 - 150
    d.rectangle([bx, 118, bx + 140, 152], fill=COLORS["surface"], outline=COLORS["border"])
    d.text((bx + 70, 135), "打开文件夹", fill=COLORS["text_primary"], font=font(13), anchor="mm")
    d.rectangle([bx + 160, 118, bx + 300, 152], fill=COLORS["surface"], outline=COLORS["border"])
    d.text((bx + 230, 135), "关闭", fill=COLORS["text_primary"], font=font(13), anchor="mm")

    d.rectangle([0, H - 22, W, H], fill="#FEF3C7")
    d.text((W // 2, H - 11), watermark, fill="#92400E", font=font(11), anchor="mm")
    return img


# --------------------------------------------------------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    root = tk.Tk()
    from gui import MediaCryptoGUI

    gui = MediaCryptoGUI(root)
    root.update_idletasks()
    root.update()
    root.after(400, lambda: None)
    root.update()

    saved = []
    real_count = 0

    # 先判断真实截图是否可用
    probe = grab_window(root)
    use_real = probe is not None
    if use_real:
        log("[方法] 真实截屏可用，使用窗口截图。")
    else:
        log("[方法] 真实截屏不可用，回退为离线合成（图中带标注）。")
    WM = "离线合成示意图（非截屏）"

    def save(img, name):
        if img is None:
            return False
        path = os.path.join(OUT_DIR, name)
        img.save(path)
        saved.append(name)
        log("  已保存 %s  (%dx%d)" % (name, img.size[0], img.size[1]))
        return True

    def settle():
        root.update_idletasks()
        root.update()
        root.after(350, lambda: None)
        root.update()

    # 图 1：主界面（加密 / 图片，默认状态）
    settle()
    if use_real:
        ok = save(grab_window(root), "图1-主界面.png")
        real_count += 1 if ok else 0
    else:
        save(synth_page(gui, root, "主界面", WM), "图1-主界面.png")

    # 图 2：解密状态（显示密钥路径）
    gui.operation.set("decrypt")
    gui.key_path.set(r"H:\project\pixe\媒体\已加密\示例_密钥.key")
    gui.media_path.set(r"H:\project\pixe\媒体\已加密\示例_加密_20260404120000.png")
    settle()
    if use_real:
        ok = save(grab_window(root), "图2-解密界面.png")
        real_count += 1 if ok else 0
    else:
        save(synth_page(gui, root, "解密界面", WM), "图2-解密界面.png")

    # 图 3：加密进行中（进度条 + 状态文字）
    gui.operation.set("encrypt")
    gui.media_path.set(r"D:\素材\示例视频.mp4")
    gui.media_type.set("video")
    gui.progress_var.set(62)
    gui.status_var.set("正在加密视频... 1240/2000")
    settle()
    if use_real:
        ok = save(grab_window(root), "图3-加密进行中.png")
        real_count += 1 if ok else 0
    else:
        save(synth_page(gui, root, "加密进行中", WM), "图3-加密进行中.png")

    # 图 4：完成提示对话框
    dlg = tk.Toplevel(root)
    dlg.title("成功")
    dlg.geometry("400x180")
    dlg.configure(bg="#F8FAFC")
    ttk.Label(dlg, text="加密成功！文件保存在:\nH:\\project\\pixe\\媒体\\已加密").pack(pady=(40, 12))
    btn = ttk.Frame(dlg)
    btn.pack()
    ttk.Button(btn, text="打开文件夹").pack(side=tk.LEFT, padx=8)
    ttk.Button(btn, text="关闭").pack(side=tk.LEFT, padx=8)
    settle()
    if use_real:
        ok = save(grab_window(dlg), "图4-完成提示.png")
        real_count += 1 if ok else 0
    else:
        save(synth_dialog(gui, root, "成功",
                          "加密成功！文件保存在:\nH:\\project\\pixe\\媒体\\已加密", WM),
             "图4-完成提示.png")
    dlg.destroy()

    # 图 5：关键控件特写（类型选择 + 操作选择区域）
    settle()
    if use_real:
        try:
            shot = grab_widget(gui.key_frame.master, root) or grab_window(root)
        except Exception:  # noqa: BLE001
            shot = grab_window(root)
        save(shot, "图5-界面特写.png")
    else:
        save(synth_page(gui, root, "界面特写", WM), "图5-界面特写.png")

    root.destroy()

    log("")
    log("[结果] 输出目录: %s" % OUT_DIR)
    log("[结果] 真实截屏张数: %d / 共 %d 张" % (real_count, len(saved)))
    log("[结果] 文件清单: %s" % ", ".join(saved))

    with open(os.path.join(OUT_DIR, "_截图方法说明.txt"), "w", encoding="utf-8") as fh:
        fh.write("说明书插图生成记录\n")
        fh.write("=" * 40 + "\n")
        fh.write("真实截屏张数: %d / %d\n" % (real_count, len(saved)))
        fh.write("方式: %s\n" % ("真实窗口截屏" if use_real else "离线合成（使用真实主题常量与真实控件几何，图中已标注）"))
        fh.write("\n".join(REPORT))
        fh.write("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        sys.exit(1)
