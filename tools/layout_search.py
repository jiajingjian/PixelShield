# -*- coding: utf-8 -*-
"""
layout_search.py —— 自动标定「每页行数」参数。

思路：以候选的 lines_per_page 值反复生成《源程序》文档 → 转 PDF → 渲染为位图
→ 逐页统计真实文字行数，选出「所有页面均 >= 要求行数、且没有空白页」的最优值。

这避免了对字体度量与排版引擎行为的任何猜测：结论直接来自渲染结果。
"""

import json
import os
import re
import shutil
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(PROJECT_DIR, "tools")
WORK = os.path.join(TOOLS_DIR, "search")
NODE = r"D:\Programs\deepseeek\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
CLI = (r"D:\Programs\deepseeek\resources\app.asar.unpacked\dsh\node_modules"
       r"\@deepseek-ai\libreoffice-kit\lib\cli.js")
PY = sys.executable

sys.path.insert(0, TOOLS_DIR)
from verify_layout import count_text_rows  # noqa: E402


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def try_value(lpp, code_size, line_pt):
    # 生成一份临时脚本，替换常量后运行
    src = os.path.join(TOOLS_DIR, "make_source_doc.py")
    with open(src, encoding="utf-8") as fh:
        code = fh.read()
    code = re.sub(r"^LINES_PER_PAGE = \d+", "LINES_PER_PAGE = %d" % lpp, code, flags=re.M)
    code = re.sub(r"^CODE_SIZE_PT = [\d.]+", "CODE_SIZE_PT = %s" % code_size, code, flags=re.M)
    code = re.sub(r"^LINE_SPACING_PT = [\d.]+", "LINE_SPACING_PT = %s" % line_pt, code, flags=re.M)
    # 生成脚本被放到 tools/search/ 下，需固定回真实项目目录
    code = code.replace(
        'PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))',
        'PROJECT_DIR = r"%s"' % PROJECT_DIR)
    code = code.replace('OUT_DIR = os.path.join(PROJECT_DIR, "软著")',
                        'OUT_DIR = r"%s"' % os.path.join(WORK, "out").replace("\\", "\\\\"))
    tmp = os.path.join(WORK, "gen_%s_%s_%s.py" % (lpp, code_size, line_pt))
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(code)

    r = run([PY, tmp])
    if r.returncode != 0:
        return None, "生成失败: %s" % (r.stderr or "")[-300:]

    docx = None
    outdir = os.path.join(WORK, "out")
    for f in os.listdir(outdir):
        if f.startswith("源程序-") and f.endswith(".docx"):
            docx = os.path.join(outdir, f)
    if not docx:
        return None, "未找到生成的 docx"

    pdf = os.path.join(WORK, "t.pdf")
    if os.path.exists(pdf):
        os.remove(pdf)
    r = run([NODE, CLI, "convert", "--input", docx, "--output", pdf])
    if not os.path.exists(pdf):
        return None, "转换 PDF 失败: %s" % (r.stdout or r.stderr)[-300:]

    pgdir = os.path.join(WORK, "pg")
    if os.path.isdir(pgdir):
        shutil.rmtree(pgdir)
    r = run([NODE, CLI, "render", "--input", pdf, "--output-dir", pgdir, "--dpi", "110"])
    try:
        info = json.loads(r.stdout)
        page_count = info.get("pageCount")
    except Exception:  # noqa: BLE001
        page_count = None

    counts = []
    for f in sorted(os.listdir(pgdir)):
        if f.lower().endswith(".png"):
            n, _ = count_text_rows(os.path.join(pgdir, f))
            counts.append(n)
    return {"lpp": lpp, "size": code_size, "line_pt": line_pt,
            "pages": page_count, "counts": counts}, None


def main():
    if os.path.isdir(WORK):
        shutil.rmtree(WORK)
    os.makedirs(os.path.join(WORK, "out"), exist_ok=True)

    # 第一步：让引擎自然分页，量出「单页最多能容纳多少行」
    print("=== 第一步：测量单页容量（自然分页，lines_per_page 取大值） ===")
    caps = {}
    for size, pt in (("9", 13.0), ("8.5", 12.5), ("8", 11.5), ("8", 11.0)):
        res, err = try_value(300, size, pt)
        if err:
            print("  字号 %s/%spt: %s" % (size, pt, err[:120]))
            continue
        c = res["counts"]
        caps[(size, pt)] = max(c)
        print("  字号 %s / 行高 %spt → 页数 %2d，每页行数 min=%d max=%d 中位=%d"
              % (size, pt, res["pages"], min(c), max(c), sorted(c)[len(c) // 2]))

    print()
    print("=== 第二步：按目标行数强制分页，检查是否出现空白页/不足页 ===")
    best = None
    for (size, pt), cap in caps.items():
        for lpp in sorted({50, 52, 54, cap - 4, cap - 2}):
            if lpp < 50 or lpp > cap:
                continue
            res, err = try_value(lpp, size, pt)
            if err:
                print("  %s/%spt lpp=%d %s" % (size, pt, lpp, err[:100]))
                continue
            c = res["counts"]
            zeros = sum(1 for x in c if x == 0)
            below = sum(1 for x in c if x < 50)
            print("  字号 %-4s 行高 %-5s lpp=%2d → 页数=%2s 行数 min=%d max=%d 空白页=%d 不足50行页=%d"
                  % (size, pt, lpp, res["pages"], min(c), max(c), zeros, below))
            if zeros == 0 and below == 0:
                score = min(c)
                if best is None or score > best["min_lines"]:
                    best = {"size": size, "line_pt": pt, "lpp": lpp,
                            "min_lines": score, "pages": res["pages"], "counts": c}

    print()
    if best:
        print(">>> 推荐配置：字号 %s pt / 行高 %s pt / 每页 %d 行"
              % (best["size"], best["line_pt"], best["lpp"]))
        print("    共 %d 页，每页行数最少 %d，最多 %d"
              % (best["pages"], min(best["counts"]), max(best["counts"])))
        print("    分布: %s" % best["counts"])
    else:
        print(">>> 未找到同时满足「无空白页」与「每页>=50行」的配置")

    with open(os.path.join(WORK, "result.json"), "w", encoding="utf-8") as fh:
        json.dump({"best": best, "caps": {str(k): v for k, v in caps.items()}},
                  fh, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
