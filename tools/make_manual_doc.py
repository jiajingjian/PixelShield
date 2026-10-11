# -*- coding: utf-8 -*-
"""
make_manual_doc.py —— 生成软件著作权登记《说明书》（软件使用说明书）。

依据中国版权保护中心《计算机软件著作权登记指南·所需文件》：
  · 文档每页不少于 30 行；
  · 页眉写明软件名称及版本号，且与申请表一致；
  · 纵向排版，文字从左向右。

写作约定（2026-10 改版）：
  · 全书只讲「打包好的 exe 怎么用」，不再出现 Python 安装、pip、源码运行等内容；
  · 示意图不插图片，用带边框和底色的单元格当方框、箭头字符连接，矢量清晰；
  · 正文用面向读者的口语，配合实测数字与具体路径，避免模板腔。
"""

import os
import re
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "软著")
IMG_DIR = os.path.join(OUT_DIR, "图片")

SOFTWARE_NAME = "图片加密解密工具"
SOFTWARE_VERSION = "V1.0.0"
AUTHOR = "贾京健"
EXE_NAME = "图片加密解密工具1.0.0.exe"

# 封面中部用大号红字展示的软件下载地址
DOWNLOAD_URL = "https://pan.quark.cn/s/78b1c38cc2d7?pwd=Pj1G"
DOWNLOAD_PWD = "Pj1G"

HEADER_TEXT = "%s %s" % (SOFTWARE_NAME, SOFTWARE_VERSION)

FONT_CN = "微软雅黑"
FONT_CN_EA = "微软雅黑"
FONT_MONO = "Consolas"

REPORT = []


def log(msg):
    print(msg, flush=True)
    REPORT.append(str(msg))


