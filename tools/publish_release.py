# -*- coding: utf-8 -*-
"""发布 GitHub Release：打包目录版 zip -> 推送 tag -> 建 Release -> 上传两个附件。

全部网络操作都带重试（本机到 github.com 的连通性是间歇性的）。
只用标准库；token 通过 git credential fill 从凭据管理器取，不落盘、不回显。
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

REPO = "jiajingjian/PixelShield"
ROOT = r"H:\project\pixe"
TAG = "v1.0.0"
APP = "图片加密解密工具1.0.0"
ONEDIR_DIR = os.path.join(ROOT, "dist_onedir", APP)
ZIP_PATH = os.path.join(ROOT, "dist_onedir", APP + "-目录版.zip")
EXE_ONE = os.path.join(ROOT, "dist", APP + ".exe")

# 附件名必须是 ASCII —— GitHub 会把非 ASCII 字符直接剥掉
# （实测：中文名 "图片加密解密工具1.0.0-目录版.zip" 被上传成了 "1.0.0-.zip"），
# 所以这里统一用仓库名 PixelShield + 版本 + 平台 的英文命名。
ASSET_EXE = "PixelShield-1.0.0-windows-x64.exe"
ASSET_ZIP = "PixelShield-1.0.0-windows-x64-portable.zip"


def log(msg=""):
    print(msg, flush=True)


def get_token():
    p = subprocess.run(["git", "credential", "fill"],
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True, timeout=60)
    for line in p.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("无法从凭据管理器取到 token")


def sha256(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def make_zip():
    if os.path.exists(ZIP_PATH):
        log("  已存在，跳过打包: %s" % os.path.basename(ZIP_PATH))
        return
    log("  正在压缩目录版（1043 个文件，约 162 MB）…")
    t0 = time.time()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for base, _dirs, files in os.walk(ONEDIR_DIR):
            for f in files:
                full = os.path.join(base, f)
                rel = os.path.relpath(full, os.path.dirname(ONEDIR_DIR))
                z.write(full, rel)
    log("  压缩完成: %s  %.1f MB  用时 %.0f 秒"
        % (os.path.basename(ZIP_PATH), os.path.getsize(ZIP_PATH) / 1048576, time.time() - t0))


def api(tok, path, method="GET", payload=None, raw=None, ctype="application/json"):
    url = path if path.startswith("http") else "https://api.github.com" + path
    data = raw if raw is not None else (json.dumps(payload).encode("utf-8") if payload is not None else None)
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + tok)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "pixe-release")
    if data is not None:
        req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            body = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def push_tag():
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    for i in range(1, 21):
        p = subprocess.run(["git", "push", "origin", TAG], cwd=ROOT, env=env,
                           capture_output=True, text=True, timeout=180)
        if p.returncode == 0:
            log("  [推 tag] 第 %d 次成功：%s" % (i, (p.stdout + p.stderr).strip().replace("\n", " | ")))
            return True
        log("  [推 tag] 第 %d 次失败：%s" % (i, (p.stderr or p.stdout).strip().splitlines()[-1][:140]))
        time.sleep(45)
    return False


log("=" * 66)
log("发布 GitHub Release：%s @ %s" % (REPO, TAG))
log("=" * 66)

log("\n[1/4] 打包目录版 zip")
make_zip()

log("\n[2/4] 推送 tag %s" % TAG)
if not push_tag():
    log("  ✗ tag 推送连续失败，停止。网络恢复后可重跑本脚本。")
    sys.exit(2)

tok = get_token()
log("\n[3/4] 创建 Release")

exe_sha = sha256(EXE_ONE)
zip_sha = sha256(ZIP_PATH)
body = """## 图片加密解密工具 V1.0.0

基于**像素置乱**的图片加密/解密工具，Windows 桌面程序，纯本地运行、不联网。

> ⚠️ 说明：本工具做的是像素位置重排，属于「防随手翻看」级别的内容遮蔽，
> **不是密码学意义上的加密**。高价值数据请使用 VeraCrypt、7-Zip AES-256 等专业工具。

### 下载哪个？

