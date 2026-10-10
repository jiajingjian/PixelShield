# -*- coding: utf-8 -*-
"""
pitch_sweep.py —— 扫描「行高」，找到自然分页下每一页都不少于 50 行的版面。

只做一件事：不加人为分页，让排版引擎自然分页，然后用像素统计每页实际行数。
选出「最小行数 >= 50」且「没有空白页」的行高。
"""

import json
import os
import re
import shutil
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(PROJECT_DIR, "tools")
WORK = os.path.join(TOOLS_DIR, "sweep")
NODE = r"D:\Programs\deepseeek\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
CLI = (r"D:\Programs\deepseeek\resources\app.asar.unpacked\dsh\node_modules"
       r"\@deepseek-ai\libreoffice-kit\lib\cli.js")
PY = sys.executable

sys.path.insert(0, TOOLS_DIR)
from verify_layout import count_text_rows  # noqa: E402


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def build_and_measure(size, line_pt):
    src = os.path.join(TOOLS_DIR, "make_source_doc.py")
    with open(src, encoding="utf-8") as fh:
        code = fh.read()
    code = re.sub(r"^LINES_PER_PAGE = \d+", "LINES_PER_PAGE = 100000", code, flags=re.M)
    code = re.sub(r"^CODE_SIZE_PT = [\d.]+", "CODE_SIZE_PT = %s" % size, code, flags=re.M)
    code = re.sub(r"^LINE_SPACING_PT = [\d.]+", "LINE_SPACING_PT = %s" % line_pt, code, flags=re.M)
    code = code.replace(
        'PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
        'PROJECT_DIR = r"%s"' % PROJECT_DIR)
    code = code.replace('OUT_DIR = os.path.join(PROJECT_DIR, "软著")',
                        'OUT_DIR = r"%s"' % os.path.join(WORK, "out"))
    tag = "%s_%s" % (size, line_pt)
    tmp = os.path.join(WORK, "gen_%s.py" % tag)
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(code)

    r = run([PY, tmp])
    if r.returncode != 0:
        return None, (r.stderr or "")[-200:]

    outdir = os.path.join(WORK, "out")
    docx = None
    for f in os.listdir(outdir):
        if f.startswith("源程序-") and f.endswith(".docx"):
            docx = os.path.join(outdir, f)
    if not docx:
        return None, "无 docx"

    pdf = os.path.join(WORK, "t_%s.pdf" % tag)
    if os.path.exists(pdf):
        os.remove(pdf)
    run([NODE, CLI, "convert", "--input", docx, "--output", pdf])
    if not os.path.exists(pdf):
        return None, "PDF 转换失败"

    pgdir = os.path.join(WORK, "pg_%s" % tag)
    if os.path.isdir(pgdir):
        shutil.rmtree(pgdir)
    run([NODE, CLI, "render", "--input", pdf, "--output-dir", pgdir, "--dpi", "110"])

    counts = []
    for f in sorted(os.listdir(pgdir)):
        if f.lower().endswith(".png"):
            n, _ = count_text_rows(os.path.join(pgdir, f))
            counts.append(n)
    return counts, None


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(os.path.join(WORK, "out"), exist_ok=True)

    print("自然分页扫描（不加人为分页符）")
    print("%-16s %6s %6s %6s %8s" % ("字号/行高", "页数", "最小", "最大", "空白页"))
    print("-" * 52)

    results = []
    for size, pitches in (("8", [11.5, 11.3, 11.2, 11.1, 11.0]),
                          ("7.5", [11.0, 10.8, 10.6])):
        for pt in pitches:
            counts, err = build_and_measure(size, pt)
            if err:
                print("%-16s 失败: %s" % ("%s/%s" % (size, pt), err[:60]))
                continue
            zeros = sum(1 for c in counts if c == 0)
            print("%-16s %6d %6d %6d %8d"
                  % ("%s pt / %s pt" % (size, pt), len(counts), min(counts), max(counts), zeros))
            results.append({"size": size, "line_pt": pt, "pages": len(counts),
                            "min": min(counts), "max": max(counts), "zeros": zeros,
                            "counts": counts})
            if zeros == 0 and min(counts) >= 50:
                print("\n>>> 达标配置：字号 %s pt / 行高 %s pt" % (size, pt))
                print("    共 %d 页，每页 %d ~ %d 行" % (len(counts), min(counts), max(counts)))
                print("    分布: %s" % counts)
                with open(os.path.join(WORK, "result.json"), "w", encoding="utf-8") as fh:
                    json.dump(results, fh, ensure_ascii=False, indent=2)
                return 0

    print()
    ok = [r for r in results if r["zeros"] == 0]
    if ok:
        b = max(ok, key=lambda r: r["min"])
        print(">>> 最接近达标：字号 %s pt / 行高 %s pt，最小 %d 行 / %d 页"
              % (b["size"], b["line_pt"], b["min"], b["pages"]))
        print("    分布: %s" % b["counts"])
    with open(os.path.join(WORK, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    return 1


if __name__ == "__main__":
    sys.exit(main())
