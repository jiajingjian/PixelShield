# -*- coding: utf-8 -*-
"""
calibrate_wrap.py —— 判定「给定宽度的一行会不会折行」。

每个用例单独成段，段间距给足，因此渲染出来的每条文字带只对应一段；
段落数 == 文字带数 说明没有折行，段落数 > 文字带数 说明有段落被折成两行。
"""

import os
import shutil
import subprocess
import sys

from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(PROJECT_DIR, "tools", "calib2")
NODE = r"D:\Programs\deepseeek\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
CLI = (r"D:\Programs\deepseeek\resources\app.asar.unpacked\dsh\node_modules"
       r"\@deepseek-ai\libreoffice-kit\lib\cli.js")


def count_bands(path):
    from PIL import Image
    import numpy as np
    im = Image.open(path).convert("L")
    a = np.asarray(im)
    H, W = a.shape
    top, bot = int(H * 0.05), int(H * 0.95)
    prof = (a[top:bot] < 160).sum(axis=1)
    nz = prof > 0
    n = 0
    prev = False
    for v in nz:
        if v and not prev:
            n += 1
        prev = v
    return n


def run_case(label, texts):
    """返回 (段落数, 文字带数)。"""
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.left_margin = Cm(1.6); sec.right_margin = Cm(1.6)
    sec.top_margin = Cm(1.8); sec.bottom_margin = Cm(1.6)

    style = doc.styles["Normal"]
    style.font.name = "Consolas"
    style.font.size = Pt(8)
    rf = style.element.get_or_add_rPr().get_or_add_rFonts()
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), "Consolas" if a != "w:eastAsia" else "宋体")
    pf = style.paragraph_format
    pf.space_before = Pt(0); pf.space_after = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(11.5)
    pf.widow_control = False

    for t in texts:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(t)
        r.font.name = "Consolas"
        r.font.size = Pt(8)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        r._element.rPr.rFonts.set(qn("w:cs"), "Consolas")

    docx = os.path.join(WORK, "c.docx")
    pdf = os.path.join(WORK, "c.pdf")
    doc.save(docx)
    for f in (pdf,):
        if os.path.exists(f):
            os.remove(f)
    subprocess.run([NODE, CLI, "convert", "--input", docx, "--output", pdf],
                   capture_output=True, text=True)
    pg = os.path.join(WORK, "pg")
    if os.path.isdir(pg):
        shutil.rmtree(pg)
    subprocess.run([NODE, CLI, "render", "--input", pdf, "--output-dir", pg,
                    "--pages", "1", "--dpi", "200"], capture_output=True, text=True)
    pngs = sorted(f for f in os.listdir(pg) if f.endswith(".png"))
    bands = count_bands(os.path.join(pg, pngs[0]))
    return len(texts), bands


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK, exist_ok=True)

    print("=== 测试一：行号前缀 + 纯 ASCII 代码，总宽度 80~100 ===")
    for total in (80, 84, 86, 88, 90, 92, 94, 96, 100):
        code = "M" * (total - 6)
        texts = ["%4d  %s" % (i + 1, code) for i in range(40)]
        np_, nb = run_case("ascii", texts)
        print("  总宽 %3d : 段落 %d / 文字带 %d  %s"
              % (total, np_, nb, "折行" if nb < np_ else "不折行"))

    print()
    print("=== 测试二：含中文的行（按 2 倍宽度估算）===")
    for n_cjk in (30, 34, 38, 40, 42, 44, 46, 48):
        code = "中" * n_cjk
        texts = ["%4d  %s" % (i + 1, code) for i in range(40)]
        np_, nb = run_case("cjk", texts)
        print("  中文 %2d 字(估宽 %3d): 段落 %d / 文字带 %d  %s"
              % (n_cjk, n_cjk * 2 + 6, np_, nb, "折行" if nb < np_ else "不折行"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
