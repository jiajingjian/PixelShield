# -*- coding: utf-8 -*-
"""
export_bundle.py —— 从已生成的《源程序》DOCX 中导出纯文本版源程序清单。

用途：部分登记渠道或内部归档更希望拿到「纯文本的源程序」，
      本脚本保证导出的文本与 DOCX 内容逐行一致，避免两处不一致。
"""

import os
import sys

from docx import Document

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_DIR, "软著")
DOCX = os.path.join(OUT_DIR, "源程序-图片加密解密工具V1.0.0.docx")
TXT = os.path.join(OUT_DIR, "源程序-图片加密解密工具V1.0.0.txt")


def main():
    if not os.path.exists(DOCX):
        print("找不到: %s" % DOCX)
        return 1

    doc = Document(DOCX)
    lines = []
    for p in doc.paragraphs:
        t = p.text.rstrip()
        lines.append(t)
    # 去掉首尾多余空行
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    with open(TXT, "w", encoding="utf-8", newline="\r\n") as fh:
        fh.write("\n".join(lines))
        fh.write("\n")

    print("已导出: %s" % TXT)
    print("行数: %d" % len(lines))
    print("字符数: %d" % sum(len(l) for l in lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
