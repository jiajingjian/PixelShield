# -*- coding: utf-8 -*-
"""
make_source_doc.py —— 生成软件著作权登记《源程序》鉴别材料。

规则依据（中国版权保护中心《计算机软件著作权登记指南·所需文件》）：
  · 一般交存：源程序前、后各连续 30 页；不足 60 页的，全部提交；
  · 程序每页不少于 50 行；
  · 页眉须写明软件名称及版本号，且与申请表一致；
  · 纵向排版，文字从左向右。

本脚本做法：
  · 源程序不足 60 页，因此全部提交；
  · 按固定 50 行/页排版，并在每页末尾插入分页符，保证「每页不少于 50 行」；
  · 页眉：图片加密解密工具 V1.0.0；页脚：第 X 页（自动域）；
  · 空行折叠，避免出现整页不足 50 行的情况。
"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "软著")

SOFTWARE_NAME = "图片加密解密工具"
SOFTWARE_VERSION = "V1.0.0"
PAGE_HEADER = "%s %s" % (SOFTWARE_NAME, SOFTWARE_VERSION)

LINES_PER_PAGE = 50          # 每页排入 50 行，页码与行号均从 1 重新开始
REQUIRED_MIN_LINES = 50      # 登记要求：程序每页不少于 50 行
MAX_CHARS_PER_LINE = 102     # 含行号的行宽上限（行号 4 + 2 空格 + 代码 96）
                             # 实测 8pt Consolas 在 17.8cm 宽度内可容纳约 100 字符
                             # （见 tools/calibrate_wrap.py），此处留出安全余量
SEP_LEN = 60                 # 分隔线长度，避免过宽导致折行
LINENO_WIDTH = 4             # 行号字段宽度（右对齐）
LINENO_PREFIX = LINENO_WIDTH + 2          # 行号 + 两个空格
MAX_CODE_CHARS = MAX_CHARS_PER_LINE - LINENO_PREFIX   # 代码本身允许的最大宽度
CODE_FONT = "Consolas"
CODE_SIZE_PT = 8
LINE_SPACING_PT = 11.5

# 提交顺序：入口 → 基础设施 → 主题 → 核心算法 → 界面 → 未纳入主流程的历史模块
# 源码位于 src/ 下，此处的相对路径是相对项目根目录的
SOURCE_FILES = [
    "src/main.py",
    "src/utils.py",
    "src/theme.py",
    "src/encryption.py",
    "src/decryption.py",
    "src/opencv_accelerator.py",
    "src/gui.py",
]

# 未纳入当前主流程、仅供归档的历史脚本（放在文档最后，与主程序区分）
ARCHIVE_FILES = [
    "src/simple_test.py",
]

REPORT = []


def log(msg):
    print(msg, flush=True)
    REPORT.append(str(msg))


def read_source(rel_path):
    path = os.path.join(PROJECT_DIR, rel_path)
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    return raw.replace("\t", "    ").split("\n")


def collect_lines():
    """返回 (逻辑行列表, 统计信息)"""
    out = []
    stats = []
    out.append("=" * SEP_LEN)
    out.append("源程序清单（本软件全部源程序不足 60 页，按登记指南规定全部提交）")
    out.append("软件名称：%s    版本号：%s" % (SOFTWARE_NAME, SOFTWARE_VERSION))
    out.append("=" * SEP_LEN)
    out.append("")

    for rel in SOURCE_FILES + ARCHIVE_FILES:
        path = os.path.join(PROJECT_DIR, rel)
        lines = read_source(rel)
        physical = len(lines)
        kept = 0

        out.append("-" * SEP_LEN)
        out.append("// 源文件：%s" % rel)
        out.append("-" * SEP_LEN)

        for line in lines:
            s = line.rstrip()
            if s.strip() == "":
                continue  # 折叠空行，保证每页行数达标
            out.append(s)
            kept += 1

        out.append("")
        out.append("// 源文件 %s 结束" % rel)
        out.append("")
        stats.append((rel, physical, kept))
        log("  %-32s 物理行 %4d → 收录 %4d 行" % (rel, physical, kept))

    return out, stats


def current_lines(text, width=MAX_CODE_CHARS):
    """按等宽字体估算显示行数：中文/全角字符按 2 个字符宽度计。"""
    if not text:
        return 1
    w = 0
    for ch in text:
        w += 2 if ord(ch) > 0x2E7F else 1
    return max(1, (w + width - 1) // width)


def _split_code_line(line, limit):
    """
    在「语法安全」的位置把一行代码拆成多行：
      · 字符串字面量内部不拆；
      · 优先在空白处断行；否则在逗号、左括号后断行；
      · 用反斜杠续行，保证拆分后仍是合法 Python。
    返回拆分后的若干行（不含原文本身）。
    """
    segs = []
    rest = line
    while True:
        w = 0
        in_str = None
        esc = False
        last_space = -1
        last_sep = -1
        cut = None
        for i, ch in enumerate(rest):
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif in_str:
                if ch == in_str:
                    in_str = None
            elif ch in "\"'":
                in_str = ch
            else:
                if ch == " ":
                    last_space = i
                elif ch in ",(":
                    last_sep = i
            w += 2 if ord(ch) > 0x2E7F else 1
            if w > limit:
                cut = i
                break
        if cut is None:
            segs.append(rest)
            return segs

        # 断点优先级：安全的空白 > 逗号/左括号之后 > 硬切
        if 0 < last_space:
            pos = last_space
            strip = True
        elif 0 < last_sep:
            pos = last_sep + 1
            strip = False
        else:
            pos = cut
            strip = False
        head = rest[:pos].rstrip() if strip else rest[:pos]
        tail = rest[pos:].lstrip() if strip else rest[pos:].lstrip()
        segs.append(head + " \\")
        rest = " " * 8 + tail


def reflow(lines, limit=MAX_CODE_CHARS):
    """把超宽代码行重排为续行形式，使加上行号后仍能在版面内完整显示。"""
    out = []
    changed = 0
    for line in lines:
        if current_lines(line, limit) == 1:
            out.append(line)
            continue
        changed += 1
        out.extend(_split_code_line(line, limit))
    return out, changed


def paginate(all_lines, lines_per_page=LINES_PER_PAGE):
    """
    按「真实代码行数」严格分页：每页恰好 lines_per_page 行。
    这里不按显示宽度分组，因为实测 8pt 字号下即使 100 个字符的代码行也能
    在版面内完整显示（见 tools/calibrate_wrap.py），不会折行，
    因此「真实行数」就是每页实际呈现的行数。
    """
    if lines_per_page <= 0:
        return [list(all_lines)]
    return [all_lines[i:i + lines_per_page]
            for i in range(0, len(all_lines), lines_per_page)]


def build_docx(all_lines):
    from docx import Document
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()

    # ---- 页面设置：A4 纵向，左右各 2.0cm ----
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(1.6)
    sec.right_margin = Cm(1.6)
    sec.top_margin = Cm(1.8)
    sec.bottom_margin = Cm(1.6)
    sec.header_distance = Cm(0.9)
    sec.footer_distance = Cm(0.8)

    # ---- 默认样式：等宽字体、小字号 ----
    style = doc.styles["Normal"]
    style.font.name = CODE_FONT
    style.font.size = Pt(CODE_SIZE_PT)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), CODE_FONT if attr != "w:eastAsia" else "宋体")
    pf = style.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(LINE_SPACING_PT)
    pf.widow_control = False

    # ---- 页眉 ----
    header = sec.header
    hp = header.paragraphs[0]
    hp.text = PAGE_HEADER
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in hp.runs:
        run.font.name = "宋体"
        run.font.size = Pt(9)
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    # ---- 页脚：第 X 页 ----
    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_field(paragraph, instr):
        r1 = paragraph.add_run()
        fc1 = OxmlElement("w:fldChar")
        fc1.set(qn("w:fldCharType"), "begin")
        r1._r.append(fc1)

        r2 = paragraph.add_run()
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = instr
        r2._r.append(it)

        r3 = paragraph.add_run()
        fc2 = OxmlElement("w:fldChar")
        fc2.set(qn("w:fldCharType"), "separate")
        r3._r.append(fc2)

        r4 = paragraph.add_run("1")

        r5 = paragraph.add_run()
        fc3 = OxmlElement("w:fldChar")
        fc3.set(qn("w:fldCharType"), "end")
        r5._r.append(fc3)
        return [r1, r2, r3, r4, r5]

    run_page = fp.add_run("第 ")
    runs = [run_page] + add_field(fp, " PAGE ") + [fp.add_run(" 页")]
    for r in runs:
        r.font.name = "宋体"
        r.font.size = Pt(9)
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    # ---- 正文：每页固定 50 行，行号自 1 重新编号 ----
    # 每页末尾插入分页符，因此页数、页内行号都从 1 重新开始计算。
    # 重排后每行都能在版面内完整显示，「显示行数 == 真实代码行数」，
    # 每页排入 50 行即满足「程序每页不少于 50 行」。
    total_display = sum(current_lines(l) for l in all_lines)
    pages = paginate(all_lines)
    total_pages = len(pages)
    log("  正文合计 %d 行（显示行 %d）→ %d 页，每页 %d 行，行号每页从 1 重新编号"
        % (len(all_lines), total_display, total_pages, LINES_PER_PAGE))

    for pi, page in enumerate(pages):
        for li, line in enumerate(page, start=1):
            p = doc.add_paragraph()
            p.paragraph_format.widow_control = False
            p.paragraph_format.keep_together = False
            p.paragraph_format.keep_with_next = False
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            # 行号列（右对齐的等宽数字）+ 两个空格 + 代码
            num = str(li).rjust(LINENO_WIDTH)
            r = p.add_run(num + "  " + (line if line else ""))
            r.font.name = CODE_FONT
            r.font.size = Pt(CODE_SIZE_PT)
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            r._element.rPr.rFonts.set(qn("w:cs"), CODE_FONT)

            # 每页最后一行之后分页（末页除外）
            if li == len(page) and pi != len(pages) - 1:
                p.runs[-1].add_break(WD_BREAK.PAGE)

    page_counts = [len(pg) for pg in pages]
    return doc, total_pages, page_counts


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    log("[1/2] 收集源程序……")
    all_lines, stats = collect_lines()
    total_code_lines = sum(s[2] for s in stats)

    log("[1.5] 重排超宽代码行（保证版面内完整显示）……")
    all_lines, reflowed = reflow(all_lines)
    log("  已重排 %d 行为续行形式" % reflowed)

    log("[2/2] 生成 DOCX……")
    doc, total_pages, page_counts = build_docx(all_lines)

    out_path = os.path.join(OUT_DIR, "源程序-%s%s.docx" % (SOFTWARE_NAME, SOFTWARE_VERSION))
    doc.save(out_path)
    log("  已保存: %s" % out_path)

    # ---- 校验 ----
    log("")
    log("=== 校验 ===")
    log("源程序有效行数（不含空行）: %d" % total_code_lines)
    log("文档总行数: %d" % len(all_lines))
    log("总页数: %d（每页 %d 行；页码与行号均自 1 重新计算）"
        % (total_pages, LINES_PER_PAGE))
    log("每页代码行数范围: %d ~ %d" % (min(page_counts), max(page_counts)))
    below = [(i + 1, c) for i, c in enumerate(page_counts) if c < REQUIRED_MIN_LINES]
    if below:
        log("末页不足 %d 行的页面: %s（源程序不足 60 页全部提交，末页行数不足属正常）"
            % (REQUIRED_MIN_LINES, below))
    else:
        log("通过：全部 %d 页均不少于 %d 行。" % (total_pages, REQUIRED_MIN_LINES))
    longest = max((len(l) for l in all_lines), default=0)
    wrapped = sum(1 for l in all_lines if current_lines(l) > 1)
    log("最长行字符数: %d（限宽 %d；仍超宽的显示行 %d 行）"
        % (longest, MAX_CHARS_PER_LINE, wrapped))
    log("版面参数: 字号 %s pt / 行高 %s pt / 页边距 1.6cm / A4 纵向"
        % (CODE_SIZE_PT, LINE_SPACING_PT))
    log("行号: 每页独立编号，从 1 到 %d，与页脚页码同步重新计算" % LINES_PER_PAGE)
    log("分页方式: 每页末尾插入分页符，固定 %d 行/页" % LINES_PER_PAGE)

    with open(os.path.join(OUT_DIR, "_源程序文档生成报告.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(REPORT))
        fh.write("\n")
        fh.write("\n各文件行数统计:\n")
        for rel, physical, kept in stats:
            fh.write("  %-32s 物理 %5d 行  收录 %5d 行\n" % (rel, physical, kept))
        fh.write("\n每页行数（行号自 1 重新编号）:\n")
        for i, c in enumerate(page_counts, 1):
            fh.write("  第 %2d 页: %d 行\n" % (i, c))


if __name__ == "__main__":
    sys.exit(main())
