# -*- coding: utf-8 -*-
"""
make_manual_doc.py —— 生成软件著作权登记《说明书》（软件使用说明书）。

依据中国版权保护中心《计算机软件著作权登记指南·所需文件》：
  · 文档每页不少于 30 行；
  · 页眉写明软件名称及版本号，且与申请表一致；
  · 纵向排版，文字从左向右。

文体约定（2026-10 定稿）：
  · 只讲打包后的 exe 怎么用，不含源码运行、Python 安装、pip 等内容；
  · 章节标题用规范的专业表述；
  · 技术说明段落用书面语，操作步骤与提示保留平实口吻，避免刻意口语化；
  · 示意图不插图片，用带边框和底色的单元格当方框、箭头字符连接。
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
        rfonts.set(qn("w:ascii"), name)
        rfonts.set(qn("w:hAnsi"), name)
        rfonts.set(qn("w:cs"), name)
        rfonts.set(qn("w:eastAsia"), FONT_CN_EA)

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
        st.paragraph_format.keep_with_next = True

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
        # 手动编号：向上数紧邻的编号段落得到本项序号，遇到别的内容就从 1 重来。
        # （Word 的 List Number 样式全文共用一个计数序列，会跨小节串号。）
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
        p.paragraph_format.keep_with_next = True
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
    SHADE_MAIN = "E8F1FB"
    SHADE_ALT = "FDF3E3"
    SHADE_WARN = "FDECEC"
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
        """竖向流程：方框 ↓ 方框 ↓ ……（整条流程放在一个表格里，不会与相邻表格粘连）"""
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
        """提示块：小标题 + 说明，带底色，与正文区分"""
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
        ("第一章  软件概述", ""),
        ("  1.1  软件用途", ""),
        ("  1.2  设计背景与原创思路", ""),
        ("  1.3  适用对象", ""),
        ("  1.4  功能范围与使用边界", ""),
        ("  1.5  核心原理", ""),
        ("第二章  运行环境", ""),
        ("  2.1  硬件环境", ""),
        ("  2.2  软件环境", ""),
        ("  2.3  支持的文件格式", ""),
        ("第三章  安装与启动", ""),
        ("  3.1  两种发布形式的选择", ""),
        ("  3.2  获取与运行", ""),
        ("  3.3  首次运行的系统提示", ""),
        ("  3.4  启动、退出与卸载", ""),
        ("第四章  界面说明", ""),
        ("  4.1  主界面布局", ""),
        ("  4.2  界面元素说明", ""),
        ("  4.3  核心控件特写", ""),
        ("  4.4  状态提示说明", ""),
        ("第五章  图片加密操作", ""),
        ("  5.1  操作流程总览", ""),
        ("  5.2  选择待加密图片", ""),
        ("  5.3  确认存储位置", ""),
        ("  5.4  执行加密", ""),
        ("  5.5  输出文件说明", ""),
        ("  5.6  中止正在进行的操作", ""),
        ("第六章  图片解密操作", ""),
        ("  6.1  解密流程概述", ""),
        ("  6.2  解密操作步骤", ""),
        ("  6.3  解密失败的常见原因", ""),
        ("第七章  密钥文件管理", ""),
        ("  7.1  密钥丢失的后果", ""),
        ("  7.2  备份建议", ""),
        ("  7.3  使用禁忌", ""),
        ("第八章  提示信息与故障处理", ""),
        ("  8.1  提示信息对照表", ""),
        ("  8.2  常见问题解答", ""),
        ("第九章  完整操作实例", ""),
        ("  9.1  实例环境", ""),
        ("  9.2  加密过程", ""),
        ("  9.3  解密过程", ""),
        ("  9.4  结果汇总", ""),
        ("第十章  技术原理", ""),
        ("  10.1  像素置乱算法", ""),
        ("  10.2  密钥文件结构", ""),
        ("  10.3  无损还原的原理", ""),
        ("  10.4  程序结构", ""),
        ("  10.5  硬件加速检测说明", ""),
        ("第十一章  性能与使用建议", ""),
        ("  11.1  处理耗时参考", ""),
        ("  11.2  影响速度的因素", ""),
        ("  11.3  使用建议", ""),
        ("第十二章  目录结构与文件命名", ""),
        ("  12.1  目录结构", ""),
        ("  12.2  文件命名规则", ""),
        ("  12.3  变更存储位置的影响", ""),
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
    doc.add_heading("第一章  软件概述", level=1)

    doc.add_heading("1.1  软件用途", level=2)
    para("本软件是一款运行于 Windows 平台的图片加密工具，处理对象为本机图片文件。"
         "加密时按随机规则重新排列图片的像素次序，使画面成为无法辨识的噪点图；"
         "需要查看时，用加密时生成的密钥文件把像素次序还原回来。")
    para("整个处理过程只改变像素的排列位置，不改变像素的颜色数值，因此像素置乱本身是无损的。"
         "输出格式会带来一点差别：原图为 PNG、BMP 等无损格式时，解密结果与原始文件逐像素完全一致；"
         "原图为 JPG 时，解密按原格式写回会重新编码一次，画面与原件在视觉上一致，"
         "像素值存在极小差异（详见 10.3 节）。")
    para("全部运算在本机完成：软件不联网、不上传文件，也无需注册或登录账号。")

    doc.add_heading("1.2  设计背景与原创思路", level=2)
    para("本软件的设计起点是一个很常见的场景。")
    para("把照片存进网盘已经是普遍做法：手机相册自动同步、换机前先备份、"
         "或者把网盘当作第二块硬盘使用。方便之余有一个容易被忽略的问题——"
         "上传的照片是以“明文”保存在服务端的。一旦账号被盗、分享链接被转发，"
         "或者服务端出现异常，这些照片就会以原始画面被人看到，"
         "其中可能含有不宜公开的内容。")
    para("由此产生一个想法：能不能在上传之前，先让图片“看不出内容”？")
    para("顺着这个思路，本软件采用的方案是：不改变图片的颜色数值，"
         "只把像素的排列次序彻底打乱。处理后的画面成为一片彩色噪点，"
         "视觉上接近马赛克效果；而图片的尺寸、格式均保持正常，"
         "可以照常上传，但打开后无法辨识原本的内容。")
    vflow(["手机／电脑中的原图（含隐私内容）",
           "用本软件打乱像素次序",
           "噪点图 → 上传至网盘（即便被获取也无法辨识内容）",
           "需要查看时，将噪点图下载回本机",
           "配合密钥文件还原 → 原图完整恢复"],
          width=10.4, cap="先打乱、再上传、需要时还原")
    para("这里有一个关键点：整个过程只调整像素的位置，不修改颜色数值，"
         "因此还原结果与原始图片完全一致，不会产生画质损失。")
    para("也就是说：网盘只负责“存储”，密钥负责“查看”。两者分离之后，"
         "即使存储环节出现问题，他人得到的也只是一张无法辨识的噪点图。")
    tip("设计初衷",
        "把隐私图片在本地打乱为噪点图后再上传至第三方存储，"
        "使存储环节的泄露不等于内容泄露；需要查看时再用本地密钥还原。"
        "打乱与还原均在本机完成，图片不经过任何外部服务。")

    doc.add_heading("1.3  适用对象", level=2)
    para("本软件适用于以下情形：")
    bullet("需要在个人电脑中长期保存私人照片、家庭影像，并希望避免被他人随手翻看的个人用户；")
    bullet("需要把样片、底稿或未公开素材交付给外部人员，又不希望素材被二次留存的摄影、设计从业者；")
    bullet("需要对取证照片等资料做临时保护，且处理过程必须完全在本地完成的行业用户；")
    bullet("需要在教学或演示场景中，直观展示“像素置乱”效果的教学人员。")
    para("需要说明的是：如果防护目标是具备专业能力的破解者，本软件并不适用，"
         "原因见 13.2 节。")

    doc.add_heading("1.4  功能范围与使用边界", level=2)
    table(
        ["项目", "是否支持", "说明"],
        [
            ["加密图片", "支持", "按随机置换表重排像素，输出无损 PNG"],
            ["解密图片", "支持", "凭密钥文件还原；PNG／BMP 逐像素无损，JPG 视觉一致"],
            ["处理视频", "不支持", "本版本只处理图片，不含视频功能"],
            ["处理 PDF／压缩包", "不支持", "仅识别图片格式，不是通用加密工具"],
            ["抵御专业破解", "不支持", "像素置乱属于内容遮蔽，不是密码学加密"],
            ["联网备份／云同步", "不提供", "软件不联网，密钥由用户自行保管"],
        ],
        widths=[4.2, 2.6, 8.5],
    )

    doc.add_heading("1.5  核心原理", level=2)
    para("以一张 1200 万像素的图片为例：它的像素按行展开后是一个长度 1200 万的序列。"
         "加密所做的，就是生成一张随机置换表，再按这张置换表重新排列像素——"
         "颜色数值不变，排列次序全部改变。")
    hflow(["原始图片", "按随机置换表重排像素", "无法辨识的噪点图"],
          width=4.4, cap="加密的基本思路（颜色值不变，只改位置）")
    para("解密是这一过程的逆运算：用密钥文件中保存的置换表反推出原始次序。"
         "因此密钥文件必须妥善保管，具体见第七章。")

    # ======================================================================
    # 第二章
    # ======================================================================
    doc.add_heading("第二章  运行环境", level=1)

    doc.add_heading("2.1  硬件环境", level=2)
    table(
        ["项目", "最低配置", "建议配置"],
        [
            ["操作系统", "Windows 10（64 位）", "Windows 10 / 11（64 位）"],
            ["内存", "4 GB", "8 GB 及以上"],
            ["硬盘可用空间", "200 MB", "1 GB 以上（另需存放图片本身）"],
            ["屏幕分辨率", "1280 × 720", "1920 × 1080 及以上"],
        ],
        widths=[3.2, 5.0, 7.1],
    )
    para("软件界面为固定 600 × 600 的窗口，在低分辨率屏幕上也不会变形。")

    doc.add_heading("2.2  软件环境", level=2)
    para("本软件以独立可执行程序的形式发布，所需的运行库均已封装在程序内部。")
    tip("无需安装", "不需要安装 Python、Office、.NET 或任何第三方工具，"
                    "也不需要联网激活；下载后直接双击即可运行。")

    doc.add_heading("2.3  支持的文件格式", level=2)
    table(
        ["类别", "格式", "说明"],
        [
            ["输入图片", "JPG / JPEG / PNG / BMP / GIF", "选择文件时对话框只列出这些格式"],
            ["加密输出", "PNG", "无损保存，任何看图软件均可打开"],
            ["解密输出", "按原始扩展名还原", "原始为 JPG 则输出 JPG；PNG／BMP 逐像素一致"],
            ["密钥文件", ".key", "加密时自动生成，解密时必须配套使用"],
        ],
        widths=[3.0, 5.4, 6.9],
    )
    para("若待处理图片不在上述范围内（例如 HEIC、RAW），"
         "可先用系统自带“画图”或其它看图软件另存为 JPG／PNG 后再处理。")
    para("GIF 属于调色板格式，解密时会按 GIF 的调色板写回，建议优先使用 PNG、BMP 或 JPG。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第三章
    # ======================================================================
    doc.add_heading("第三章  安装与启动", level=1)

    doc.add_heading("3.1  两种发布形式的选择", level=2)
    para("下载地址提供的是单文件版：一个可直接运行的可执行程序，下载后无需解压、无需安装。"
         "项目主页另提供目录版，两者功能完全相同：")
    table(
        ["", "单文件版（单个 exe）", "目录版（文件夹）"],
        [
            ["分发", "只有一个文件，便于传输", "需整个文件夹一起复制，缺文件会报错"],
            ["启动", "首次启动约 3 秒", "1 秒内启动"],
            ["环境适应性", "系统临时目录不可写或被安全软件拦截时可能启动失败",
             "基本不受上述影响，稳定性更好"],
        ],
        widths=[2.4, 6.4, 6.5],
    )
    tip("选择建议", "日常使用下载地址里的单文件版即可，下载后直接双击运行；"
                    "若所在环境限制了临时目录，可改用项目主页提供的目录版。")

    doc.add_heading("3.2  获取与运行", level=2)
    vflow(["从封面所列下载地址取得 %s（无需解压）" % EXE_NAME,
           "建议移动到一个固定文件夹，例如 D:\\软件\\图片加密解密工具",
           "双击该文件",
           "出现 600 × 600 的主窗口，状态栏显示“就绪”"],
          cap="从下载到启动的四个步骤")
    para("下载到的文件就是可执行程序本身，双击即可运行。建议把它从“下载”文件夹移动到"
         "一个固定的目录（例如 D:\\软件\\图片加密解密工具\\）长期使用："
         "加密与解密的结果会默认保存在该文件所在目录下，放在固定位置便于日后查找。")
    para("如需经常使用，可右键该文件选择“发送到 → 桌面快捷方式”。")

    doc.add_heading("3.3  首次运行的系统提示", level=2)
    para("由于程序未购买商业代码签名证书，首次运行时 Windows 会给出安全提示，"
         "这属于正常现象：")
    bullet("“Windows 已保护你的电脑”：点击“更多信息”，再点击“仍要运行”；")
    bullet("“无法验证发布者”：点击“运行”即可；")
    bullet("部分安全软件会询问是否放行，选择“允许”。")
    tip("处理建议", "可改用目录版，或把整个文件夹加入安全软件的信任列表，通常不会再提示。")

    doc.add_heading("3.4  启动、退出与卸载", level=2)
    bullet("启动：双击 exe，1～3 秒后出现主窗口。")
    bullet("退出：点击窗口右上角关闭按钮。处理过程中直接关闭会中断当前任务，"
           "已生成的文件不受影响。")
    bullet("卸载：删除该 exe 文件即可。软件不写入注册表、不向系统目录安装文件。"
           "如需一并清理处理结果，再删除同目录下的“媒体”文件夹。")

    # ======================================================================
    # 第四章
    # ======================================================================
    doc.add_heading("第四章  界面说明", level=1)

    doc.add_heading("4.1  主界面布局", level=2)
    para("软件采用单一窗口设计，自上而下依次为：存储位置、图片路径、操作选择、"
         "密钥路径（仅解密时出现）、进度条、执行操作／取消按钮、状态栏。")
    figure("图1-主界面.png", 9.4, "主界面（默认停留在“加密”状态）")

    doc.add_heading("4.2  界面元素说明", level=2)
    figure("图6-界面操作指引.png", 9.4, "界面主要区域标注")
    table(
        ["编号", "区域", "作用"],
        [
            ["1", "存储位置", "结果显示位置，默认为软件目录下的“媒体”文件夹"],
            ["2", "图片路径", "待处理图片的完整路径，可点“浏览…”选择或直接粘贴"],
            ["3", "操作选择", "选择加密或解密；选“解密”后会新增一行“密钥路径”"],
            ["4", "进度与状态", "进度条显示完成百分比，下方文字说明当前步骤"],
        ],
        widths=[1.2, 2.4, 11.7],
    )

    doc.add_heading("4.3  核心控件特写", level=2)
    figure("图5-控件特写.png", 11.0, "操作选择、进度条与两个按钮")

    doc.add_heading("4.4  状态提示说明", level=2)
    bullet("“就绪”：当前无任务，可以开始操作。")
    bullet("“正在加密图片…”／“正在解密图片…”：任务进行中，操作按钮不可用。")
    bullet("“加密成功！文件保存在: …”：任务完成，其后为结果目录路径。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第五章
    # ======================================================================
    doc.add_heading("第五章  图片加密操作", level=1)

    doc.add_heading("5.1  操作流程总览", level=2)
    para("加密操作共三步：")
    vflow(["选择图片", "确认存储位置", "点击“执行操作”"],
          note="完成后得到两个文件：加密图与密钥文件",
          cap="加密的三个步骤")

    doc.add_heading("5.2  选择待加密图片", level=2)
    para("点击“图片路径”右侧的“浏览…”按钮，在文件对话框中选中待加密图片并打开。")
    para("若已持有图片的完整路径（例如从资源管理器地址栏复制），"
         "也可直接点击路径输入框并按 Ctrl+V 粘贴。")

    doc.add_heading("5.3  确认存储位置", level=2)
    para("“存储位置”默认为软件目录下的“媒体”文件夹，加密结果写入其下的“已加密”子目录。"
         "如需更改，点击右侧“选择…”按钮指定新目录，例如“D:\\照片\\加密”。")
    para("存储位置的修改在点击“执行操作”时生效，无需另行保存。")

    doc.add_heading("5.4  执行加密", level=2)
    para("确认“操作选择”为“加密”后点击“执行操作”按钮：该按钮随即变灰，"
         "“取消”按钮转为可用，进度条开始推进。处理完成后弹出提示窗口，"
         "点击“打开文件夹”即可查看结果。")
    figure("图3-加密进行中.png", 9.4, "加密进行中的界面状态")
    figure("图4-完成提示.png", 7.4, "完成后的提示窗口")

    doc.add_heading("5.5  输出文件说明", level=2)
    para("“已加密”文件夹中会生成两个相互对应的文件，两者必须一并保留：")
    vflow(["海边日落_加密_20260404103015.png",
           "海边日落_密钥.key"],
          width=9.0)
    table(
        ["文件名组成部分", "含义"],
        [
            ["海边日落", "原文件名，便于识别对应的原始图片"],
            ["_加密_", "标识这是加密结果而非原图"],
            ["20260404103015", "处理时间戳：2026 年 04 月 04 日 10:30:15"],
            ["_密钥.key", "密钥文件，解密时使用"],
        ],
        widths=[4.6, 10.7],
    )

    doc.add_heading("5.6  中止正在进行的操作", level=2)
    para("点击“取消”按钮后，状态栏显示“正在取消…”，当前步骤结束后停止，"
         "不会生成不完整的文件；如需继续，重新点击“执行操作”即可。")

    # ======================================================================
    # 第六章
    # ======================================================================
    doc.add_heading("第六章  图片解密操作", level=1)

    doc.add_heading("6.1  解密流程概述", level=2)
    para("加密是按置换表重新排列像素，解密是按同一张置换表反向还原。"
         "因此解密除选定加密图外，还需一并指定密钥文件——这是两种操作唯一的区别。")
    hflow(["加密图 + 密钥文件", "按密钥反推原始次序", "原始图片"],
          width=4.4, cap="解密的基本思路")

    doc.add_heading("6.2  解密操作步骤", level=2)
    numbered("在“操作选择”中点击“解密”，界面会新增一行“密钥路径”。")
    numbered("“图片路径”选择加密后的 PNG 文件，“密钥路径”选择同名的 .key 文件。")
    numbered("点击“执行操作”，完成后在“已解密”子文件夹中取回图片。")
    figure("图2-解密界面.png", 9.4, "解密状态的界面（新增“密钥路径”一行）")

    doc.add_heading("6.3  解密失败的常见原因", level=2)
    table(
        ["现象", "原因", "处理办法"],
        [
            ["提示“操作失败：发生错误: 请选择密钥文件”", "只选择了图片，未指定密钥",
             "补选同名的 .key 文件"],
            ["能生成图片，但画面仍是错乱的", "使用了其它图片的密钥",
             "改用文件名前缀一致的那个 .key 文件"],
            ["提示密钥文件无法读取", "密钥被改动、损坏或格式不符",
             "从备份中找回原始密钥；改过名的密钥需改回原名"],
        ],
        widths=[5.4, 4.4, 5.5],
    )
    tip("经验提示", "解密是验证密钥是否可用的最直接办法：加密后立即试解一次，"
                    "能完整还原即说明这对文件没有问题，之后再删除原图更为稳妥。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第七章
    # ======================================================================
    doc.add_heading("第七章  密钥文件管理", level=1)

    doc.add_heading("7.1  密钥丢失的后果", level=2)
    para("本节是本手册最需要注意的一节。密钥文件是还原画面的唯一凭据，"
         "软件不保存任何副本，也没有找回途径。")
    vflow(["加密图 + 密钥文件", "图片完整还原"],
          width=8.8)
    vflow(["仅剩加密图（密钥已丢失）", "画面始终为噪点，无法还原"],
          width=8.8)
    para("也就是说：密钥一旦丢失，对应的加密图就等同于一份无意义的文件；"
         "若原图也已删除，内容将无法恢复。")

    doc.add_heading("7.2  备份建议", level=2)
    numbered("加密完成后，立即把 .key 文件复制一份到其它位置（例如另一块硬盘或 U 盘）。")
    numbered("密钥与加密图不建议长期存放在同一文件夹内，分开保存更安全。")
    numbered("重要资料可采用“3-2-1”思路：至少 2 份副本，其中 1 份放在离线介质上。")
    numbered("定期抽查几张加密图做一次试解密，确认密钥完好、位置记录无误。")

    doc.add_heading("7.3  使用禁忌", level=2)
    bullet("不要修改密钥文件名——“_密钥”三个字是软件识别它的依据；")
    bullet("不要用文本编辑器打开或另存密钥文件，其中的二进制数据会被破坏；")
    bullet("不要把密钥与加密图放在同一个压缩包中发送，等同于把钥匙和锁一并寄出；")
    bullet("不要对同一张图片重复加密：第二次加密会覆盖第一次的密钥文件，"
           "先前生成的加密图将无法还原。")

    # ======================================================================
    # 第八章
    # ======================================================================
    doc.add_heading("第八章  提示信息与故障处理", level=1)

    doc.add_heading("8.1  提示信息对照表", level=2)
    table(
        ["软件提示原文", "出现原因", "处理办法"],
        [
            ["请选择图片文件", "未选择图片就点击了“执行操作”", "先用“浏览…”选定图片"],
            ["正在处理中，请稍候…", "上一次任务尚未结束",
             "等待进度条走完，或点击“取消”中止"],
            ["操作失败：发生错误: 请选择密钥文件", "解密时未指定密钥文件",
             "点击“密钥路径”的“浏览…”选择 .key 文件"],
            ["操作失败：发生错误: …（其它内容）", "图片无法打开、密钥损坏或不匹配",
             "确认图片可正常打开，并核对密钥是否同名配套"],
            ["正在取消…", "用户点击了“取消”按钮", "如需继续，重新点击“执行操作”"],
        ],
        widths=[4.8, 4.4, 6.1],
    )

    doc.add_heading("8.2  常见问题解答", level=2)
    para("问一：加密后的图片还能被看图软件打开吗？", indent=True)
    para("答：可以打开，只是画面成为噪点。文件本身是标准 PNG，没有额外加密外壳。", indent=True)
    para("问二：解密以后画质会变差吗？", indent=True)
    para("答：像素置乱本身是无损的。原图为 PNG、BMP 等无损格式时，解密结果与原件逐像素完全一致；"
         "原图为 JPG 时，解密按原格式写回会重新编码一次，画面与原件视觉一致，"
         "像素值最多相差几个色阶。", indent=True)
    para("问三：为什么加密后的文件大了这么多？", indent=True)
    para("答：一是噪点图失去了原有的规律性，PNG 压缩率很低；二是密钥文件记录了整张置换表，"
         "体积与像素总数成正比。以 1200 万像素的照片为例，加密图约 33 MB、密钥约 57 MB，"
         "合计约为原 JPG 的几十倍，属正常现象。", indent=True)
    para("问四：一次可以处理多张图片吗？", indent=True)
    para("答：一次处理一张。多张图片可分多次操作，加密结果的文件名带时间戳，不会互相覆盖。", indent=True)
    para("问五：同一张图片连续加密两次会怎样？", indent=True)
    para("答：加密图不会互相覆盖，但密钥文件会——第二次的密钥会覆盖第一次的，"
         "先前那张加密图将无法还原。因此不建议重复加密。", indent=True)
    para("问六：加密前需要先备份原图吗？", indent=True)
    para("答：建议保留原图至确认可还原之后。先试解一次，确认无误再删除原图。", indent=True)
    para("问七：软件会联网或上传我的图片吗？", indent=True)
    para("答：不会。全部处理在本机完成，软件没有任何联网行为。", indent=True)
    para("问八：可以加密 PDF、Word 或视频吗？", indent=True)
    para("答：不可以。本版本只处理图片，也不含视频功能。", indent=True)
    para("问九：更换电脑后还能解密吗？", indent=True)
    para("答：可以。把 exe、加密图与密钥一并复制到新电脑即可，密钥与设备无关。", indent=True)
    para("问十：可以自行编辑密钥文件吗？", indent=True)
    para("答：不可以，也不建议尝试。密钥是二进制数据，改动一个字节即无法还原。", indent=True)

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第九章
    # ======================================================================
    doc.add_heading("第九章  完整操作实例", level=1)

    doc.add_heading("9.1  实例环境", level=2)
    table(
        ["项目", "本例取值"],
        [
            ["软件位置", "D:\\软件\\图片加密解密工具\\"],
            ["默认存储目录", "D:\\软件\\图片加密解密工具\\媒体\\"],
            ["待处理图片", "D:\\照片\\旅行\\海边日落.jpg（4032 × 3024，约 3.2 MB）"],
        ],
        widths=[3.2, 12.1],
    )

    doc.add_heading("9.2  加密过程", level=2)
    numbered("双击 %s，等待主窗口出现，状态栏显示“就绪”。" % EXE_NAME)
    numbered("“存储位置”保持默认，结果将写入“媒体\\已加密”。")
    numbered("点击“图片路径”的“浏览…”，选中 D:\\照片\\旅行\\海边日落.jpg。")
    numbered("确认“操作选择”为“加密”，点击“执行操作”。")
    numbered("进度条走完后弹出提示窗口，点击“打开文件夹”。")
    para("“已加密”文件夹中生成以下两个文件：")
    code_block([
        "海边日落_加密_20260404103015.png",
        "海边日落_密钥.key",
    ])
    para("用看图软件打开该 PNG，画面为彩色噪点，尺寸仍为 4032 × 3024。")

    doc.add_heading("9.3  解密过程", level=2)
    numbered("在“操作选择”中点击“解密”，界面新增“密钥路径”一行。")
    numbered("“图片路径”选择上一步生成的加密 PNG。")
    numbered("“密钥路径”选择海边日落_密钥.key。")
    numbered("点击“执行操作”，完成后点击“打开文件夹”。")
    para("“已解密”文件夹中得到还原后的图片：")
    code_block([
        "海边日落_加密_20260404103015_解密_20260404103220.jpg",
    ])
    vflow(["原始图片（海边日落.jpg）",
           "加密 → 海边日落_加密_时间戳.png 与 海边日落_密钥.key",
           "解密 → 还原后的 .jpg"],
          cap="本例的文件流转")

    doc.add_heading("9.4  结果汇总", level=2)
    table(
        ["环节", "输入", "输出", "检查点"],
        [
            ["加密", "海边日落.jpg", "加密 PNG 与密钥文件",
             "画面变为噪点，尺寸不变"],
            ["解密", "加密 PNG 与密钥", "还原后的 jpg 文件", "画面与原图一致（JPG 写回，差异极小）"],
        ],
        widths=[2.0, 3.5, 4.8, 5.0],
    )
    para("两次操作合计耗时不到两秒，适合日常随手处理。")

    # ======================================================================
    # 第十章
    # ======================================================================
    doc.add_heading("第十章  技术原理", level=1)

    doc.add_heading("10.1  像素置乱算法", level=2)
    para("先把图片的像素矩阵展开为一维序列，用随机数生成置换表，再按置换表重新排列。"
         "以五个像素为例，原本按 1-2-3-4-5 排列：")
    hflow(["1 2 3 4 5", "置换表：3 1 5 2 4", "3 1 5 2 4"],
          width=4.2, cap="像素置乱示意（颜色值不变，位置改变）")
    para("解密时按置换表反查：排在第 1 位的像素原本位于第 2 位。"
         "这张置换表就是密钥文件中最主要的内容。")

    doc.add_heading("10.2  密钥文件结构", level=2)
    table(
        ["字段", "类型", "含义"],
        [
            ["indices", "整数列表", "置换表，记录每个位置上的像素来自何处"],
            ["original_mode", "字符串", "原始颜色模式（RGB／RGBA），还原时按它写回"],
            ["original_ext", "字符串", "原始扩展名（.jpg／.png 等），还原时保持一致"],
        ],
        widths=[3.2, 2.6, 9.5],
    )
    para("indices 的长度等于图片的像素总数，因此图片越大，密钥文件越大——"
         "实测一张 1200 万像素的照片，密钥文件约 57 MB；2400 万像素约 114 MB。")

    doc.add_heading("10.3  无损还原的原理", level=2)
    para("整个过程中像素的颜色数值从未被修改，改变的只是位置，解密即把位置还原，"
         "因此像素置乱本身不引入任何损失。加密结果统一保存为 PNG 而非 JPG，"
         "原因是 JPG 属有损格式，会对噪点图再次压缩，造成真实的数据损失。")
    para("解密环节的差别来自输出格式：原图为 PNG、BMP 时按原格式无损写回，"
         "实测与原件逐像素完全一致；原图为 JPG 时，写回会以画质 95 重新编码一次，"
         "实测像素值最大相差 7 个色阶，画面上看不出区别，但严格说不是逐位相同。"
         "若对逐像素一致性有要求，可先把图片另存为 PNG 再加密。")

    doc.add_heading("10.4  程序结构", level=2)
    table(
        ["模块", "职责"],
        [
            ["main.py", "程序入口"],
            ["gui.py", "界面布局、事件响应与后台线程"],
            ["theme.py", "配色、字体与控件样式"],
            ["encryption.py", "加密：生成置换表、重排像素、写入密钥"],
            ["decryption.py", "解密：读取密钥、反推次序、按原格式写回"],
            ["opencv_accelerator.py", "检测 OpenCL／UMat 是否可用并输出检测结果"],
            ["utils.py", "目录定位与结果文件命名"],
        ],
        widths=[4.4, 10.9],
    )

    doc.add_heading("10.5  硬件加速检测说明", level=2)
    para("软件启动时会检测本机的显卡加速能力（OpenCL／UMat），"
         "并将结果打印到启动信息中，便于排查运行环境问题。")
    tip("说明", "像素置乱的实际运算由 NumPy 的向量化指令在 CPU 上完成，不依赖显卡。"
                "检测结果仅影响启动信息，更换显卡不会改变处理速度。")

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # ======================================================================
    # 第十一章
    # ======================================================================
    doc.add_heading("第十一章  性能与使用建议", level=1)

    doc.add_heading("11.1  处理耗时参考", level=2)
    para("下表为四核处理器、8 GB 内存环境下的实测值（含输出体积），供估算参考：")
    table(
        ["图片规格", "加密图", "密钥文件", "加密耗时", "解密耗时"],
        [
            ["1200 万像素（4000 × 3000，约 2 MB JPG）", "约 33 MB", "约 57 MB", "约 2 秒", "约 1.5 秒"],
            ["2400 万像素（6000 × 4000，约 4 MB JPG）", "约 67 MB", "约 114 MB", "约 4 秒", "约 3 秒"],
            ["4000 万像素（按比例估算）", "约 110 MB", "约 190 MB", "约 7 秒", "约 5 秒"],
            ["1 亿像素（按比例估算）", "约 280 MB", "约 480 MB", "约 18 秒", "约 13 秒"],
        ],
        widths=[6.0, 2.3, 2.6, 2.3, 2.2],
    )
    tip("空间提醒", "加密图与密钥文件的体积都远大于原图：可按“每百万像素约 8 MB”预留空间"
                    "（加密图与密钥合计），一张 1200 万像素照片约需 90 MB。")

    doc.add_heading("11.2  影响速度的因素", level=2)
    bullet("像素总量：处理耗时与像素数量近似成正比，4000 万像素约为 1200 万像素的三倍。")
    bullet("磁盘速度：读取数十至数百兆的图片时，机械硬盘可能成为瓶颈，固态硬盘明显更快。")
    bullet("内存容量：处理超大尺寸图片时像素数组占用内存较多，内存不足会拖慢整体速度。")

    doc.add_heading("11.3  使用建议", level=2)
    numbered("加密前预留足够的磁盘空间：加密图与密钥文件合计约为“每百万像素 8 MB”，"
             "1200 万像素的照片约需 90 MB。")
    numbered("处理过程中不要关闭窗口、拔出移动硬盘或让电脑休眠。")
    numbered("加密图与密钥文件必须成对保管，只保留其中一个等同于没有保留。")
    numbered("不要把加密图当作备份：文件一旦损坏，密钥完好也无法还原。")
    numbered("不要二次加密：密钥会相互覆盖，还原时极易出错。")
    numbered("传输给他人时，图片与密钥分两个渠道发送，不要放在同一个压缩包内。")
    numbered("本软件不提供密钥找回功能，也不保存任何副本，请自行做好备份。")

    # ======================================================================
    # 第十二章
    # ======================================================================
    doc.add_heading("第十二章  目录结构与文件命名", level=1)

    doc.add_heading("12.1  目录结构", level=2)
    para("首次运行后，软件会在 exe 文件所在目录下创建“媒体”文件夹，"
         "加密与解密结果分别存放在两个子目录中：")
    vflow(["exe 所在目录（例如 D:\\软件\\图片加密解密工具\\）",
           "媒体\\  ← 结果总目录",
           "媒体\\已加密\\  ← 加密图与密钥文件",
           "媒体\\已解密\\  ← 还原后的图片"],
          width=10.2, cap="默认的目录结构")
    para("这样安排可以避免结果文件与程序文件混放，整个文件夹复制到别处也不会丢失数据。")

    doc.add_heading("12.2  文件命名规则", level=2)
    code_block([
        "原文件名_加密_年月日时分秒.png         加密结果",
        "原文件名_密钥.key                      密钥文件（不含时间戳）",
        "原文件名_加密_时间戳_解密_时间戳.原扩展名   解密结果",
    ])
    para("加密结果带时间戳，因此同一张图片多次加密不会互相覆盖；"
         "而密钥文件不带时间戳，这也是 7.3 节建议不要重复加密的原因。")

    doc.add_heading("12.3  变更存储位置的影响", level=2)
    para("点击“存储位置”右侧的“选择…”可以更换目录，软件会在新目录中自动创建"
         "“已加密”与“已解密”两个子文件夹，原目录中的结果不会随之迁移。"
         "若新目录不可写（例如位于只读介质），软件会退回到“文档\\媒体”目录，"
         "并在状态栏提示实际保存位置。")

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
    para("需要说明的是：本软件的加密方式为像素次序重排，"
         "其定位是防止他人随手查看，并非对抗有意的破解。"
         "若图片价值较高，或对手具备专业能力，"
         "建议改用密码学意义上的加密工具（如 VeraCrypt、7-Zip 的 AES-256 加密）。", indent=True)
    bullet("加密处理属于像素置乱，不构成对高价值数据的强密码学保护。")
    bullet("软件按现状提供；因误删密钥、磁盘故障等造成的数据丢失，作者不承担责任。")
    bullet("请遵守当地法律法规，不要处理无权处置的内容。")

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