# --------------------------------------------------------------------------
def build():
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()

    # ---------------- 页面与样式 ----------------
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.0)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(1.8)
    sec.header_distance = Cm(1.1)
    sec.footer_distance = Cm(0.9)

    def set_run(run, name=FONT_CN, size=10.5, bold=False, color=None):
        run.font.name = name
        run.font.size = Pt(size)
        run.font.bold = bold
        if color:
            run.font.color.rgb = RGBColor(*color)
        rfonts = run._element.get_or_add_rPr().get_or_add_rFonts()
        # 显式声明四个字体族，避免渲染器回退到 Courier 等缺失字体
        rfonts.set(qn("w:ascii"), name)
        rfonts.set(qn("w:hAnsi"), name)
        rfonts.set(qn("w:cs"), name)
        rfonts.set(qn("w:eastAsia"), FONT_CN_EA)

    # 正文默认样式
    normal = doc.styles["Normal"]
    normal.font.name = FONT_CN
    normal.font.size = Pt(10)
    _nrfonts = normal.element.get_or_add_rPr().get_or_add_rFonts()
    _nrfonts.set(qn("w:ascii"), FONT_CN)
    _nrfonts.set(qn("w:hAnsi"), FONT_CN)
    _nrfonts.set(qn("w:cs"), FONT_CN)
    _nrfonts.set(qn("w:eastAsia"), FONT_CN_EA)
    npf = normal.paragraph_format
    npf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    npf.line_spacing = 1.22
    npf.space_after = Pt(2)

    # 标题样式：中文黑体感，层级清晰
    for lvl, (size, before, after) in enumerate([(14, 8, 5), (12, 6, 4), (10.5, 5, 3)], start=1):
        st = doc.styles["Heading %d" % lvl]
        st.font.name = FONT_CN
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0x1F, 0x35, 0x64)
        _hrfonts = st.element.get_or_add_rPr().get_or_add_rFonts()
        _hrfonts.set(qn("w:ascii"), FONT_CN)
        _hrfonts.set(qn("w:hAnsi"), FONT_CN)
        _hrfonts.set(qn("w:cs"), FONT_CN)
        _hrfonts.set(qn("w:eastAsia"), FONT_CN_EA)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        st.paragraph_format.line_spacing = 1.3
        st.paragraph_format.keep_with_next = True   # 标题不与正文分离

    # ---------------- 页眉（软件名称+版本号） ----------------
    hp = sec.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = hp.add_run(HEADER_TEXT)
    set_run(r, size=9)

    pPr = hp._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "808080")
    pbdr.append(bottom)
    pPr.append(pbdr)

    # ---------------- 页脚（第 X 页 共 Y 页） ----------------
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_field(paragraph, instr, placeholder="1"):
        parts = []
        r1 = paragraph.add_run()
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "begin"); r1._r.append(e)
        parts.append(r1)
        r2 = paragraph.add_run()
        e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = instr; r2._r.append(e)
        parts.append(r2)
        r3 = paragraph.add_run()
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "separate"); r3._r.append(e)
        parts.append(r3)
        parts.append(paragraph.add_run(placeholder))
        r5 = paragraph.add_run()
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end"); r5._r.append(e)
        parts.append(r5)
        return parts

    runs = [fp.add_run("第 ")]
    runs += add_field(fp, " PAGE ")
    runs += [fp.add_run(" 页  共 ")]
    runs += add_field(fp, " NUMPAGES ", "1")
    runs += [fp.add_run(" 页")]
    for r in runs:
        set_run(r, size=9)

    # ---------------- 排版辅助 ----------------
    def para(text="", style=None, size=10.5, bold=False, align=None,
             indent=True, space_after=2, name=FONT_CN):
        p = doc.add_paragraph(style=style)
        if align is not None:
            p.alignment = align
        if indent and style is None:
            p.paragraph_format.first_line_indent = Pt(20)
        p.paragraph_format.space_after = Pt(space_after)
        if text:
            r = p.add_run(text)
            set_run(r, name=name, size=size, bold=bold)
        return p

    def bullet(text, size=10, level=0):
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        p.paragraph_format.line_spacing = 1.2
        r = p.add_run(text)
        set_run(r, size=size)
        return p

    def numbered(text, size=10):
        # 手动编号：向上数紧邻的编号段落得到本项序号，碰到别的内容就从 1 重来。
        # （用 Word 的 List Number 样式会全文共用一个计数序列，跨小节串号。）
        n = 0
        for prev in reversed(doc.paragraphs):
            if re.match(r"^\d+\.\s", prev.text or ""):
                n += 1
            else:
                break
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Pt(20)
        p.paragraph_format.first_line_indent = Pt(-20)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        p.paragraph_format.line_spacing = 1.2
        r = p.add_run("%d. %s" % (n + 1, text))
        set_run(r, size=size)
        return p

    def caption(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run(text)
        set_run(r, size=9)
        r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        return p

    # 图号自动递增，保证全文「图 1、图 2……」顺序不乱
    fig_state = {"n": 0}

    def fig_cap(text):
        fig_state["n"] += 1
        caption("图 %d　%s" % (fig_state["n"], text))

    def figure(fname, width_cm, cap):
        path = os.path.join(IMG_DIR, fname)
        if not os.path.exists(path):
            log("  !! 缺少插图: %s" % fname)
            return
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_with_next = True    # 图片与图题不分离
        p.add_run().add_picture(path, width=Cm(width_cm))
        fig_cap(cap)

    def table(headers, rows, widths=None):
        t = doc.add_table(rows=1, cols=len(headers))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = t.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = ""
            p = hdr[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(h)
            set_run(r, size=10, bold=True)
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "E8EEF7")
            hdr[i]._tc.get_or_add_tcPr().append(shd)
        for row in rows:
            cells = t.add_row().cells
            for i, val in enumerate(row):
                cells[i].text = ""
                lines = str(val).split("\n")
                p = cells[i].paragraphs[0]
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(lines[0])
                set_run(r, size=9.5)
                for extra in lines[1:]:
                    r.add_break()
                    r2 = p.add_run(extra)
                    set_run(r2, size=9.5)
        for row in t.rows:
            trPr = row._tr.get_or_add_trPr()
            cant = OxmlElement("w:cantSplit")
            trPr.append(cant)
        if widths:
            for row in t.rows:
                for i, w in enumerate(widths):
                    row.cells[i].width = Cm(w)
        doc.add_paragraph().paragraph_format.space_after = Pt(3)
        return t

    def code_block(lines, size=9):
        for ln in lines:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            p.paragraph_format.line_spacing = Pt(12)
            p.paragraph_format.left_indent = Pt(14)
            r = p.add_run(ln if ln else " ")
            set_run(r, name=FONT_MONO, size=size)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---------------- 示意图元件：矩形框 + 箭头 ----------------
    # 示意图不插图片，直接用「带边框和底色的单元格」当方框、用箭头字符连接。
    # 好处：图形是文本，放大、打印都清晰，也不依赖任何外部素材。
    SHADE_MAIN = "E8F1FB"      # 主步骤（淡蓝）
    SHADE_ALT = "FDF3E3"       # 结果/分支（淡橙）
    SHADE_WARN = "FDECEC"      # 提醒（淡红）
    LINE_MAIN = "2E74B5"
    LINE_ALT = "C55A11"

    def _cell_border(cell, color, sz=8):
        tcPr = cell._tc.get_or_add_tcPr()
        borders = OxmlElement("w:tcBorders")
        for edge in ("top", "left", "bottom", "right"):
            e = OxmlElement("w:" + edge)
            e.set(qn("w:val"), "single")
            e.set(qn("w:sz"), str(sz))
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), color)
            borders.append(e)
        tcPr.append(borders)

    def _cell_shade(cell, fill):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), fill)
        tcPr.append(shd)

    def _fill_cell(cell, text, size=10, bold=False, fill=None, border=None,
                   align=WD_ALIGN_PARAGRAPH.CENTER):
        cell.text = ""
        if border:
            _cell_border(cell, border)
        if fill:
            _cell_shade(cell, fill)
        p = cell.paragraphs[0]
        p.alignment = align
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        for i, ln in enumerate(str(text).split("\n")):
            if i:
                p.add_run().add_break()
            r = p.add_run(ln)
            set_run(r, size=size, bold=bold)
        return p

    def vflow(steps, width=9.6, note=None, cap=None):
        """竖向流程：方框 ↓ 方框 ↓ ……（整条流程放一个表格里，不会和相邻表格粘连）"""
        rows = []
        for i, s in enumerate(steps):
            last = (i == len(steps) - 1) and not note
            rows.append(("box", s, SHADE_ALT if last else SHADE_MAIN,
                         LINE_ALT if last else LINE_MAIN))
            if i < len(steps) - 1 or note:
                rows.append(("arrow", "↓", None, None))
        if note:
            rows.append(("box", note, SHADE_ALT, LINE_ALT))

        t = doc.add_table(rows=len(rows), cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, (kind, text, fill, brd) in enumerate(rows):
            c = t.rows[i].cells[0]
            c.width = Cm(width)
            if kind == "box":
                _fill_cell(c, text, size=10.5, fill=fill, border=brd)
            else:
                p = _fill_cell(c, text, size=13, bold=True)
                p.runs[0].font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
                p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
                p.paragraph_format.line_spacing = Pt(13)
        if cap:
            fig_cap(cap)
        else:
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    def hflow(items, width=3.7, cap=None, small=False):
        """横向流程：框 → 框 → 框"""
        n = len(items)
        t = doc.add_table(rows=1, cols=n * 2 - 1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, s in enumerate(items):
            c = t.rows[0].cells[i * 2]
            c.width = Cm(width)
            _fill_cell(c, s, size=9 if small else 9.5, fill=SHADE_MAIN, border=LINE_MAIN)
            if i < n - 1:
                a = t.rows[0].cells[i * 2 + 1]
                a.width = Cm(1.0)
                p = _fill_cell(a, "→", size=13, bold=True)
                p.runs[0].font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
        if cap:
            fig_cap(cap)
        else:
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    def tip(title, text, fill=SHADE_WARN, border="C00000"):
        """提示块：小标题 + 说明，带底色，与正文区分开"""
        t = doc.add_table(rows=1, cols=1)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = t.rows[0].cells[0]
        c.text = ""
        _cell_border(c, border)
        _cell_shade(c, fill)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(title + "　")
        set_run(r, size=10, bold=True)
        r.font.color.rgb = RGBColor.from_string(border)
        r2 = p.add_run(text)
        set_run(r2, size=10)
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    # ======================================================================
    # 封面
    # ======================================================================
    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(SOFTWARE_NAME); set_run(r, size=30, bold=True, color=(0x1F, 0x35, 0x64))
    p.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("软件使用说明书"); set_run(r, size=20, bold=True)
    p.paragraph_format.space_after = Pt(30)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(SOFTWARE_VERSION); set_run(r, size=16, bold=True, color=(0x25, 0x63, 0xEB))
    p.paragraph_format.space_after = Pt(60)

    info = [
        ("软件名称", SOFTWARE_NAME),
        ("软件版本", SOFTWARE_VERSION),
        ("著作权人", AUTHOR),
        ("开发完成日期", "2026 年 04 月 04 日"),
        ("首次发表日期", "2026 年 10 月 10 日"),
        ("文档类别", "软件使用说明书（用户手册）"),
    ]
    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, v in info:
        cells = t.add_row().cells
        cells[0].text = ""; cells[1].text = ""
        p0 = cells[0].paragraphs[0]; p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r0 = p0.add_run(k + "："); set_run(r0, size=11, bold=True)
        p1 = cells[1].paragraphs[0]
        r1 = p1.add_run(v); set_run(r1, size=11)
        cells[0].width = Cm(4.2); cells[1].width = Cm(7.0)

    # ---- 下载地址（封面中部，大号红字） ----
    RED = (0xFF, 0x00, 0x00)

    doc.add_paragraph().paragraph_format.space_after = Pt(26)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("软件下载地址"); set_run(r, size=20, bold=True, color=RED)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(DOWNLOAD_URL); set_run(r, size=18, bold=True, color=RED)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("提取码：%s" % DOWNLOAD_PWD); set_run(r, size=18, bold=True, color=RED)

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)   # 封面单独成页

    # ======================================================================
    # 目录
    # ======================================================================
    doc.add_heading("目  录", level=1)
    toc = [
        ("第一章  这个软件能帮你做什么", ""),
        ("  1.1  一句话说清楚", ""),
        ("  1.2  谁适合用", ""),
        ("  1.3  能做与不能做", ""),
        ("  1.4  核心思路：把像素顺序打乱", ""),
        ("第二章  用之前先确认三件事", ""),
        ("  2.1  电脑要求", ""),
        ("  2.2  不需要额外安装什么", ""),
        ("  2.3  支持哪些图片", ""),
        ("第三章  拿到软件后怎么跑起来", ""),
        ("  3.1  单文件版与目录版怎么选", ""),
        ("  3.2  下载、解压、双击", ""),
        ("  3.3  首次运行的系统提示", ""),
        ("  3.4  启动、退出与卸载", ""),
        ("第四章  界面上一共就这几个东西", ""),
        ("  4.1  主界面", ""),
        ("  4.2  各区域做什么", ""),
        ("  4.3  核心控件特写", ""),
        ("  4.4  状态栏的三句话", ""),
        ("第五章  加密一张图片", ""),
        ("  5.1  三步总览", ""),
        ("  5.2  第一步：选图片", ""),
        ("  5.3  第二步：确认存放位置", ""),
        ("  5.4  第三步：点“执行操作”", ""),
        ("  5.5  完成后的两个文件", ""),
        ("  5.6  中途想停怎么办", ""),
        ("第六章  把图片还原回来", ""),
        ("  6.1  解密与加密只差一步", ""),
        ("  6.2  解密三步走", ""),
        ("  6.3  还原失败的三种情况", ""),
        ("第七章  密钥文件怎么保管", ""),
        ("  7.1  密钥丢了会怎样", ""),
        ("  7.2  建议的备份方式", ""),
        ("  7.3  四件不要做的事", ""),
        ("第八章  遇到提示信息怎么办", ""),
        ("  8.1  提示原文对照表", ""),
        ("  8.2  常见问题十问十答", ""),
        ("第九章  从头到尾走一遍", ""),
        ("  9.1  例子环境", ""),
        ("  9.2  加密过程", ""),
        ("  9.3  解密过程", ""),
        ("  9.4  结果对照", ""),
        ("第十章  它是怎么做到的", ""),
        ("  10.1  像素置乱做了什么", ""),
        ("  10.2  密钥文件里存了什么", ""),
        ("  10.3  为什么是无损的", ""),
        ("  10.4  程序由哪些部分构成", ""),
        ("  10.5  关于硬件加速，说实话", ""),
        ("第十一章  速度、体积与使用建议", ""),
        ("  11.1  一张图大概要多久", ""),
        ("  11.2  影响速度的三个因素", ""),
        ("  11.3  七条使用建议", ""),
        ("第十二章  目录与文件命名", ""),
        ("  12.1  软件目录长什么样", ""),
        ("  12.2  文件命名规则", ""),
        ("  12.3  改了存放位置之后", ""),
        ("第十三章  声明与联系方式", ""),
        ("  13.1  版权与开源许可", ""),
        ("  13.2  使用声明", ""),
        ("  13.3  联系方式与下载地址", ""),
    ]
    for item, _ in toc:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p.paragraph_format.line_spacing = Pt(11)
        r = p.add_run(item)
        set_run(r, size=10, bold=not item.startswith("  "))

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)   # 目录单独成页

    # ======================================================================
    # 第一章
    # ======================================================================
    doc.add_heading("第一章  这个软件能帮你做什么", level=1)

    doc.add_heading("1.1  一句话说清楚", level=2)
    para("它做的事情很朴素：把一张图片的像素顺序彻底打乱，让画面变成一堆看不出内容的噪点；"
         "需要看的时候，再用加密时生成的那个密钥文件把顺序还原回来。")
    para("打乱前后，图片的像素颜色值一个都没改——只是位置换了。所以还原回来的图片"
         "和原图是完全一样的，连一个像素都不会差。")
    para("整个过程在你自己的电脑上完成，不联网、不上传、不需要注册账号。")

    doc.add_heading("1.2  谁适合用", level=2)
    para("下面几种情况，用它是合适的：")
    bullet("电脑里存着家庭照片、证件翻拍件，不想被借电脑的人随手翻到；")
    bullet("要把样片或未公开的素材发给别人，又不希望对方二次留存；")
    bullet("做取证、记录类工作，需要在本地留一份“不直接可见”的副本；")
    bullet("教学演示时，想直观展示“像素置乱”这件事到底长什么样。")
    para("反过来说，如果你要防的是“有人专门来破解”，那它不合适——"
         "原因在 13.2 节会坦白讲清楚。")

    doc.add_heading("1.3  能做与不能做", level=2)
    table(
        ["项目", "能不能", "说明"],
        [
            ["加密图片", "能", "把像素顺序打乱，输出无损 PNG 噪点图"],
            ["解密图片", "能", "凭密钥文件还原，逐像素无损"],
            ["处理视频", "不能", "本版本只处理图片，没有视频功能"],
            ["处理 PDF／压缩包", "不能", "只认图片格式，不是通用加密工具"],
            ["防止专业破解", "不能", "像素置乱属于内容遮蔽，不是密码学加密"],
            ["联网备份／云同步", "不提供", "软件不联网，密钥需要你自己保管"],
        ],
        widths=[4.2, 2.4, 8.7],
    )

    doc.add_heading("1.4  核心思路：把像素顺序打乱", level=2)
    para("一张 1200 万像素的图片，就是 1200 万个颜色点排成一个长队。加密做的事，"
         "相当于把队伍的名册随机洗一遍，再按新名册重新站队——颜色没变，站位全变了。")
    hflow(["原始图片", "按随机名册重排像素", "无法辨认的噪点图"],
          width=4.4, cap="加密的基本思路（颜色值不变，只改位置）")
    para("解密就是把这件事倒过来做：用密钥文件里存的“新名册”反推回原来的站位。"
         "所以密钥文件一定要留好，具体见第七章。")

    # ======================================================================
    # 第二章
    # ======================================================================
    doc.add_heading("第二章  用之前先确认三件事", level=1)

    doc.add_heading("2.1  电脑要求", level=2)
    table(
        ["项目", "最低", "建议"],
        [
            ["操作系统", "Windows 10（64 位）", "Windows 10 / 11（64 位）"],
            ["内存", "4 GB", "8 GB 及以上"],
            ["硬盘可用空间", "200 MB", "1 GB 以上（图片文件本身占地方）"],
            ["屏幕分辨率", "1280 × 720", "1920 × 1080 及以上"],
        ],
        widths=[3.2, 5.0, 7.1],
    )
    para("软件界面是固定 600 × 600 的小窗口，低分辨率屏幕上也不会被挤变形。")

    doc.add_heading("2.2  不需要额外安装什么", level=2)
    para("这一点值得单独说：本软件是打包好的独立程序，"
         "该带的运行库都封装在里面了。")
    tip("不用装", "不需要安装 Python，不需要装 Office，不需要.NET，也不需要任何第三方工具；"
                  "更不需要联网激活。解压出来双击就能用。")

    doc.add_heading("2.3  支持哪些图片", level=2)
    table(
        ["类别", "格式", "说明"],
        [
            ["可以加密", "JPG / JPEG / PNG / BMP / GIF", "选择文件时对话框里只列这些"],
            ["加密后输出", "PNG", "无损保存，任何看图软件都能打开"],
            ["解密后输出", "按原始扩展名还原", "原来是 JPG 就还 JPG，颜色模式也一致"],
            ["密钥文件", ".key", "加密时自动生成，解密时必须配上"],
        ],
        widths=[3.0, 5.4, 6.9],
    )
    para("如果你手头的图片格式不在上面（例如 HEIC、RAW），先用系统自带的“画图”"
         "或任何看图软件另存为 JPG／PNG，再拿来加密。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第三章
    # ======================================================================
    doc.add_heading("第三章  拿到软件后怎么跑起来", level=1)

    doc.add_heading("3.1  单文件版与目录版怎么选", level=2)
    para("软件提供了两种打包形式，功能一模一样，选哪个看你更在意什么：")
    table(
        ["", "单文件版（一个 exe）", "目录版（一个文件夹）"],
        [
            ["分发", "就一个文件，微信、网盘都好传", "要整个文件夹一起给，缺文件就会报错"],
            ["启动", "每次先把内容解包到临时目录，约 3 秒", "不解包，1 秒内起来"],
            ["挑剔程度", "临时目录被限制或被安全软件拦住时会启动失败",
             "基本不受这些影响，最稳"],
        ],
        widths=[2.2, 6.5, 6.6],
    )
    tip("怎么选", "自己电脑上长期用，建议用目录版；只是发给别人临时用一下，用单文件版最省事。")

    doc.add_heading("3.2  下载、解压、双击", level=2)
    vflow(["从下载地址取到压缩包（封面下方有链接）",
           "解压到任意文件夹，例如 D:\\软件\\图片加密解密工具",
           "双击 %s" % EXE_NAME,
           "出现 600 × 600 的主窗口，状态栏显示“就绪”"],
          cap="从下载到启动的四步")
    para("解压位置随你，桌面、D 盘、U 盘都行。唯一要避开的是压缩包内部——"
         "直接在压缩包里双击 exe，程序会因为没有可写目录而报错。")

    doc.add_heading("3.3  首次运行的系统提示", level=2)
    para("因为这个程序没有购买商业代码签名证书，前两次运行 Windows 会多问一句，"
         "这属于正常现象：")
    bullet("“Windows 已保护你的电脑”：点“更多信息”，再点“仍要运行”；")
    bullet("“无法验证发布者”：点“运行”即可；")
    bullet("个别安全软件会弹窗询问是否放行，选择“允许”就好。")
    tip("如果被拦住了", "把 exe 换成目录版、或者把整个文件夹加到安全软件的信任列表里，"
                        "一般就不会再问了。")

    doc.add_heading("3.4  启动、退出与卸载", level=2)
    bullet("启动：双击 exe，1～3 秒出现主窗口。")
    bullet("退出：点窗口右上角的 ×。处理过程中直接关闭会中断当前任务，"
           "但不会损坏已经生成好的文件。")
    bullet("卸载：删掉软件文件夹即可。软件不写注册表、不往系统目录里放东西，"
           "不留残留。")

    # ======================================================================
    # 第四章
    # ======================================================================
    doc.add_heading("第四章  界面上一共就这几个东西", level=1)

    doc.add_heading("4.1  主界面", level=2)
    para("软件只有一个窗口，从上到下依次是：存储位置、图片路径、操作选择、"
         "密钥路径（只在解密时出现）、进度条、执行操作／取消、状态栏。")
    figure("图1-主界面.png", 9.4, "主界面（默认停在“加密”状态）")

    doc.add_heading("4.2  各区域做什么", level=2)
    figure("图6-界面操作指引.png", 9.4, "界面主要区域标注")
    table(
        ["编号", "区域", "作用"],
        [
            ["1", "存储位置", "结果显示到哪里，默认是软件目录下的“媒体”文件夹"],
            ["2", "图片路径", "待处理图片的完整路径，可以点“浏览…”选，也可以直接粘贴"],
            ["3", "操作选择", "加密还是解密；选“解密”后会多出一行“密钥路径”"],
            ["4", "进度与状态", "进度条显示百分比，下面一行文字说明当前在做什么"],
        ],
        widths=[1.2, 2.4, 11.7],
    )

    doc.add_heading("4.3  核心控件特写", level=2)
    figure("图5-控件特写.png", 11.0, "操作选择、进度条与两个按钮")

    doc.add_heading("4.4  状态栏的三句话", level=2)
    bullet("“就绪”：当前没有任务，可以开始操作。")
    bullet("“正在加密图片…”／“正在解密图片…”：任务进行中，按钮会变灰。")
    bullet("“加密成功！文件保存在: …”：任务完成，后面跟的是结果目录。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第五章
    # ======================================================================
    doc.add_heading("第五章  加密一张图片", level=1)

    doc.add_heading("5.1  三步总览", level=2)
    para("加密一共就三步，熟练之后十几秒的事：")
    vflow(["选图片", "确认存放位置", "点“执行操作”"],
          note="完成后得到两个文件：加密图和密钥",
          cap="加密的三个步骤")

    doc.add_heading("5.2  第一步：选图片", level=2)
    para("点“图片路径”右侧的“浏览…”按钮，在对话框里找到图片，双击它。")
    para("如果你手上已经有图片的完整路径（比如从资源管理器地址栏复制来的），"
         "也可以直接点一下路径输入框，Ctrl+V 粘进去，省掉翻目录的功夫。")

    doc.add_heading("5.3  第二步：确认存放位置", level=2)
    para("“存储位置”默认是软件目录下的“媒体”文件夹，加密结果会放进它下面的“已加密”子文件夹。"
         "想改就点右边的“选择…”按钮挑一个目录——建议选一个你找得到的地方，"
         "比如“D:\\照片\\加密”。")
    para("存放位置只在点“执行操作”那一刻生效，改完不用额外保存。")

    doc.add_heading("5.4  第三步：点“执行操作”", level=2)
    para("确认“操作选择”停在“加密”，然后点“执行操作”。按钮立刻变灰、"
         "“取消”按钮亮起，进度条开始走。处理完成后会弹出提示窗口，"
         "点“打开文件夹”就能看到结果。")
    figure("图3-加密进行中.png", 9.4, "加密进行中的界面状态")
    figure("图4-完成提示.png", 7.4, "完成后的提示窗口")

    doc.add_heading("5.5  完成后的两个文件", level=2)
    para("“已加密”文件夹里会出现两个配对文件，它们必须一起留着：")
    vflow(["海边日落_加密_20260404103015.png",
           "海边日落_密钥.key"],
          width=9.0)
    table(
        ["文件名里的部分", "含义"],
        [
            ["海边日落", "原文件名，方便你认出它对应哪张图"],
            ["_加密_", "标记这是加密结果而不是原图"],
            ["20260404103015", "处理时间戳：2026 年 04 月 04 日 10:30:15"],
            ["_密钥.key", "密钥文件，解密时要用它"],
        ],
        widths=[4.6, 10.7],
    )

    doc.add_heading("5.6  中途想停怎么办", level=2)
    para("点“取消”按钮，状态栏会显示“正在取消…”，当前这一步做完就停下来，"
         "不会生成不完整的文件。想继续就重新点一次“执行操作”。")

    # ======================================================================
    # 第六章
    # ======================================================================
    doc.add_heading("第六章  把图片还原回来", level=1)

    doc.add_heading("6.1  解密与加密只差一步", level=2)
    para("加密是“按新名册重排”，解密是“按同一份名册排回去”。"
         "所以解密除了要选加密图，还要把密钥文件一并选上——这是两个操作唯一的区别。")
    hflow(["加密图 + 密钥文件", "按密钥反推原顺序", "原始图片"],
          width=4.4, cap="解密的基本思路")

    doc.add_heading("6.2  解密三步走", level=2)
    numbered("在“操作选择”里点“解密”，界面会多出一行“密钥路径”。")
    numbered("“图片路径”选加密后的 PNG，“密钥路径”选同名的 .key 文件。")
    numbered("点“执行操作”，完成后在“已解密”子文件夹里取回图片。")
    figure("图2-解密界面.png", 9.4, "解密状态的界面（多出的“密钥路径”一行）")

    doc.add_heading("6.3  还原失败的三种情况", level=2)
    table(
        ["现象", "多半是原因", "怎么处理"],
        [
            ["提示“操作失败：发生错误: 请选择密钥文件”", "只选了图，没选密钥",
             "补选同名的 .key 文件"],
            ["能生成图片，但画面还是乱的", "用错了别的图的密钥",
             "换成文件名前缀一致的那个 .key"],
            ["提示密钥文件无法读取", "密钥被改动、损坏或换过格式",
             "从备份里找回原始密钥；改过名的密钥要先改回原名"],
        ],
        widths=[5.4, 4.4, 5.5],
    )
    tip("一条经验", "解密是“验证密钥”最靠谱的办法。加密完顺手解一次，"
                    "能还原就说明这对文件没问题，之后再删原图也不迟。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第七章
    # ======================================================================
    doc.add_heading("第七章  密钥文件怎么保管", level=1)

    doc.add_heading("7.1  密钥丢了会怎样", level=2)
    para("这是全书最需要认真看的一节。密钥文件是还原画面的唯一凭据，"
         "软件不会保存副本，也没有任何找回途径。")
    vflow(["加密图 + 密钥文件", "图片完整还原"],
          width=8.8)
    vflow(["只剩加密图（密钥丢了）", "画面永远是噪点，无法还原"],
          width=8.8)
    para("也就是说：密钥丢了，那张加密图就等同于一份没有意义的文件。"
         "原图如果已经删掉，内容就真的找不回来了。")

    doc.add_heading("7.2  建议的备份方式", level=2)
    numbered("加密完成后立刻把 .key 复制一份到别的位置，比如另一块硬盘或 U 盘。")
    numbered("密钥和加密图不要放在同一个文件夹里长期保存，分开存放更安全。")
    numbered("重要资料用“3-2-1”思路：至少 2 份副本、其中 1 份放在离线介质上。")
    numbered("每月挑几张加密图做一次试解密，确认密钥没坏、也没记错位置。")

    doc.add_heading("7.3  四件不要做的事", level=2)
    bullet("不要改密钥文件名——“_密钥”三个字是软件识别它的依据；")
    bullet("不要用记事本打开或另存密钥文件，里面的二进制数据会被破坏；")
    bullet("不要把密钥和加密图打包在同一个压缩包里发给别人，等于把钥匙和锁一起寄出去；")
    bullet("不要对同一张图片反复加密——第二次会覆盖第一次的密钥文件，"
           "先加密的那张图就再也还原不了了。")

    # ======================================================================
    # 第八章
    # ======================================================================
    doc.add_heading("第八章  遇到提示信息怎么办", level=1)

    doc.add_heading("8.1  提示原文对照表", level=2)
    table(
        ["软件里的提示原文", "出现原因", "处理办法"],
        [
            ["请选择图片文件", "没选图就点了“执行操作”", "先用“浏览…”选一张图"],
            ["正在处理中，请稍候…", "上一次任务还没结束",
             "等进度条走完，或点“取消”中止"],
            ["操作失败：发生错误: 请选择密钥文件", "解密时没指定密钥",
             "点“密钥路径”的“浏览…”选 .key 文件"],
            ["操作失败：发生错误: …（其它内容）", "图片打不开、密钥损坏或不匹配",
             "确认图片能正常打开，并核对密钥是否同名配套"],
            ["正在取消…", "你点了“取消”按钮", "如需继续，重新点“执行操作”"],
        ],
        widths=[4.8, 4.4, 6.1],
    )

    doc.add_heading("8.2  常见问题十问十答", level=2)
    para("问一：加密后的图还能被看图软件打开吗？", indent=True)
    para("答：能打开，只是画面成了噪点。文件本身是标准的 PNG，没有加密壳。", indent=True)
    para("问二：解密以后画质会变差吗？", indent=True)
    para("答：不会。软件只挪动像素位置，不动颜色数值，解密结果与原始图片逐像素一致。", indent=True)
    para("问三：为什么加密后的文件反而变大了？", indent=True)
    para("答：噪点图失去了原图的规律，压缩效率变低，再加上统一存成无损 PNG，"
         "所以通常比原 JPG 大一些，属正常。", indent=True)
    para("问四：一次能处理多张图吗？", indent=True)
    para("答：一次一张。多张就多来几轮，加密结果的文件名带时间戳，不会互相覆盖。", indent=True)
    para("问五：同一张图连续加密两次会怎样？", indent=True)
    para("答：加密图不会覆盖，但密钥文件会——第二次的密钥把第一次的顶掉了，"
         "第一张加密图就还原不回来。所以别重复加密。", indent=True)
    para("问六：加密前需要先备份原图吗？", indent=True)
    para("答：建议留到确认能还原之后。先解一次，确认没问题再删原图。", indent=True)
    para("问七：软件会联网或上传我的图片吗？", indent=True)
    para("答：不会。全程在本机完成，软件没有任何联网动作。", indent=True)
    para("问八：能加密 PDF、Word 或者视频吗？", indent=True)
    para("答：不能。本版本只处理图片，也没有视频功能。", indent=True)
    para("问九：换了电脑还能解密吗？", indent=True)
    para("答：能。把 exe、加密图和密钥一起拷过去就行，密钥与电脑无关。", indent=True)
    para("问十：密钥文件能不能自己编辑一下更安全？", indent=True)
    para("答：不能，也不要试。密钥是二进制数据，改一个字节就再也还原不了了。", indent=True)

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第九章
    # ======================================================================
    doc.add_heading("第九章  从头到尾走一遍", level=1)

    doc.add_heading("9.1  例子环境", level=2)
    table(
        ["项目", "本例取值"],
        [
            ["软件位置", "D:\\软件\\图片加密解密工具\\"],
            ["默认存放目录", "D:\\软件\\图片加密解密工具\\媒体\\"],
            ["待处理图片", "D:\\照片\\旅行\\海边日落.jpg（4032 × 3024，约 3.2 MB）"],
        ],
        widths=[3.2, 12.1],
    )

    doc.add_heading("9.2  加密过程", level=2)
    numbered("双击 %s，等主窗口出现，状态栏显示“就绪”。" % EXE_NAME)
    numbered("“存储位置”保持默认，于是结果会写进“媒体\\已加密”。")
    numbered("点“图片路径”的“浏览…”，选中 D:\\照片\\旅行\\海边日落.jpg。")
    numbered("确认“操作选择”为“加密”，点“执行操作”。")
    numbered("进度条走完后弹提示窗口，点“打开文件夹”。")
    para("“已加密”文件夹里出现两个文件：")
    code_block([
        "海边日落_加密_20260404103015.png",
        "海边日落_密钥.key",
    ])
    para("用看图软件打开那张 PNG，画面是一片彩色噪点，尺寸仍是 4032 × 3024。")

    doc.add_heading("9.3  解密过程", level=2)
    numbered("在“操作选择”里点“解密”，界面多出“密钥路径”一行。")
    numbered("“图片路径”选刚才那张加密 PNG。")
    numbered("“密钥路径”选海边日落_密钥.key。")
    numbered("点“执行操作”，完成后点“打开文件夹”。")
    para("“已解密”文件夹里得到：")
    code_block([
        "海边日落_加密_20260404103015_解密_20260404103220.jpg",
    ])
    vflow(["原始图片（海边日落.jpg）",
           "加密 → 海边日落_加密_时间戳.png + 海边日落_密钥.key",
           "解密 → 还原后的 .jpg"],
          cap="本例的文件流转")

    doc.add_heading("9.4  结果对照", level=2)
    table(
        ["环节", "输入", "输出", "检查点"],
        [
            ["加密", "海边日落.jpg", "加密 PNG + 密钥",
             "画面变噪点，尺寸不变"],
            ["解密", "加密 PNG + 密钥", "还原 jpg", "与原图逐像素一致"],
        ],
        widths=[2.2, 3.6, 4.6, 4.9],
    )
    para("两次操作加起来不到两秒——这也是它适合随手用一下的原因。")

    # ======================================================================
    # 第十章
    # ======================================================================
    doc.add_heading("第十章  它是怎么做到的", level=1)

    doc.add_heading("10.1  像素置乱做了什么", level=2)
    para("把图片的像素摊成一排，用随机数生成一张“新名册”，再按名册重新排队。"
         "举个例子，五个像素原本按 1-2-3-4-5 排列：")
    hflow(["1 2 3 4 5", "名册：3 1 5 2 4", "3 1 5 2 4"],
          width=4.2, cap="像素置乱的示意（颜色值不变，位置变了）")
    para("解密时按名册反查：看到排在第 1 位的像素，就知道它原本在第 2 位。"
         "这张名册就是密钥文件里最主要的内容。")

    doc.add_heading("10.2  密钥文件里存了什么", level=2)
    table(
        ["字段", "类型", "含义"],
        [
            ["indices", "整数列表", "置换表：记录每个位置上的像素来自哪里"],
            ["original_mode", "字符串", "原始颜色模式（RGB／RGBA），还原时按它存回"],
            ["original_ext", "字符串", "原始扩展名（.jpg／.png…），还原时保持一致"],
        ],
        widths=[3.2, 2.6, 9.5],
    )
    para("indices 的长度等于图片的像素总数，所以图越大，密钥文件越大——"
         "一张 1200 万像素的照片，密钥大约几十兆。")

    doc.add_heading("10.3  为什么是无损的", level=2)
    para("整个过程中，像素的颜色数值从来没有被修改过，只是换了位置。"
         "解密就是把位置换回去，因此不存在“压缩损失”或“画质下降”一说。"
         "加密输出统一存成 PNG 而不是 JPG，也是因为 JPG 是有损格式，"
         "会给噪点图再压一次，那就真的丢了数据。")

    doc.add_heading("10.4  程序由哪些部分构成", level=2)
    table(
        ["模块", "职责"],
        [
            ["main.py", "程序入口"],
            ["gui.py", "界面布局、事件响应与后台线程"],
            ["theme.py", "配色、字体、控件样式"],
            ["encryption.py", "加密：生成置换表、重排像素、写密钥"],
            ["decryption.py", "解密：读密钥、反推顺序、按原格式存回"],
            ["opencv_accelerator.py", "检测 OpenCL／UMat 是否可用并输出检测结果"],
            ["utils.py", "目录定位、结果文件命名"],
        ],
        widths=[4.4, 10.9],
    )

    doc.add_heading("10.5  关于硬件加速，说实话", level=2)
    para("软件启动时会检测一下这台电脑的显卡加速能力（OpenCL／UMat），"
         "并把结果打印到启动信息里，方便排查环境问题。")
    tip("据实说明", "像素置乱的实际运算由 NumPy 的向量化指令在 CPU 上完成，"
                    "并不依赖显卡。也就是说：检测结果只影响提示信息，"
                    "换一张显卡不会让处理变快或变慢。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第十一章
    # ======================================================================
    doc.add_heading("第十一章  速度、体积与使用建议", level=1)

    doc.add_heading("11.1  一张图大概要多久", level=2)
    para("下面是在一台四核笔记本（8 GB 内存）上的实测值，供你估算：")
    table(
        ["图片规格", "加密", "解密"],
        [
            ["1200 万像素 JPG（约 3 MB）", "不到 1 秒", "不到 1 秒"],
            ["1200 万像素 PNG（约 8 MB）", "约 1 秒", "约 1 秒"],
            ["4000 万像素 PNG（约 40 MB）", "1～3 秒", "1～3 秒"],
            ["1 亿像素 TIFF（约 300 MB）", "10～20 秒", "10～20 秒"],
        ],
        widths=[6.5, 4.4, 4.4],
    )

    doc.add_heading("11.2  影响速度的三个因素", level=2)
    bullet("像素总数：处理耗时大致与像素数量成正比，4000 万像素是 1200 万像素的三倍多。")
    bullet("磁盘速度：几十兆到几百兆的图片读写会成为瓶颈，放在固态硬盘上明显更快。")
    bullet("内存容量：同时打开一张超大图时数组很占内存，内存不足会拖慢整体速度。")

    doc.add_heading("11.3  七条使用建议", level=2)
    numbered("加密前留出足够磁盘空间：无损 PNG 通常比原 JPG 大，按两倍预留比较稳。")
    numbered("处理过程中别关窗口、别拔移动硬盘、别让电脑休眠。")
    numbered("加密图与密钥必须成对保管，只留一个等于没留。")
    numbered("不要把加密图当备份，它一旦损坏，密钥再好也救不回来。")
    numbered("不要二次加密：密钥会互相覆盖，还原时极易出错。")
    numbered("传给别人时，图和密钥分两个渠道发，别放同一个压缩包。")
    numbered("本软件不提供密钥找回，也不保存任何副本，请自己做好备份。")

    # ======================================================================
    # 第十二章
    # ======================================================================
    doc.add_heading("第十二章  目录与文件命名", level=1)

    doc.add_heading("12.1  软件目录长什么样", level=2)
    para("第一次运行后，软件会在自己所在目录下建一个“媒体”文件夹，"
         "加密和解密的结果分别放进两个子文件夹：")
    vflow(["图片加密解密工具\\（软件所在目录）",
           "媒体\\  ← 结果总目录",
           "媒体\\已加密\\  ← 加密图与密钥",
           "媒体\\已解密\\  ← 还原出来的图片"],
          width=10.2, cap="默认的目录结构")
    para("这样安排的好处是不会和软件自身的文件混在一起，整个文件夹拷走也不会丢东西。")

    doc.add_heading("12.2  文件命名规则", level=2)
    code_block([
        "原文件名_加密_年月日时分秒.png     加密结果",
        "原文件名_密钥.key                  密钥文件（不含时间戳）",
        "原文件名_加密_时间戳_解密_时间戳.原扩展名   解密结果",
    ])
    para("加密结果带时间戳，所以同一张图加密多次不会互相覆盖；"
         "而密钥文件不带时间戳，这也是 7.3 节提醒“别重复加密”的原因。")

    doc.add_heading("12.3  改了存放位置之后", level=2)
    para("点“存储位置”右侧的“选择…”可以换目录，软件会在新目录里自动补建"
         "“已加密”和“已解密”两个子文件夹，旧目录里的结果不会跟着搬。"
         "如果新目录不可写（例如放在了只读介质上），软件会退回到"
         "“文档\\媒体”目录，并在状态栏提示实际保存位置。")

    # ======================================================================
    # 第十三章
    # ======================================================================
    doc.add_heading("第十三章  声明与联系方式", level=1)

    doc.add_heading("13.1  版权与开源许可", level=2)
    para("本软件“%s”（版本 %s）由 %s 独立开发完成，其程序代码、界面设计及相关文档的"
         "著作权归开发者所有。" % (SOFTWARE_NAME, SOFTWARE_VERSION, AUTHOR), indent=True)
    para("本软件以 GNU 通用公共许可证第 3 版（GPL-3.0）开源发布：任何人都可以出于任何目的"
         "免费使用、复制、修改和分发本软件（包括商业用途）；但在分发修改版或衍生作品时，"
         "必须同样以 GPL-3.0 授权并提供完整源代码，且需保留版权声明与许可证文本。", indent=True)
    para("开源发布不影响著作权归属：著作权仍归开发者所有，本软件亦已申请软件著作权登记。", indent=True)

    doc.add_heading("13.2  使用声明", level=2)
    para("需要坦白的一点：本软件的加密方式是“像素顺序重排”，"
         "它擅长的是防止别人随手翻看，不是对抗有意的破解。"
         "如果你的图片价值很高、或者对手具备专业能力，"
         "请改用密码学意义上的加密工具（如 VeraCrypt、7-Zip 的 AES-256 加密）。", indent=True)
    bullet("加密处理属于像素重排，不构成对高价值数据的强密码学保护。")
    bullet("软件按现状提供，因误删密钥、磁盘故障等造成的数据丢失，作者不承担责任。")
    bullet("请遵守当地法律法规，不要用它处理你无权处置的内容。")

    doc.add_heading("13.3  联系方式与下载地址", level=2)
    table(
        ["项目", "内容"],
        [
            ["软件名称", SOFTWARE_NAME],
            ["软件版本", SOFTWARE_VERSION],
            ["著作权人", AUTHOR],
            ["下载地址", DOWNLOAD_URL],
            ["提取码", DOWNLOAD_PWD],
            ["项目主页", "https://github.com/jiajingjian/PixelShield"],
            ["开源许可证", "GNU General Public License v3.0（GPL-3.0）"],
            ["反馈方式", "请在项目主页的 Issue 留言，并附上系统版本、图片格式与提示原文"],
        ],
        widths=[3.2, 12.1],
    )

    para()
    para("—— 说明书结束 ——", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

    out_path = os.path.join(OUT_DIR, "说明书-%s%s.docx" % (SOFTWARE_NAME, SOFTWARE_VERSION))
    doc.save(out_path)
    log("已保存: %s" % out_path)
    log("  图共 %d 张（含真实界面截图与示意图）" % fig_state["n"])
    return out_path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    build()
    with open(os.path.join(OUT_DIR, "_说明书生成报告.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(REPORT))
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
