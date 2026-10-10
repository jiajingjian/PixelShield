# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包定义（可复现）。

用法（推荐直接用 build_exe.py）：
    pyinstaller --noconfirm --clean --distpath dist --workpath build_pyi pixecrypto.spec

说明：
- 入口 src/main.py，单文件（onefile）+ 无控制台窗口，和 dist 里原有的 exe 形态一致。
- 不做 UPX 压缩（upx=False）。UPX 压缩是 exe 启动即失败、以及被杀毒软件误报的常见原因。
- cv2 / numpy / PIL 由 PyInstaller 官方 hook 处理（hook-cv2、hook-numpy、hook-PIL、
  hook-_tkinter 均已安装），这里再显式声明 tkinter 子模块，避免“缺少模块”类报错。
- 版本号自动跟随 main.py 里的 version 变量（由 build_exe.py 通过环境变量传入）。
"""

import os

APP_VERSION = os.environ.get('PIXE_APP_VERSION', '1.0.0')
APP_NAME = '图片加密解密工具%s' % APP_VERSION

project_root = SPECPATH  # noqa: F821  (PyInstaller 注入)
src_dir = os.path.join(project_root, 'src')
entry_script = os.path.join(src_dir, 'main.py')

hidden_imports = [
    # 显式声明，避免裁剪掉 tkinter 的子模块
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.font',
    # PIL 用到但可能被静态分析漏掉的插件
    'PIL.Image',
    'PIL.ImageFile',
    'PIL.PngImagePlugin',
    'PIL.JpegImagePlugin',
    'PIL.BmpImagePlugin',
    'PIL.GifImagePlugin',
    # 项目自身模块
    'gui',
    'theme',
    'utils',
    'encryption',
    'decryption',
    'opencv_accelerator',
    'simple_video_encryption',
    'simple_video_decryption',
    'video_utils',
]

a = Analysis(  # noqa: F821
    [entry_script],
    pathex=[src_dir, project_root],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # 关键：禁用 UPX，避免启动失败与杀毒误报
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # 无控制台窗口（GUI 程序）
    disable_windowed_traceback=False,  # 出错时仍弹出可读的报错窗口
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
