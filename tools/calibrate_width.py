# -*- coding: utf-8 -*-
"""
calibrate_width.py —— 实测「一行到底能放多少个字符」。

做法：生成一份只含测量行的文档（8pt Consolas，与正式材料同样式），
渲染成位图后逐行统计文字带的「起始 y」——被折行的句子会产生两条带，
据此判定该长度是否超宽，从而得到真实的每行容量。
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
WORK = os.path.join(PROJECT_DIR, "tools", "calib")
NODE = r"D:\Programs\deepseek\resources\app.asar.unpacked\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js"
NODE = r"D:\Programs\deepseeek\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
CLI = (r"D:\Programs\deepseeek\resources\app.asar.unpacked\dsh\node_modules"
       r"\@deepseek-ai\libreoffice-kit\lib\cli.js")
PY = sys.executable

sys.path.insert(0, os.path.join(PROJECT_DIR, "tools"))
from verify_layout import count_text_rows  # noqa: E402


def bands(path):
    """返回页面中所有文字带的 (起, 止) 列表（正文区域）。"""
    from PIL import Image
    img = Image.open(path).convert("L")
    W, H = img.size
    px = img.load()
    top, bottom = int(H * 0.08), int(H * 0.92)
    out = []
    cur = None
    for y in range(top, bottom):
        has = False
        for x in range(W):
            if px[x, y] < 128:
                has = True
                break
        if has:
            cur = [y, y] if cur is None else [cur[0], y]
        else:
            if cur is not None and cur[1] - cur[0] + 1 >= 2:
                out.append(tuple(cur))
            cur = None
    if cur is not None:
        out.append(tuple(cur))
    return out


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK, exist_ok=True)

    # 测量行：分别测试纯 ASCII 与含中文的行，找出真实折行阈值
    cases = []
    for n in range(70, 111, 2):
        cases.append(("A" * n, "ASCII %d" % n))
    for n in range(30, 61, 2):
        cases.append(("行" * n, "CJK %d 字 (=%d 宽)" % (n, n * 2)))
    # 模拟真实代码：行号前缀 + 代码
    for n in range(74, 95, 2):
        cases.append(("1234  " + "M" * n, "前缀+ASCII %d (总 %d)" % (n, n + 6)))

    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.left_margin = Cm(1.6); sec.right_margin = Cm(1.6)
    sec.top_margin = Cm(1.8); sec.bottom_margin = Cm(1.6)
    sec.header_distance = Cm(0.9); sec.footer_distance = Cm(0.8)

    style = doc.styles["Normal"]
    style.font.name = "Consolas"
    style.font.size = Pt(8)
    rpr = style.element.get_or_add_rPr()
    rf = rpr.get_or_add_rFonts()
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), "Consolas" if a != "w:eastAsia" else "宋体")
    pf = style.paragraph_format
    pf.space_before = Pt(0); pf.space_after = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(11.5)
    pf.widow_control = False

    for text, label in cases:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        r.font.name = "Consolas"
        r.font.size = Pt(8)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        r._element.rPr.rFonts.set(qn("w:cs"), "Consolas")

    docx = os.path.join(WORK, "calib.docx")
    doc.save(docx)

    subprocess.run([NODE, CLI, "convert", "--input", docx,
                    "--output", os.path.join(WORK, "calib.pdf")],
                   capture_output=True, text=True)
    outdir = os.path.join(WORK, "pg")
    subprocess.run([NODE, CLI, "render",
                    "--input", os.path.join(WORK, "calib.pdf"),
                    "--output-dir", outdir, "--pages", "1", "--dpi", "150"],
                   capture_output=True, text=True)

    pngs = [f for f in os.listdir(outdir) if f.endswith(".png")]
    if not pngs:
        print("渲染失败")
        return 1
    bl = bands(os.path.join(outdir, pngs[0]))

    # 逐行分配：每个用例占 1 条带，若折行则占 2 条
    print("共 %d 个测量用例，渲染出 %d 条文字带" % (len(cases), len(bl)))
    idx = 0
    results = {}
    for text, label in cases:
        if idx >= len(bl):
            results[label] = None
            continue
        if idx + 1 < len(bl):
            gap = bl[idx + 1][0] - bl[idx][1]
            wrapped = gap < 4          # 同一段落内的折行几乎没有间隙
        else:
            wrapped = False
        results[label] = wrapped
        idx += 2 if wrapped else 1

    for text, label in cases:
        print("  %-28s -> %s" % (label, "折行" if results.get(label) else "单行"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
