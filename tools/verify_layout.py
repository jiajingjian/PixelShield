# -*- coding: utf-8 -*-
"""
verify_layout.py —— 对渲染后的页面位图做版面校验。

不做任何猜测：直接在位图上检测「文字行」的像素行区间，统计每页实际行数，
用于验证《源程序》文档是否满足「每页不少于 50 行」的登记要求。
"""

import os
import sys

from PIL import Image


def count_text_rows(path, dpi=110, dark=128, min_band_px=2, x_step=1):
    """
    统计一张页面图中「正文文字行」的数量。
    做法：逐像素行统计暗色像素；只要该行存在暗像素即视为文字行，
    再把纵向相邻的文字行合并为一条文字带（一条带 = 一行文字）。
    页眉与页脚通过纵向范围排除。
    """
    img = Image.open(path).convert("L")
    W, H = img.size
    px = img.load()

    # 纵向只取正文区域：跳过页眉（顶部 8%）与页脚（底部 8%）
    top = int(H * 0.08)
    bottom = int(H * 0.92)

    bands = []
    cur = None
    for y in range(top, bottom):
        has_text = False
        for x in range(0, W, x_step):
            if px[x, y] < dark:
                has_text = True
                break
        if has_text:
            if cur is None:
                cur = [y, y]
            else:
                cur[1] = y
        else:
            if cur is not None:
                if cur[1] - cur[0] + 1 >= min_band_px:
                    bands.append(tuple(cur))
                cur = None
    if cur is not None and cur[1] - cur[0] + 1 >= min_band_px:
        bands.append(tuple(cur))

    heights = [b[1] - b[0] + 1 for b in bands]
    return len(bands), heights


def main():
    if len(sys.argv) < 2:
        print("用法: verify_layout.py <页面图目录> [期望最少行数]")
        return 2

    d = sys.argv[1]
    expect = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    files = sorted(f for f in os.listdir(d) if f.lower().endswith(".png"))
    if not files:
        print("目录下没有 PNG: %s" % d)
        return 2

    print("校验目录: %s" % d)
    print("期望每页不少于 %d 行" % expect)
    print()
    print("%-14s %8s %8s %10s" % ("文件", "文字行数", "带高范围", "判定"))
    print("-" * 46)

    results = []
    for f in files:
        n, heights = count_text_rows(os.path.join(d, f))
        ok = n >= expect
        results.append((f, n, ok))
        hr = "%d~%d" % (min(heights), max(heights)) if heights else "-"
        print("%-14s %8d %8s %10s" % (f, n, hr, "OK" if ok else "不足"))

    bad = [r for r in results if not r[2]]
    print()
    print("总页数(已检): %d" % len(results))
    print("行数范围: %d ~ %d" % (min(r[1] for r in results), max(r[1] for r in results)))
    if bad:
        print("!! 未达标页面: %s" % [(b[0], b[1]) for b in bad])
        return 1
    print("通过：所有已检页面均不少于 %d 行。" % expect)
    return 0


if __name__ == "__main__":
    sys.exit(main())
