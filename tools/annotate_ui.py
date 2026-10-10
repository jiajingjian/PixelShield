# -*- coding: utf-8 -*-
"""
annotate_ui.py —— 生成《说明书》用的真实界面标注图与控件特写。

在真实窗口截屏的基础上：
  · 重新抓取「类型选择 / 操作选择 / 进度 / 按钮」区域的特写；
  · 依据控件的真实屏幕坐标绘制红色标注框与编号，生成操作指引图。
不修改软件本体，也不虚构界面。
"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "软著", "图片")
SRC_DIR = os.path.join(PROJECT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import tkinter as tk  # noqa: E402

sys.path.insert(0, os.path.join(PROJECT_DIR, "tools"))
from capture_ui import grab_window  # noqa: E402


def rect_in_window(widget, win, pad=4, dx=0, dy=0):
    widget.update_idletasks()
    x = widget.winfo_rootx() - win.winfo_rootx() - dx
    y = widget.winfo_rooty() - win.winfo_rooty() - dy
    w = widget.winfo_width()
    h = widget.winfo_height()
    return (x - pad, y - pad, x + w + pad, y + h + pad)


def main():
    from PIL import Image, ImageDraw, ImageFont

    os.makedirs(OUT_DIR, exist_ok=True)

    root = tk.Tk()
    from gui import ImageCryptoGUI

    gui = ImageCryptoGUI(root)
    root.update_idletasks()
    root.update()
    root.after(400, lambda: None)
    root.update()

    shot = grab_window(root)
    if shot is None:
        print("截屏不可用，跳过标注图生成。")
        return 1
    print("已获取真实窗口截图: %dx%d" % shot.size)

    # 计算窗口「客户区」在整窗位图里的偏移（标题栏 + 边框）。
    # 在抓图之后测量，避免窗口被 SetForegroundWindow 移动导致坐标错位。
    root.update_idletasks()
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    hwnd = user32.GetAncestor(int(root.winfo_id()), 2)
    full = wintypes.RECT()
    user32.GetWindowRect(wintypes.HWND(hwnd), ctypes.byref(full))
    cli = wintypes.RECT()
    user32.GetClientRect(wintypes.HWND(hwnd), ctypes.byref(cli))
    OFFSET_X = int(root.winfo_rootx()) - full.left
    OFFSET_Y = int(root.winfo_rooty()) - full.top
    print("窗口 rect=(%d,%d) 大小=%dx%d | 客户区=%dx%d | 偏移 dx=%d dy=%d"
          % (full.left, full.top, full.right - full.left, full.bottom - full.top,
             cli.right, cli.bottom, OFFSET_X, OFFSET_Y))

    def font(size):
        for name in ("msyh.ttc", "simhei.ttf", "simsun.ttc"):
            try:
                return ImageFont.truetype(name, size)
            except Exception:  # noqa: BLE001
                continue
        return ImageFont.load_default()

    # ---------------- 图6：界面操作指引（真实截图 + 红框编号） ----------------
    img = shot.copy()
    d = ImageDraw.Draw(img)
    fnum = font(16)
    flab = font(13)

    # 依据真实控件坐标定位。
    # winfo_rootx/rooty 给出「客户区相对」坐标，而位图包含标题栏，
    # 因此纵向需要加上 OFFSET_Y 才能与截图像素对齐。
    def gbox(widget, pad=3):
        widget.update_idletasks()
        cx = widget.winfo_rootx() - root.winfo_rootx()
        cy = widget.winfo_rooty() - root.winfo_rooty() + OFFSET_Y
        return (cx - pad, cy - pad, cx + widget.winfo_width() + pad, cy + widget.winfo_height() + pad)

    regions = [
        ("1", "存储目录", gbox(gui.dir_entry)),
        ("2", "图片路径", gbox(gui.media_path_entry)),
        ("3", "操作选择", gbox(gui.operation_frame)),
        ("4", "进度与状态", gbox(gui.progress_frame)),
        ("5", "执行 / 取消", gbox(gui.execute_btn.master)),
    ]
    regions = regions[:4]

    W, H = img.size
    print("窗口尺寸 %dx%d" % (W, H))


    # 1) 先画所有红框，并记录坐标
    placed = []
    for num, label, box in regions:
        x0 = max(1, box[0]); y0 = max(1, box[1])
        x1 = min(W - 2, box[2]); y1 = min(H - 2, box[3])
        d.rectangle([x0, y0, x1, y1], outline=(220, 38, 38), width=2)
        placed.append([num, label, x0, y0, x1, y1])
        print("  %s %-8s box=(%d,%d,%d,%d)" % (num, label, x0, y0, x1, y1))

    # 2) 标签：紧跟框上方；若与已放标签重叠则依次上移
    taken = []
    for num, label, x0, y0, x1, y1 in placed:
        tw = d.textlength(label, font=flab)
        bw = tw + 34
        bx = x1 - bw
        bx = max(2, min(bx, W - bw - 2))
        by = y0 - 24
        if by < 2:
            by = y1 + 3
        guard = 0
        while any(not (by + 21 < ty or by > ty + 21) and not (bx + bw < tx or bx > tx + tw2)
                  for tx, ty, tw2 in taken) and guard < 12:
            by -= 23
            guard += 1
            if by < 2:
                by = y1 + 3 + guard * 23
        taken.append((bx, by, bw))

        d.rectangle([bx, by, bx + bw, by + 21], fill=(255, 255, 255), outline=(220, 38, 38), width=2)
        r = 9
        d.ellipse([bx + 2, by + 2, bx + 2 + 2 * r, by + 2 + 2 * r], fill=(220, 38, 38))
        d.text((bx + 2 + r, by + 2 + r), num, fill="white", font=font(12), anchor="mm")
        d.text((bx + 2 * r + 6, by + 10), label, fill=(220, 38, 38), font=flab, anchor="lm")

    img.save(os.path.join(OUT_DIR, "图6-界面操作指引.png"))
    print("已保存 图6-界面操作指引.png")

    # ---------------- 图5：控件特写（操作选择 + 进度 + 按钮） ----------------
    # 保留一张未标注的清晰特写，便于说明书中单独展示核心控件。
    boxes = [
        gbox(gui.operation_frame, 4),
        gbox(gui.progress_frame, 4),
        gbox(gui.execute_btn.master, 4),
    ]
    xs0 = max(0, min(b[0] for b in boxes) - 4)
    ys0 = max(0, min(b[1] for b in boxes) - 6)
    xs1 = min(img.size[0], max(b[2] for b in boxes) + 4)
    ys1 = min(img.size[1], max(b[3] for b in boxes) + 6)
    crop = shot.crop((xs0, ys0, xs1, ys1))  # 用未标注的原图裁切
    crop.save(os.path.join(OUT_DIR, "图5-控件特写.png"))
    print("已保存 图5-控件特写.png  %dx%d  crop=(%d,%d,%d,%d)" % (crop.size + (xs0, ys0, xs1, ys1)))

    root.destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main())
