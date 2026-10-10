# -*- mode: python ; coding: utf-8 -*-
"""一键打包脚本：把当前源码打包成 dist 下的单文件 exe，并可做启动冒烟测试。

用法：
    python build_exe.py              # 打包
    python build_exe.py --smoke      # 打包后顺便启动一次，确认主窗口能出现
    python build_exe.py --dry-run    # 只做环境自检，不真的打包

设计要点：
- 版本号自动读 src/main.py 里的 version，产物名 = 图片加密解密工具<版本>.exe
- 打包参数全部写在 pixecrypto.spec 里（禁 UPX、无控制台、显式 hiddenimports），
  所以任何人任何机器跑本脚本，结果都一致。
- 会先把 dist 里同名的旧 exe 挪到 dist/_previous/<时间戳>/ 备份，不会直接覆盖丢失。
- 工作目录用 build_pyi/（打包中间产物，可随时删）；软著文档生成脚本在 tools/，两者互不干扰。
"""

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(PROJECT_ROOT, 'pixecrypto.spec')
SPEC_FILE_ONEDIR = os.path.join(PROJECT_ROOT, 'pixecrypto_onedir.spec')
ENTRY_FILE = os.path.join(PROJECT_ROOT, 'src', 'main.py')
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')
DIST_DIR_ONEDIR = os.path.join(PROJECT_ROOT, 'dist_onedir')
WORK_DIR = os.path.join(PROJECT_ROOT, 'build_pyi')
WORK_DIR_ONEDIR = os.path.join(PROJECT_ROOT, 'build_pyi_onedir')
BACKUP_DIR = os.path.join(DIST_DIR, '_previous')

REQUIRED_MODULES = [
    ('PyInstaller', 'pyinstaller'),
    ('numpy', 'numpy'),
    ('cv2', 'opencv_python'),
    ('PIL', 'Pillow'),
    ('tkinter', '（Python 自带，需在安装 Python 时勾选 tcl/tk）'),
]

# 源码都放在 src/ 下
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')

REQUIRED_SOURCES = [
    'main.py', 'gui.py', 'theme.py', 'utils.py', 'encryption.py', 'decryption.py',
    'opencv_accelerator.py',
]


def read_version():
    """从 main.py 读 version = "x.y.z" """
    try:
        with open(ENTRY_FILE, encoding='utf-8') as f:
            m = re.search(r'^\s*version\s*=\s*["\']([^"\']+)["\']', f.read(), re.M)
        if m:
            return m.group(1)
    except OSError as e:
        print('  ! 读取 main.py 失败：%s' % e)
    return '1.0.0'


def check_environment(onedir=False):
    """打包前自检，把能提前发现的问题全部报出来。"""
    print('=' * 64)
    print('环境自检')
    print('=' * 64)
    print('  Python      : %s (%s)' % (sys.version.split()[0], sys.executable))
    print('  项目目录    : %s' % PROJECT_ROOT)
    print('  平台        : %s' % sys.platform)
    mode = ('目录版 onedir（不解包到临时目录，启动更快、更抗环境问题）' if onedir
            else '单文件版 onefile（每次运行都要解包到临时目录）')
    print('  打包形态    : %s' % mode)

    ok = True

    if os.name != 'nt':
        print('  ! 本脚本面向 Windows 打包（tkinter + exe）')
        ok = False

    missing_sources = [s for s in REQUIRED_SOURCES if not os.path.exists(os.path.join(SRC_DIR, s))]
    if missing_sources:
        print('  ! 缺少源码文件：%s' % ', '.join(missing_sources))
        ok = False
    else:
        print('  源码文件    : %d 个齐全' % len(REQUIRED_SOURCES))

    spec = SPEC_FILE_ONEDIR if onedir else SPEC_FILE
    if not os.path.exists(spec):
        print('  ! 找不到 %s' % spec)
        ok = False

    print('  依赖模块：')
    for mod, pkg in REQUIRED_MODULES:
        try:
            __import__(mod)
            print('    [OK]   %-12s (%s)' % (mod, pkg))
        except Exception as e:  # noqa: BLE001
            print('    [缺少] %-12s (%s) -> %s' % (mod, pkg, e))
            ok = False

    try:
        import PyInstaller  # noqa: F401
        from PyInstaller import __version__ as pi_version
        print('  PyInstaller : %s' % pi_version)
    except Exception:  # noqa: BLE001
        pass

    return ok


def backup_existing(target_path, dist_dir):
    """把 dist 里同名的旧产物（onefile 是文件，onedir 是目录）挪进 _previous/<时间戳>/。"""
    if not os.path.exists(target_path):
        return None
    stamp = time.strftime('%Y%m%d_%H%M%S')
    dest_dir = os.path.join(dist_dir, '_previous', stamp)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(target_path))
    shutil.move(target_path, dest)
    print('  已备份旧产物 -> %s' % dest)
    return dest


