# -*- coding: utf-8 -*-
"""measure2.py —— 评估「折行显示」对分页的影响，为最终版面提供依据。"""
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["main.py", "utils.py", "theme.py", "encryption.py", "decryption.py",
         "video_utils.py", "opencv_accelerator.py", "simple_video_encryption.py",
         "simple_video_decryption.py", "gui.py", "simple_test.py"]


def disp_h(text, width):
    """按等宽字体的字符宽度估算显示行数；中文/全角按 2 个字符宽计。"""
    if not text:
        return 1
    w = 0
    for ch in text:
        w += 2 if ord(ch) > 0x2E7F else 1
    return max(1, (w + width - 1) // width)


total_lines = 0
chars_total = 0
for f in FILES:
    with open(os.path.join(PROJECT, f), encoding="utf-8") as fh:
        for line in fh.read().replace("\t", "    ").split("\n"):
            if line.strip():
                total_lines += 1
                chars_total += len(line)

print("有效代码行总数:", total_lines)
print("平均行长(按字符): %.1f" % (chars_total / total_lines))
print()

for width in (78, 80, 82, 84, 86, 88, 90, 95, 100):
    disp = 0
    wrapped = 0
    for f in FILES:
        with open(os.path.join(PROJECT, f), encoding="utf-8") as fh:
            for line in fh.read().replace("\t", "    ").split("\n"):
                if line.strip():
                    h = disp_h(line, width)
                    disp += h
                    if h > 1:
                        wrapped += 1
    ratio = total_lines / disp
    print("限宽 %3d 字符: 折行 %3d 行, 显示行合计 %4d, 每页可容纳代码行(按50显示行/页) ≈ %.1f"
          % (width, wrapped, disp, 50 * ratio))