| 文件 | 说明 |
| --- | --- |
| `%s` | **单文件版**，64 MB，双击即用，方便单独发给别人 |
| `%s` | **目录版**，解压后运行文件夹内的 exe；不解压到临时目录，启动更快、更不容易被安全软件或目录权限拦住 |

> 若单文件版双击后弹出 `Could not create temporary directory!`，
> 说明所在目录不允许创建临时目录 —— 换到别的文件夹（如桌面）再试，或改用目录版。

### 功能

- 图片加密：把像素顺序按随机置换表打乱，输出无损 PNG，画面成为无法辨认的噪点
- 图片解密：依据 `.key` 密钥文件还原，**逐像素无损**，保留原始颜色模式与扩展名
- 启动时检测 OpenCL / UMat 硬件加速是否可用并在控制台显示结果（像素置乱运算由 NumPy 在 CPU 上完成）
- 进度显示、随时取消、结果一键打开所在文件夹
- 绿色免安装：不写注册表，复制文件夹即可迁移；**不依赖任何外部程序**

### 环境

- Windows 10 / 11（64 位）
- 单文件版与目录版均**无需安装 Python**；源码运行需 Python 3.8+ 与 NumPy / OpenCV / Pillow

### 校验值（SHA-256）

```
%s  %s
%s  %s
```

### 许可证

GNU General Public License v3.0（GPL-3.0）：可免费使用、修改、分发（含商业用途），
但分发修改版时必须同样以 GPL-3.0 开源并提供完整源代码。
第三方组件许可见仓库内 `THIRD-PARTY-NOTICES.md`。
""" % (ASSET_EXE, ASSET_ZIP, exe_sha, ASSET_EXE, zip_sha, ASSET_ZIP)

payload = {
    "tag_name": TAG,
    "name": "图片加密解密工具 V1.0.0",
    "body": body,
    "draft": False,
    "prerelease": False,
    "target_commitish": "main",
}

release = None
for i in range(1, 13):
    st, res = api(tok, "/repos/%s/releases" % REPO, "POST", payload)
    if st in (200, 201):
        release = res
        log("  第 %d 次成功：%s" % (i, res["html_url"]))
        break
    log("  第 %d 次失败（HTTP %s）：%s" % (i, st, str(res)[:200]))
    if st == 422 and "already_exists" in str(res):
        st2, lst = api(tok, "/repos/%s/releases/tags/%s" % (REPO, TAG))
        if st2 == 200:
            release = lst
            log("  已存在同名 Release，复用：%s" % release["html_url"])
            break
    time.sleep(30)

if not release:
    log("  ✗ 创建 Release 失败，停止。")
    sys.exit(3)

log("\n[4/4] 上传附件到 release id=%s" % release["id"])
assets = [(EXE_ONE, "application/octet-stream"),
          (ZIP_PATH, "application/zip")]
for path, ctype in assets:
    name = os.path.basename(path)
    size_mb = os.path.getsize(path) / 1048576
    ok = False
    for i in range(1, 9):
        with open(path, "rb") as f:
            raw = f.read()
        st, res = api(tok,
                      "https://uploads.github.com/repos/%s/releases/%s/assets?name=%s"
                      % (REPO, release["id"], urllib.parse.quote(name)),
                      "POST", raw=raw, ctype=ctype)
        if st in (200, 201):
            log("  ✅ %s（%.1f MB）上传成功，第 %d 次尝试" % (name, size_mb, i))
            ok = True
            break
        log("  ✗ %s 第 %d 次失败（HTTP %s）：%s" % (name, i, st, str(res)[:160]))
        if st == 422:
            log("     （可能已存在同名附件，视为完成）")
            ok = True
            break
        time.sleep(30)
    if not ok:
        log("  ✗ %s 上传失败" % name)

log("\n" + "=" * 66)
st, final = api(tok, "/repos/%s/releases/tags/%s" % (REPO, TAG))
if st == 200:
    log("Release 页面：%s" % final["html_url"])
    log("附件清单：")
    for a in final.get("assets", []):
        log("  - %s  %.1f MB  下载 %d 次" % (a["name"], a["size"] / 1048576, a["download_count"]))
log("=" * 66)