def run_pyinstaller(app_name, onedir=False):
    dist = DIST_DIR_ONEDIR if onedir else DIST_DIR
    work = WORK_DIR_ONEDIR if onedir else WORK_DIR
    spec = SPEC_FILE_ONEDIR if onedir else SPEC_FILE
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        '--log-level', 'INFO',
        '--distpath', dist,
        '--workpath', work,
        spec,
    ]
    env = dict(os.environ)
    env['PIXE_APP_VERSION'] = app_name
    print('=' * 64)
    print('开始打包（%s）：%s' % ('目录版 onedir' if onedir else '单文件版 onefile', ' '.join(cmd)))
    print('=' * 64)
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
    return proc.returncode


def smoke_test(exe_path):
    """启动一次 exe，确认主窗口能出现。

    注意：某些受限环境（沙箱 / 被 Job Object 限制的 shell）会阻止 PyInstaller
    onefile 的父进程重启子进程，导致启动失败；这种情况请在资源管理器里双击验证。
    """
    print('=' * 64)
    print('启动冒烟测试')
    print('=' * 64)

    def find_window():
        try:
            import win32gui
            found = []

            def cb(h, _):
                if win32gui.IsWindowVisible(h):
                    t = win32gui.GetWindowText(h)
                    if t and '加密' in t:
                        found.append(t)
                return True

            win32gui.EnumWindows(cb, None)
            return found
        except Exception:  # noqa: BLE001
            return []

    launched = False
    # 优先用 WMI 启动：它不受当前 shell 的 Job Object 限制，最接近双击的效果
    try:
        subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "Invoke-CimMethod -ClassName Win32_Process -MethodName Create "
             "-Arguments @{CommandLine='\"%s\"'} | Out-Null" % exe_path],
            capture_output=True, timeout=60)
        launched = True
    except Exception as e:  # noqa: BLE001
        print('  WMI 启动失败（%s），改用直接启动' % e)

    if not launched:
        try:
            subprocess.Popen([exe_path])
            launched = True
        except Exception as e:  # noqa: BLE001
            print('  [失败] 无法启动 exe：%s' % e)
            return False

    for i in range(60):
        time.sleep(1)
        titles = find_window()
        if titles:
            print('  [通过] 第 %d 秒出现主窗口：%s' % (i + 1, titles))
            # 关掉它
            try:
                subprocess.run(['taskkill', '/F', '/IM', os.path.basename(exe_path)],
                               capture_output=True)
            except Exception:  # noqa: BLE001
                pass
            return True

    print('  [未通过] 60 秒内没看到主窗口。若你是双击运行的，请看 exe 弹出的报错窗口内容。')
    return False


def main():
    parser = argparse.ArgumentParser(description='打包图片/视频加密解密工具')
    parser.add_argument('--smoke', action='store_true', help='打包后启动一次做冒烟测试')
    parser.add_argument('--dry-run', action='store_true', help='只做环境自检')
    parser.add_argument('--no-backup', action='store_true', help='不备份 dist 里的同名旧产物')
    parser.add_argument('--onedir', action='store_true',
                        help='打目录版（不解包到 %TEMP%，启动更快、更抗环境问题；需整个文件夹一起分发）')
    args = parser.parse_args()

    version = read_version()
    app_name = '图片加密解密工具%s' % version
    exe_name = app_name + '.exe'
    dist = DIST_DIR_ONEDIR if args.onedir else DIST_DIR
    # onefile：dist\<名称>.exe ；onedir：dist_onedir\<名称>\<名称>.exe
    target = os.path.join(dist, app_name if args.onedir else exe_name)
    exe_path = os.path.join(target, exe_name) if args.onedir else target

    print('打包形态：%s' % ('目录版 onedir' if args.onedir else '单文件版 onefile'))
    print('目标产物：%s' % exe_path)
    print()

    if not check_environment(onedir=args.onedir):
        print()
        print('自检未通过，已停止。请先解决上面标 [缺少] / ! 的问题。')
        return 1

    if args.dry_run:
        print()
        print('自检通过（--dry-run，未执行打包）。')
        return 0

    os.makedirs(dist, exist_ok=True)
    if not args.no_backup:
        backup_existing(target, dist)

    rc = run_pyinstaller(version, onedir=args.onedir)
    if rc != 0:
        print()
        print('打包失败，PyInstaller 退出码 %s' % rc)
        return rc

    if not os.path.exists(exe_path):
        print()
        print('打包命令成功，但没有生成 %s，请检查上面日志。' % exe_path)
        return 1

    if args.onedir:
        total = sum(f.stat().st_size for f in pathlib.Path(target).rglob('*') if f.is_file())
        size_mb = total / (1024 * 1024)
    else:
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)

    print()
    print('=' * 64)
    print('打包完成：%s (%.1f MB)' % (exe_path, size_mb))
    if args.onedir:
        print('注意：目录版必须整个文件夹一起复制/分发，不能只发 exe。')
    print('=' * 64)

    if args.smoke:
        ok = smoke_test(exe_path)
        return 0 if ok else 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
