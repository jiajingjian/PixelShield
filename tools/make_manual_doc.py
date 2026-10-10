# -*- coding: utf-8 -*-
"""
make_manual_doc.py —— 生成软件著作权登记《说明书》（软件使用说明书/用户手册）。

依据中国版权保护中心《计算机软件著作权登记指南·所需文件》：
  · 文档每页不少于 30 行；
  · 页眉写明软件名称及版本号，且与申请表一致；
  · 纵向排版，文字从左向右。

本说明书按「软件用途、运行环境、安装卸载、功能操作、异常处理」组织，
并插入真实运行界面截图。
"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "软著")
IMG_DIR = os.path.join(OUT_DIR, "图片")

SOFTWARE_NAME = "图片加密解密工具"
SOFTWARE_VERSION = "V1.0.0"
AUTHOR = "贾京健"

# 封面中部用大号红字展示的软件下载地址
DOWNLOAD_URL = "https://pan.quark.cn/s/78b1c38cc2d7?pwd=Pj1G"
DOWNLOAD_PWD = "Pj1G"

HEADER_TEXT = "%s %s" % (SOFTWARE_NAME, SOFTWARE_VERSION)
DOC_TITLE = "%s\n软件使用说明书" % SOFTWARE_NAME

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

    # 页眉下划线
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
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        p.paragraph_format.line_spacing = 1.2
        r = p.add_run(text)
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
        caption(cap)

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
                # 单元格内用软换行表示多行内容
                lines = str(val).split("\n")
                p = cells[i].paragraphs[0]
                p.paragraph_format.space_after = Pt(1)
                r = p.add_run(lines[0])
                set_run(r, size=9.5)
                for extra in lines[1:]:
                    r.add_break()
                    r2 = p.add_run(extra)
                    set_run(r2, size=9.5)
        # 表格行不跨页断开，且表头之后紧跟首行
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
    # 目录（静态）
    # ======================================================================
    doc.add_heading("目  录", level=1)
    toc = [
        ("第一章  软件概述", ""),
        ("  1.1  软件简介", ""),
        ("  1.2  开发目的与适用对象", ""),
        ("  1.3  主要功能", ""),
        ("  1.4  软件特点", ""),
        ("第二章  运行环境", ""),
        ("  2.1  硬件环境", ""),
        ("  2.2  软件环境", ""),
        ("  2.3  支持的文件格式", ""),
        ("第三章  安装与卸载", ""),
        ("  3.1  安装步骤", ""),
        ("  3.2  启动与退出", ""),
        ("  3.3  卸载方法", ""),
        ("第四章  界面说明", ""),
        ("  4.1  主界面布局", ""),
        ("  4.2  界面元素说明", ""),
        ("第五章  功能操作说明", ""),
        ("  5.1  图片加密", ""),
        ("  5.2  图片解密", ""),
        ("  5.3  变更存储目录", ""),
        ("  5.4  中止正在进行的操作", ""),
        ("第六章  密钥文件管理", ""),
        ("  6.1  密钥文件的生成与保存", ""),
        ("  6.2  密钥文件的保管要求", ""),
        ("  6.3  密钥丢失的后果", ""),
        ("第七章  异常情况与处理", ""),
        ("  7.1  常见提示信息", ""),
        ("  7.2  常见问题解答", ""),
        ("第八章  技术原理与说明", ""),
        ("  8.1  软件结构", ""),
        ("  8.2  图片加密原理", ""),
        ("  8.3  性能优化", ""),
        ("第九章  完整操作实例", ""),
        ("  9.1  实例环境", ""),
        ("  9.2  图片加密与解密全流程", ""),
        ("  9.3  实例结果汇总", ""),
        ("第十章  安装结果验证", ""),
        ("  10.1  验证清单", ""),
        ("  10.2  逐项验证方法", ""),
        ("  10.3  源码方式的功能自检", ""),
        ("第十一章  性能与注意事项", ""),
        ("  11.1  处理耗时参考", ""),
        ("  11.2  影响速度的因素", ""),
        ("  11.3  使用注意事项", ""),
        ("第十二章  技术架构说明", ""),
        ("  12.1  总体架构", ""),
        ("  12.2  关键数据结构", ""),
        ("  12.3  命名与目录约定", ""),
        ("  12.4  容错与降级策略", ""),
        ("第十三章  声明与联系方式", ""),
        ("  13.1  版权声明", ""),
        ("  13.2  使用声明", ""),
        ("  13.3  技术支持", ""),
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
    doc.add_heading("1.1  软件简介", level=2)
    para("“%s”（以下简称“本软件”）是一款运行于 Windows 平台的桌面应用程序，"
         "用于对本地图片文件进行加密与解密处理，防止私密影像资料在存储、"
         "传输和共享过程中被他人直接查看。" % SOFTWARE_NAME)
    para("本软件采用图形化窗口界面，全部操作通过鼠标点击完成，无需记忆命令行参数，"
         "也无需具备密码学专业知识。用户只需选定待处理文件、指定保存目录，"
         "点击“执行操作”按钮即可完成加密或解密。")
    para("本软件的核心思路是：加密并非销毁原始数据，而是将文件中像素的排列次序"
         "按照随机规则彻底打乱，使画面成为无法辨识的杂乱噪点；解密时依据加密时"
         "生成的密钥文件还原像素次序，即可完整恢复原始画面。整个过程不改变像素"
         "的颜色数值，因此解密后的文件与原始文件完全一致，属于无损处理。")

    doc.add_heading("1.2  开发目的与适用对象", level=2)
    para("随着数码相机、手机和运动相机的普及，个人电脑中积累的私人照片日益增多。"
         "这类文件通常以明文形式保存在硬盘中，一旦电脑被他人临时使用、送修或文件被"
         "整体拷贝，隐私内容便会直接暴露。本软件的开发目的，是为普通用户提供一种"
         "操作简单、立即可用的本地文件保护手段，在不依赖网络和云服务的前提下，"
         "把敏感影像转换为不可直接观看的形式。")
    para("本软件适用于以下对象：")
    bullet("需要在个人电脑中长期保存私人照片、家庭影像，并希望避免被他人随手翻看的个人用户；")
    bullet("需要把样片、底稿或未公开素材交付给外部人员，又不希望素材被二次留存的摄影、设计从业者；")
    bullet("需要对取证照片等资料做临时保护，且处理过程必须完全在本地完成的行业用户；")
    bullet("需要在教学或演示场景中，直观展示“像素置乱”效果的教学人员。")

    doc.add_heading("1.3  主要功能", level=2)
    table(
        ["序号", "功能名称", "功能说明"],
        [
            ["1", "图片加密", "对 JPG、PNG、BMP 等格式的图片执行像素置乱加密，"
                            "输出加密图片与配套密钥文件。"],
            ["2", "图片解密", "依据密钥文件还原加密图片，恢复原始画面与原始格式。"],
            ["3", "存储目录自定义", "用户可自行指定加密结果与解密结果的保存位置。"],
            ["4", "实时进度显示", "以进度条与百分比文字实时反映处理进度。"],
            ["5", "操作中止", "处理过程中可随时点击“取消”按钮中止任务。"],
            ["6", "结果直达", "操作完成后自动弹出提示窗口，可一键打开输出文件夹。"],
            ["7", "硬件加速检测", "启动时检测 OpenCL / UMat 是否可用，"
                              "并在控制台打印检测结果与所选后端。"],
        ],
        widths=[1.4, 3.4, 10.5],
    )

    doc.add_heading("1.4  软件特点", level=2)
    bullet("本地处理，不联网：全部加解密运算在本机完成，文件内容不经过任何网络传输，不存在上传泄露风险。")
    bullet("无损还原：加密与解密均不改变像素颜色数值，解密结果与原始文件完全一致。")
    bullet("操作简单：单一窗口、三步操作，无需命令行与配置文件。")
    bullet("绿色免安装：不写注册表、不向系统目录安装文件，复制文件夹即可整体迁移。")
    bullet("依赖精简：仅依赖 NumPy、OpenCV 与 Pillow 三个基础库，"
           "无需另行安装任何外部程序，部署方便。")

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第二章
    # ======================================================================
    doc.add_heading("第二章  运行环境", level=1)

    doc.add_heading("2.1  硬件环境", level=2)
    table(
        ["项目", "最低配置", "推荐配置"],
        [
            ["处理器", "双核 1.6 GHz 及以上", "四核 2.4 GHz 及以上"],
            ["内存", "2 GB", "8 GB 及以上"],
            ["硬盘可用空间", "200 MB", "1 GB 及以上"],
            ["显示分辨率", "1024 × 768", "1366 × 768 及以上"],
            ["显卡", "无特殊要求", "支持 OpenCL 的显卡可提升处理速度"],
        ],
        widths=[3.0, 5.5, 6.8],
    )

    doc.add_heading("2.2  软件环境", level=2)
    table(
        ["项目", "要求"],
        [
            ["操作系统", "Windows 7 / 8 / 8.1 / 10 / 11（32 位或 64 位）"],
            ["运行方式", "① 直接运行打包后的可执行程序（免安装）；"
                       "② 以 Python 解释器运行源代码"],
            ["Python 版本", "Python 3.7 及以上（源码方式运行时需要）"],
            ["图形界面库", "Tkinter（Python 标准库自带）"],
            ["第三方依赖", "NumPy 2.0 及以上；OpenCV（opencv_python）；Pillow"],
        ],
        widths=[3.0, 12.3],
    )
    para("说明：以源码方式运行时，在项目根目录执行以下命令安装依赖：", indent=True)
    code_block([
        "pip install -r requirements.txt",
    ])
    para("requirements.txt 内容如下：", indent=True)
    code_block([
        "numpy>=2.0,<2.3.0",
        "opencv_python==4.12.0.88",
        "Pillow==12.2.0",
    ])

    doc.add_heading("2.3  支持的文件格式", level=2)
    table(
        ["类别", "支持格式", "说明"],
        [
            ["图片输入", "JPG / JPEG / PNG / BMP / GIF", "加密后统一输出为 PNG 无损格式"],
            ["加密输出", "PNG", "标准 PNG 图片，任何看图软件均可打开"],
            ["解密输出", "按原始扩展名还原", "与原始图片的颜色模式、扩展名保持一致"],
            ["密钥文件", ".key", "加密时自动生成，解密时必须选用对应文件"],
        ],
        widths=[2.6, 6.2, 6.5],
    )

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第三章
    # ======================================================================
    doc.add_heading("第三章  安装与卸载", level=1)

    doc.add_heading("3.1  安装步骤", level=2)
    para("本软件为绿色免安装软件，提供两种使用方式。")

    doc.add_heading("方式一：运行打包后的可执行程序（推荐普通用户使用）", level=3)
    numbered("在发布目录（dist 文件夹）中找到可执行文件“图片加密解密工具1.0.0.exe”。")
    numbered("将该文件复制到本机任意目录，例如“D:\\软件\\图片加密解密工具”。")
    numbered("双击该文件即可启动软件，无需安装、无需配置环境变量。")
    para("提示：首次运行时，Windows 可能弹出“无法验证发布者”或“Windows 已保护你的电脑”"
         "提示，点击“运行”或“更多信息”→“仍要运行”即可。", indent=True)

    doc.add_heading("方式二：以 Python 源码方式运行（适合开发与调试）", level=3)
    numbered("在本机安装 Python 3.7 或更高版本，安装时勾选“Add Python to PATH”。")
    numbered("把项目全部源码复制到本机，保留 src 目录以及 requirements.txt 等文件的相对位置。")
    numbered("在项目根目录打开命令提示符，执行 pip install -r requirements.txt 安装依赖库。")
    numbered("在项目根目录执行 python src/main.py 启动软件。")
    para("源码组织方式：程序源代码统一放在 src 目录下，包括 main.py（程序入口）、gui.py、"
         "theme.py、encryption.py、decryption.py、opencv_accelerator.py、utils.py。", indent=True)

    doc.add_heading("3.2  启动与退出", level=2)
    bullet("启动：双击可执行文件，或在项目根目录执行 python src/main.py，"
           "稍候约 1～3 秒即出现主窗口，状态栏显示“就绪”。")
    bullet("退出：点击主窗口右上角的关闭按钮（×），或先中止正在进行的任务再关闭窗口。")
    bullet("注意：图片加解密过程中直接关闭窗口会中断当前任务，不会生成完整的结果文件。")

    doc.add_heading("3.3  卸载方法", level=2)
    numbered("可执行程序方式：直接删除可执行文件所在文件夹即可，软件不写注册表，"
             "不向系统目录安装任何文件。")
    numbered("源码方式：删除源码目录，并卸载已安装的第三方依赖库"
             "（如需彻底清理，可执行 pip uninstall numpy opencv_python Pillow）。")
    numbered("如需同时删除处理结果，请一并删除“媒体”文件夹（见 5.3 节）。")

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第四章
    # ======================================================================
    doc.add_heading("第四章  界面说明", level=1)

    doc.add_heading("4.1  主界面布局", level=2)
    para("软件采用单一窗口设计，窗口固定为 600 × 600 像素，不可缩放。"
         "所有功能集中在一个界面内，自上而下依次为：标题、存储位置区、"
         "图片路径区、操作选择区、密钥路径区（仅在解密时出现）、"
         "进度显示区、操作按钮区和状态提示区。")
    figure("图1-主界面.png", 9.6, "图 1  软件主界面（默认为“加密”状态）")

    doc.add_heading("4.2  界面元素说明", level=2)
    para("为便于对照，下图以红色标注框标出了界面中几个主要操作区域及其编号。")
    figure("图6-界面操作指引.png", 9.6, "图 2  界面主要操作区域标注图")

    table(
        ["编号", "区域名称", "说明"],
        [
            ["1", "存储目录", "显示当前的结果保存目录，默认位于软件目录下的“媒体”文件夹。"
                            "点击右侧“选择...”按钮可改为其他目录。"],
            ["2", "图片路径", "显示待加密或待解密的图片完整路径。"
                            "点击右侧“浏览...”按钮选择图片，也可手工粘贴路径。"],
            ["3", "操作选择", "选择执行“加密”还是“解密”。选择“解密”后，"
                            "界面会新增一行“密钥路径”。"],
            ["4", "进度与状态", "进度条显示整体完成百分比；下方状态文字显示"
                             "当前正在执行的步骤或结果提示。"],
        ],
        widths=[1.3, 2.7, 11.3],
    )
    para("下图为核心控件的局部特写，可见“操作选择”“进度条”"
         "以及“执行操作 / 取消”按钮的相对位置。", indent=True)
    figure("图5-控件特写.png", 11.5, "图 3  核心控件局部特写")

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第五章
    # ======================================================================
    doc.add_heading("第五章  功能操作说明", level=1)

    doc.add_heading("5.1  图片加密", level=2)
    para("图片加密用于把一张普通图片转换为无法辨认的噪点图，并生成对应的密钥文件。"
         "操作步骤如下：")
    numbered("启动软件。主界面默认处于“加密”状态。")
    numbered("在“存储位置”区域确认保存目录。默认目录为“媒体”文件夹，"
             "加密结果将保存在其下的“已加密”子文件夹中。如需更改，点击“选择...”按钮指定新目录。")
    numbered("点击“图片路径”右侧的“浏览...”按钮，在弹出的文件选择对话框中选择待加密的图片，"
             "点击“打开”。此时图片完整路径显示在输入框中。")
    numbered("确认“操作选择”为“加密”。")
    numbered("点击“执行操作”按钮。按钮随即变为不可用，“取消”按钮变为可用，进度条开始推进，"
             "状态栏依次显示“正在加密图片...”“加密成功！文件保存在: …”等提示。")
    numbered("处理完成后弹出提示窗口，显示加密结果所在目录。点击“打开文件夹”可直接"
             "在资源管理器中定位到该目录，点击“关闭”返回主界面。")
    figure("图3-加密进行中.png", 9.6, "图 4  图片加密进行中的界面状态")

    para("处理结果：在“已加密”文件夹中生成两个文件——", indent=True)
    bullet("加密图片：文件名为“原文件名_加密_年月日时分秒.png”，内容为像素被置乱后的图像。")
    bullet("密钥文件：文件名为“原文件名_密钥.key”，记录还原像素次序所需的数据。")

    doc.add_heading("5.2  图片解密", level=2)
    para("图片解密用于把加密图片还原为原始画面。操作步骤如下：")
    numbered("启动软件，在“操作选择”中选择“解密”。此时界面会新增一行“密钥路径”。")
    numbered("点击“图片路径”右侧的“浏览...”按钮，选择待解密的加密图片（.png 文件）。")
    numbered("点击“密钥路径”右侧的“浏览...”按钮，选择加密时生成的同名“.key”密钥文件。")
    numbered("点击“执行操作”按钮，等待处理完成。")
    numbered("在提示窗口中点击“打开文件夹”，在“已解密”子文件夹中查看还原后的图片。")
    figure("图2-解密界面.png", 9.6, "图 5  解密状态的界面（新增“密钥路径”一行）")

    para("处理结果：在“已解密”文件夹中生成还原后的图片，文件名为"
         "“原文件名_解密_年月日时分秒 + 原始扩展名”，画面内容与加密前完全一致。", indent=True)
    para("说明：密钥文件与加密图片必须一一对应。若选用了其他图片的密钥文件，"
         "软件会执行还原运算，但得到的画面仍是错乱的；若密钥文件本身损坏，"
         "软件将弹出“操作失败”提示。", indent=True)

    doc.add_heading("5.3  变更存储目录", level=2)
    para("软件默认在自身目录下建立“媒体”文件夹，并在其中建立两个子文件夹：", indent=True)
    table(
        ["文件夹", "用途"],
        [
            ["媒体", "结果总目录，可在界面中修改"],
            ["媒体\\已加密", "存放加密后的图片与密钥文件"],
            ["媒体\\已解密", "存放解密还原后的图片"],
        ],
        widths=[4.5, 10.8],
    )
    para("修改方法：点击“存储位置”右侧的“选择...”按钮，在目录选择对话框中指定新的文件夹，"
         "软件会立即切换到该目录，并在其中自动创建“已加密”和“已解密”两个子文件夹。"
         "也可以直接在输入框中手工输入或粘贴路径，该路径将在点击“执行操作”时生效。", indent=True)

    doc.add_heading("5.4  中止正在进行的操作", level=2)
    para("加密或解密过程中，主界面上的“取消”按钮由灰色变为可用。点击该按钮后，"
         "状态栏显示“正在取消...”，当前任务会在完成当前步骤后停止，"
         "“执行操作”按钮恢复可用，进度条保持不变。此时不会生成完整的结果文件。", indent=True)

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第六章
    # ======================================================================
    doc.add_heading("第六章  密钥文件管理", level=1)

    doc.add_heading("6.1  密钥文件的生成与保存", level=2)
    para("每次执行加密操作时，软件都会自动生成一个与该文件对应的密钥文件，"
         "扩展名为“.key”，并与加密结果保存在同一个“已加密”文件夹中。"
         "密钥文件与加密文件通过文件名相互对应，例如：", indent=True)
    code_block([
        "示例图片_加密_20260404120000.png     加密后的图片",
        "示例图片_密钥.key                     对应的密钥文件",
    ])
    para("密钥文件记录像素的置乱次序、原始颜色模式和原始扩展名。"
         "它本身不包含原始画面，无法从中恢复出图像内容。", indent=True)

    doc.add_heading("6.2  密钥文件的保管要求", level=2)
    bullet("加密后请立即把密钥文件与加密文件一并备份，建议分别保存在不同位置。")
    bullet("不要修改密钥文件的扩展名和文件名。文件名中的“密钥”二字是识别依据，"
           "改名虽不影响解密，但容易与加密文件失去对应关系。")
    bullet("不要使用文本编辑器打开或保存密钥文件，以免破坏其中的二进制数据。")
    bullet("若密钥文件需要通过不可信渠道传递，建议单独加密后再发送，"
           "不要把密钥文件与加密文件放在同一个压缩包中一并发送。")

    doc.add_heading("6.3  密钥丢失的后果", level=2)
    para("密钥文件是还原画面的唯一凭据。软件不保存密钥副本，也不提供任何找回途径。"
         "一旦密钥文件被删除、损坏或丢失，对应的加密文件将无法通过本软件还原，"
         "画面将永久保持置乱状态。因此，强烈建议在加密完成后立即备份密钥文件，"
         "并且在删除原始文件之前，先用解密功能验证一次密钥是否可用。", indent=True)

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第七章
    # ======================================================================
    doc.add_heading("第七章  异常情况与处理", level=1)

    doc.add_heading("7.1  常见提示信息", level=2)
    table(
        ["提示信息", "出现原因", "处理方法"],
        [
            ["请选择图片文件", "未选择待处理图片就点击了“执行操作”。",
             "先点击“浏览...”按钮选定图片。"],
            ["正在处理中，请稍候...", "上一次任务尚未结束。",
             "等待进度条走完，或点击“取消”中止当前任务。"],
            ["操作失败 发生错误: 请选择密钥文件", "选择“解密”后未指定密钥文件。",
             "点击“密钥路径”右侧的“浏览...”按钮选择 .key 文件。"],
            ["操作失败 发生错误: …", "图片无法打开、密钥文件损坏，或密钥与加密图片不匹配。",
             "确认图片能正常打开；确认所选 .key 与加密图片一一对应。"],
            ["正在取消... / 操作已取消", "用户点击了“取消”按钮。",
             "如需继续，请重新点击“执行操作”。"],
        ],
        widths=[4.0, 5.2, 6.1],
    )

    doc.add_heading("7.2  常见问题解答", level=2)
    para("问一：加密后的图片还能被图片浏览器打开吗？", indent=True, bold=False)
    para("答：可以打开，但画面显示为无法辨认的彩色噪点。软件把加密结果保存为标准 PNG "
         "格式，其目的正是让加密文件在任何看图软件中都“打得开、看不懂”。", indent=True)
    para("问二：加密会降低画质吗？", indent=True)
    para("答：不会。加密过程只调整像素的排列次序，不改变任何像素的颜色数值；"
         "解密时按相反次序放回原位。图片解密时按原格式保存，JPEG 以质量 95 重新编码。", indent=True)
    para("问三：可以一次加密多个文件吗？", indent=True)
    para("答：当前版本一次处理一个文件。如需处理多个文件，可依次重复操作；"
         "由于加密结果的文件名带时间戳，多次处理不会互相覆盖。", indent=True)
    para("问四：加密后需要保留原始文件吗？", indent=True)
    para("答：建议先保留。请在确认加密文件与密钥文件都能正常解密还原之后，"
         "再决定是否删除原始文件。", indent=True)
    para("问五：同一张图片连续加密两次会怎样？", indent=True)
    para("答：加密结果的文件名带时间戳，不会互相覆盖；但密钥文件的文件名不含时间戳，"
         "第二次加密会覆盖第一次生成的密钥文件，导致先生成的加密图片无法再还原。"
         "请避免对同一张图片重复加密，或在加密后立即完成一次解密验证。", indent=True)
    para("问六：软件需要联网吗？会上传我的文件吗？", indent=True)
    para("答：不需要联网，也不会上传任何文件。加密与解密全部在本机完成，"
         "软件不与外部网络发生任何数据交换。", indent=True)

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第八章
    # ======================================================================
    doc.add_heading("第八章  技术原理与说明", level=1)

    doc.add_heading("8.1  软件结构", level=2)
    para("软件采用模块化设计，各模块职责单一、相互独立，通过函数调用组合为完整流程。", indent=True)
    table(
        ["序号", "源文件", "主要职责"],
        [
            ["1", "main.py", "程序入口，创建主窗口并启动界面事件循环"],
            ["2", "gui.py", "图形界面，负责控件布局、用户交互、后台线程调度"],
            ["3", "utils.py", "目录管理、时间戳与结果文件命名等公共工具"],
            ["4", "theme.py", "界面主题，统一管理配色、字体、间距与控件样式"],
            ["5", "encryption.py", "图片加密算法实现"],
            ["6", "decryption.py", "图片解密算法实现"],
            ["7", "opencv_accelerator.py", "OpenCL / UMat 硬件加速可用性检测"],
        ],
        widths=[1.3, 5.5, 8.5],
    )

    doc.add_heading("8.2  图片加密原理", level=2)
    para("图片在计算机中以像素矩阵的形式保存，每个像素包含红、绿、蓝（及透明）分量。"
         "图片加密的做法是：读入图片后，把二维像素矩阵展开为一维序列，"
         "生成一个与原像素数量相同的随机下标序列，再按下标序列重新排列像素，"
         "最后把重排结果保存为 PNG 图片。像素的颜色值没有改变，只是位置被彻底打乱。", indent=True)
    para("加密流程如下：", indent=True)
    code_block([
        "读入原始图片  →  记录原始颜色模式与扩展名",
        "              →  展开为像素序列（宽度 × 高度）",
        "              →  生成随机下标序列并写入密钥文件",
        "              →  按随机下标重排像素",
        "              →  保存为 PNG 加密图片",
    ])
    para("解密是其逆过程：读取密钥文件中的下标序列，求出其逆排列，"
         "按逆排列把像素放回原始位置，再按密钥中记录的原始颜色模式与扩展名保存，"
         "即得到与原始文件一致的画面。", indent=True)

    doc.add_heading("8.3  性能优化", level=2)
    bullet("向量化运算：使用 NumPy 与 OpenCV 的整块数组运算代替逐像素循环，"
           "处理一张普通照片仅需数十毫秒。")
    bullet("硬件加速检测：启动时检测 OpenCL 与 UMat 是否可用，并把检测结果与"
           "所选后端打印到控制台（源码方式运行时可见）；像素置乱运算由 NumPy 的"
           "向量化指令在 CPU 上完成，不依赖显卡性能。")
    bullet("界面不卡顿：加解密任务在独立的后台线程中执行，"
           "通过线程安全队列把进度和结果回传界面，保证窗口始终可以响应。")
    bullet("不做多余拷贝：加密与解密直接在内存中的像素数组上完成重排，"
           "不生成中间图片文件，减少磁盘读写。")

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第九章
    # ======================================================================
    doc.add_heading("第九章  完整操作实例", level=1)
    para("为使操作步骤更加直观，本章给出一个从加密到解密验证的完整实例。"
         "实例中的目录与文件名为实际运行时软件生成的结果，可直接对照检查。", indent=True)

    doc.add_heading("9.1  实例环境", level=2)
    table(
        ["项目", "取值"],
        [
            ["软件存放位置", "D:\\软件\\图片加密解密工具\\"],
            ["默认存储目录", "D:\\软件\\图片加密解密工具\\媒体\\"],
            ["测试图片", "D:\\照片\\旅行\\海边日落.jpg（4032 × 3024，3.2 MB）"],
        ],
        widths=[3.2, 12.1],
    )

    doc.add_heading("9.2  图片加密与解密全流程", level=2)
    para("第一步，启动软件。双击“图片加密解密工具1.0.0.exe”，等待主窗口出现。"
         "窗口标题为“图片加密解密工具”，状态栏显示“就绪”，进度条为空。", indent=True)
    para("第二步，确认存储目录。界面“存储目录”一栏默认显示软件所在目录下的“媒体”文件夹。"
         "本实例保留默认值，因此加密结果将写入“媒体\\已加密”。", indent=True)
    para("第三步，选择待加密图片。点击“图片路径”右侧的“浏览...”按钮，"
         "在对话框中定位到 D:\\照片\\旅行\\，选中“海边日落.jpg”，点击“打开”。"
         "此时输入框中显示完整路径 D:\\照片\\旅行\\海边日落.jpg。", indent=True)
    para("第四步，执行加密。确认“操作选择”为“加密”，然后点击“执行操作”按钮。"
         "按钮立即变灰，“取消”按钮变亮，进度条从 0% 推进到 100%，"
         "状态栏依次显示“正在加密图片...”与“加密成功！文件保存在: D:\\软件\\"
         "图片加密解密工具\\媒体\\已加密”。", indent=True)
    para("第五步，查看结果。处理完成后弹出提示窗口，点击“打开文件夹”，"
         "资源管理器会定位到“已加密”文件夹，可以看到以下两个文件：", indent=True)
    code_block([
        "海边日落_加密_20260404103015.png     像素被置乱后的图片",
        "海边日落_密钥.key                    还原所需的密钥",
    ])
    para("此时用任意看图工具打开加密图片，可见画面已成为无法辨认的彩色噪点，"
         "但文件能够正常打开、尺寸与原始图片完全一致（4032 × 3024）。", indent=True)
    para("第六步，切换到解密。在主界面“操作选择”区域点击“解密”，"
         "界面随即在“图片路径”下方新增一行“密钥路径”，此时“执行操作”按钮保持可用。", indent=True)
    para("第七步，选择加密图片与密钥。点击“图片路径”右侧的“浏览...”按钮，"
         "选中上一步生成的“海边日落_加密_20260404103015.png”；"
         "再点击“密钥路径”右侧的“浏览...”按钮，选中“海边日落_密钥.key”。"
         "两行输入框均应显示完整路径，缺一不可。", indent=True)
    para("第八步，执行解密。点击“执行操作”，等待进度条走完。"
         "状态栏显示“解密成功！文件保存在: D:\\软件\\图片加密解密工具\\媒体\\已解密”。"
         "点击提示窗口中的“打开文件夹”，可以看到：", indent=True)
    code_block([
        "海边日落_加密_20260404103015_解密_20260404103220.jpg",
    ])
    para("第九步，比对验证。用看图工具打开解密后的图片，画面应与原始照片完全一致；"
         "再对比两者的像素尺寸，应同为 4032 × 3024。至此，图片加解密的闭环验证完成。", indent=True)

    doc.add_heading("9.3  实例结果汇总", level=2)
    table(
        ["步骤", "输入", "输出", "说明"],
        [
            ["图片加密", "海边日落.jpg", "海边日落_加密_时间戳.png\n海边日落_密钥.key",
             "画面置乱，尺寸与格式不变"],
            ["图片解密", "加密 png + 密钥", "…_解密_时间戳.jpg", "画面完全还原，逐像素一致"],
        ],
        widths=[2.2, 3.4, 5.6, 4.1],
    )

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第十章
    # ======================================================================
    doc.add_heading("第十章  安装结果验证", level=1)
    para("为确保软件安装正确、依赖完整，可按本章步骤逐项验证。", indent=True)

    doc.add_heading("10.1  验证清单", level=2)
    table(
        ["序号", "验证项", "预期结果"],
        [
            ["1", "程序能否启动", "双击后 3 秒内出现主窗口，无报错弹窗"],
            ["2", "界面是否完整", "可见存储位置、图片路径、操作选择、"
                                "进度条与两个按钮"],
            ["3", "存储目录是否自动创建", "软件目录下出现“媒体\\已加密”与“媒体\\已解密”"],
            ["4", "图片加密是否成功", "生成加密 png 与 .key 两个文件"],
            ["5", "密钥是否可用", "用同一密钥解密后画面与原始图片逐像素一致"],
            ["6", "硬件加速检测是否正常", "启动信息中出现“选择的硬件加速后端: OpenCL”"],
            ["7", "取消功能是否有效", "处理中点击“取消”，状态栏显示“正在取消...”并停止"],
        ],
        widths=[1.3, 4.2, 9.8],
    )

    doc.add_heading("10.2  逐项验证方法", level=2)
    para("验证项 1 与 2：启动软件后，对照本说明书第四章的界面说明逐项核对控件是否齐全。"
         "若窗口空白或缺少控件，通常是 Python 环境下 Tkinter 组件缺失所致。", indent=True)
    para("验证项 3：首次启动后检查软件所在目录，应自动生成“媒体”文件夹及其下的"
         "“已加密”“已解密”两个子文件夹；若未生成，请确认软件所在目录具有写入权限。", indent=True)
    para("验证项 4 与 5：按第九章的实例步骤加密一张小尺寸图片，再立即解密，"
         "用看图工具比对新旧图片的尺寸与画面。这是最重要的一项验证，"
         "建议对每一个需要长期保存的加密文件都执行一次。", indent=True)
    para("验证项 6：以源码方式在命令行启动软件，观察启动时打印的检测信息：", indent=True)
    code_block([
        "OpenCL 硬件加速可用",
        "OpenCV UMat 硬件加速可用",
        "选择的硬件加速后端: OpenCL",
    ])
    para("若显示“未检测到可用的 OpenCV 硬件加速后端”，属正常情况："
         "本软件的像素置乱运算由 NumPy 的向量化指令在 CPU 上完成，"
         "该检测结果只影响启动信息中的显示，不影响任何功能。", indent=True)
    para("验证项 7：加密一张尺寸较大的图片，在处理过程中点击“取消”按钮，"
         "状态栏应显示“正在取消...”，随后停止处理并恢复按钮状态。", indent=True)

    doc.add_heading("10.3  源码方式的功能自检", level=2)
    para("以源码方式部署时，软件附带一个模块自检脚本 simple_test.py，"
         "用于确认各功能模块能否正常导入。在项目根目录执行：", indent=True)
    code_block([
        "python src/simple_test.py",
    ])
    para("预期输出如下：", indent=True)
    code_block([
        "Testing image encryption/decryption module loading...",
        "[OK] encryption loaded successfully",
        "[OK] decryption loaded successfully",
        "[OK] opencv_accelerator loaded successfully",
        "OpenCV hardware acceleration available: True",
        "[OK] gui loaded successfully",
        "",
        "Test complete!",
    ])
    para("若某一项显示 [FAIL]，说明对应的依赖库缺失或版本不匹配，"
         "请按提示的异常信息安装相应依赖后重新自检。", indent=True)

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第十一章
    # ======================================================================
    doc.add_heading("第十一章  性能与注意事项", level=1)

    doc.add_heading("11.1  处理耗时参考", level=2)
    para("下表为常见文件在四核处理器、8 GB 内存环境下的实测耗时范围，"
         "仅供估算，实际耗时与文件尺寸、编码方式及磁盘速度有关。", indent=True)
    table(
        ["文件类型", "规格", "处理环节", "参考耗时"],
        [
            ["图片", "1200 万像素 JPG（3 MB）", "加密", "不足 1 秒"],
            ["图片", "1200 万像素 JPG（3 MB）", "解密", "不足 1 秒"],
            ["图片", "4000 万像素 PNG（40 MB）", "加密", "1～3 秒"],
            ["图片", "4000 万像素 PNG（40 MB）", "解密", "1～3 秒"],
            ["图片", "1 亿像素 TIFF（300 MB）", "加密", "约 10～20 秒"],
        ],
        widths=[2.2, 4.6, 3.4, 5.1],
    )

    doc.add_heading("11.2  影响速度的因素", level=2)
    bullet("像素总量：处理耗时与图片像素总数近似成正比，4000 万像素图片的数据量"
           "是 1200 万像素的三倍以上。")
    bullet("显卡与驱动：启动时会检测 OpenCL / UMat 是否可用并显示检测结果；"
           "像素置乱运算在 CPU 上完成，不依赖显卡性能。")
    bullet("磁盘读写速度：机械硬盘在读写数十兆的大图时可能成为瓶颈，"
           "建议把存储目录设在固态硬盘上。")
    bullet("内存容量：处理超大尺寸图片时像素数组占用内存较多，"
           "内存不足会导致系统频繁换页而变慢。")

    doc.add_heading("11.3  使用注意事项", level=2)
    numbered("加密前请确认磁盘剩余空间充足。加密结果保存为无损 PNG 格式，"
             "文件通常比原始 JPG 更大，建议预留原始文件两倍以上的空间。")
    numbered("处理过程中不要关闭窗口、不要拔出移动硬盘，也不要让电脑进入休眠状态，"
             "否则可能产生不完整的输出文件。")
    numbered("加密结果文件与密钥文件必须成对保管。只保留加密文件而丢失密钥文件，"
             "等同于丢失原始文件。")
    numbered("不要把加密文件当作“已完成备份”。加密文件一旦损坏，"
             "即使密钥完好也无法还原，重要资料仍应保留原始副本。")
    numbered("加密后的文件不要再次加密。重复加密会使密钥与文件不再一一对应，"
             "还原时需要按相反顺序逐层解密，极易出错。")
    numbered("分享加密文件时，不要把密钥文件放在同一个压缩包或同一封邮件中，"
             "应通过不同渠道分别传递。")
    numbered("本软件不提供密钥找回功能，也不保存任何密钥副本，请自行做好备份。")

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第十二章
    # ======================================================================
    doc.add_heading("第十二章  技术架构说明", level=1)

    doc.add_heading("12.1  总体架构", level=2)
    para("软件采用分层结构：界面层负责与用户交互，业务层负责编排加解密流程，"
         "算法层负责具体的像素运算，基础层提供目录、命名、主题与硬件检测等公共服务。"
         "各层之间通过函数调用联系，不共享全局状态，便于单独测试与替换。", indent=True)
    code_block([
        "┌─────────────────────────────────────────────┐",
        "│  界面层   gui.py / theme.py                  │",
        "│  控件布局、事件响应、后台线程、进度回传        │",
        "└───────────────────┬─────────────────────────┘",
        "                    │ 函数调用",
        "┌───────────────────┴─────────────────────────┐",
        "│  业务层   encryption / decryption            │",
        "│  编排加密与解密流程、写入密钥文件              │",
        "└───────────────────┬─────────────────────────┘",
        "                    │",
        "┌───────────────────┴─────────────────────────┐",
        "│  算法层   opencv_accelerator                  │",
        "│  像素置乱、硬件加速可用性检测                  │",
        "└───────────────────┬─────────────────────────┘",
        "                    │",
        "┌───────────────────┴─────────────────────────┐",
        "│  基础层   utils.py（目录、命名、时间戳）       │",
        "└─────────────────────────────────────────────┘",
    ])

    doc.add_heading("12.2  关键数据结构", level=2)
    para("本软件使用密钥文件保存还原所需的信息。为便于说明，以下列出密钥文件"
         "实际保存的字段及其含义。", indent=True)
    para("图片加密生成的密钥文件保存以下三个字段：", indent=True)
    table(
        ["字段名", "类型", "含义"],
        [
            ["indices", "整数列表", "置乱后的像素下标序列，长度等于像素总数"],
            ["original_mode", "字符串", "原始图片的颜色模式，如 RGB 或 RGBA"],
            ["original_ext", "字符串", "原始文件的扩展名，如 .jpg 或 .png"],
        ],
        widths=[3.4, 2.8, 9.1],
    )
    para("其中 indices 字段是一张置换表：加密时按下标序列重排像素，解密时求其"
         "逆排列即可还原。该字段的长度等于图片的像素总数，因此密钥文件的大小"
         "随图片尺寸增大而增大。解密时，软件还会读取 original_mode 与 original_ext "
         "字段，按原始颜色模式与扩展名保存还原结果，从而保证解密图片与原始图片完全一致。", indent=True)

    doc.add_heading("12.3  命名与目录约定", level=2)
    para("软件通过固定的命名规则把输入文件、输出文件与密钥文件关联起来。"
         "命名规则如下：", indent=True)
    code_block([
        "加密结果：  <原文件名>_加密_<年月日时分秒>.<扩展名>",
        "解密结果：  <原文件名>_解密_<年月日时分秒>.<扩展名>",
        "密钥文件：  <原文件名>_密钥.key",
        "",
        "示例：",
        "  原文件      海边日落.jpg",
        "  加密结果    海边日落_加密_20260404103015.png",
        "  密钥文件    海边日落_密钥.key",
        "  解密结果    海边日落_解密_20260404103220.jpg",
    ])
    para("时间戳精确到秒，因此同一文件多次加密不会互相覆盖。"
         "密钥文件不带时间戳，同一原文件再次加密会覆盖上一次的密钥文件，"
         "此时旧的加密文件将无法再用新密钥还原，请务必注意。", indent=True)

    doc.add_heading("12.4  容错与降级策略", level=2)
    table(
        ["异常情形", "软件的应对方式", "对用户的影响"],
        [
            ["硬件加速不可用", "启动信息中提示未检测到可用后端", "功能完全不受影响"],
            ["输出目录不存在", "自动创建目录后再写入", "无"],
            ["输出目录不可写", "回退到“文档\\媒体”目录", "结果保存在用户文档目录下"],
            ["图片格式无法识别", "弹出“操作失败”提示并说明原因", "无输出文件"],
            ["密钥文件损坏或不匹配", "弹出“操作失败”提示，不写出错误结果", "无输出文件"],
            ["用户点击取消", "在当前步骤结束后停止，不写最终结果", "无输出文件"],
        ],
        widths=[3.6, 7.2, 4.5],
    )

    pass  # 章节之间不再强制分页，由排版引擎连续排版

    # ======================================================================
    # 第十三章
    # ======================================================================
    doc.add_heading("第十三章  声明与联系方式", level=1)

    doc.add_heading("13.1  版权声明", level=2)
    para("本软件“%s”（版本 %s）由 %s 独立开发完成，其程序代码、界面设计及相关文档的"
         "著作权归开发者所有。" % (SOFTWARE_NAME, SOFTWARE_VERSION, AUTHOR), indent=True)
    para("本软件以 GNU 通用公共许可证第 3 版（GPL-3.0）开源发布：任何人都可以出于任何目的"
         "免费使用、复制、修改和分发本软件（包括商业用途）；但在分发修改版或衍生作品时，"
         "必须同样以 GPL-3.0 授权并提供完整源代码，且需保留版权声明与许可证文本。", indent=True)
    para("开源发布不影响著作权归属：著作权仍归开发者所有，本软件亦已申请软件著作权登记。", indent=True)

    doc.add_heading("13.2  使用声明", level=2)
    bullet("本软件仅供用户对自己合法持有或已获授权的文件进行加密与解密处理。")
    bullet("用户应自行确保待处理文件的来源合法，不得利用本软件从事任何违法活动。")
    bullet("密钥文件由用户自行保管，因密钥丢失、损坏或误删导致的数据无法恢复，"
           "由用户自行承担。")
    bullet("加密处理属于像素重排，不构成对高价值数据的强密码学保护。"
           "对于涉及重大利益的数据，建议配合专业加密工具使用。")
    bullet("建议在任何情况下保留原始文件副本，直至确认解密还原成功。")

    doc.add_heading("13.3  技术支持", level=2)
    table(
        ["项目", "内容"],
        [
            ["软件名称", SOFTWARE_NAME],
            ["软件版本", SOFTWARE_VERSION],
            ["著作权人", AUTHOR],
            ["项目主页", "https://github.com/jiajingjian/PixelShield"],
            ["开源许可证", "GNU General Public License v3.0（GPL-3.0）"],
            ["反馈方式", "请在项目主页（GitHub 仓库的 Issue）留言反馈，并提供"
                       "操作系统版本、图片格式与提示信息原文"],
        ],
        widths=[3.4, 11.9],
    )

    para()
    para("—— 说明书结束 ——", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)

    out_path = os.path.join(OUT_DIR, "说明书-%s%s.docx" % (SOFTWARE_NAME, SOFTWARE_VERSION))
    doc.save(out_path)
    log("已保存: %s" % out_path)
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
