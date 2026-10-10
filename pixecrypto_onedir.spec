# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包定义（onedir 版 / 目录版）。

用法（推荐直接用 build_exe.py --onedir）：
    pyinstaller --noconfirm --clean --distpath dist_onedir --workpath build_pyi_onedir pixecrypto_onedir.spec

与 onefile 版的区别，也是本文件存在的理由：
- onefile 版每次运行都要在 %TEMP% 下创建带安全描述符的临时目录并解包 64 MB，
  一旦那个目录创建失败（例如所在目录带有异常 ACL、杀软拦截、临时目录不可写），
  引导程序就只弹一句 "Could not create temporary directory!" 然后退出。
- onedir 版**不做任何解包**，直接从自己所在目录加载文件，因此不受上述问题影响，
  启动也更快。代价是必须整个文件夹一起分发。

其余打包参数（禁 UPX、无控制台窗口、显式 hiddenimports）与 onefile 版保持一致。
"""

import os

APP_VERSION = os.environ.get('PIXE_APP_VERSION', '1.0.0')
APP_NAME = '图片加密解密工具%s' % APP_VERSION

project_root = SPECPATH  # noqa: F821  (PyInstaller 注入)
src_dir = os.path.join(project_root, 'src')
entry_script = os.path.join(src_dir, 'main.py')

hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.font',
    'PIL.Image',
    'PIL.ImageFile',
    'PIL.PngImagePlugin',
    'PIL.JpegImagePlugin',
    'PIL.BmpImagePlugin',
    'PIL.GifImagePlugin',
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
    [],
    exclude_binaries=True,      # 关键：依赖不塞进 exe，交给 COLLECT 放到目录里
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(  # noqa: F821
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)
