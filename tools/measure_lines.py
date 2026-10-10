# -*- coding: utf-8 -*-
"""measure_lines.py —— 统计源程序行宽分布，用于确定文档字号与页边距。"""
import os, sys, glob

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["main.py", "utils.py", "theme.py", "encryption.py", "decryption.py",
         "video_utils.py", "opencv_accelerator.py", "simple_video_encryption.py",
         "simple_video_decryption.py", "gui.py", "simple_test.py"]

allw = []
for f in FILES:
    with open(os.path.join(PROJECT, f), encoding="utf-8") as fh:
        for i, line in enumerate(fh.read().replace("\t", "    ").split("\n"), 1):
            if line.strip():
                allw.append((len(line), f, i, line.rstrip()))

allw.sort(reverse=True)
print("非空行总数:", len(allw))
print("最长行:", allw[0][0], "字符 |", allw[0][1], "行", allw[0][2])
print()
print("行宽分布:")
for t in [60, 70, 80, 90, 100, 110, 120, 150, 200]:
    print("  >%3d 字符: %d 行" % (t, sum(1 for w in allw if w[0] > t)))
print()
print("最长的 15 行:")
for w, f, i, txt in allw[:15]:
    print("  %3d  %s:%d  %s" % (w, f, i, txt[:110]))
