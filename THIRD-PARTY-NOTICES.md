# 第三方组件许可声明（THIRD-PARTY NOTICES）

本软件《图片加密解密工具》（Media Crypto Tool）本身以 **GPL-3.0** 发布（见 [LICENSE](LICENSE)）。

本软件发布的可执行文件 `dist/图片加密解密工具1.0.0.exe` 是一个由 **PyInstaller** 打包的
单文件程序，其中**内嵌并一同分发**了下列第三方组件。各组件的著作权归其各自作者所有，
其许可证条款独立于本项目的 GPL-3.0，列表如下。

> 下表中的清单是根据实际打包产物（解包目录 `%TEMP%\_MEIxxxx` 的 51 个 DLL 与 12 个包目录）
> 逐个核对得到的，不是照抄依赖清单。
> 本文件是提示性说明；**权威文本以各组件官方发布为准**，链接见每一行。

## 一、运行时组件

| 组件 | 版本 | 许可证 | 许可证全文 |
| --- | --- | --- | --- |
| Python 解释器（`python313.dll`、`python3.dll`、`base_library.zip`、标准库扩展 `.pyd`） | 3.13.5 | PSF License Agreement (Python-2.0) | https://docs.python.org/3/license.html |
| Tcl/Tk（`tcl86t.dll`、`tk86t.dll`、`tcl8/`、`_tcl_data/`、`_tk_data/`） | Tcl/Tk 8.6 | Tcl/Tk License（BSD 式） | https://www.tcl.tk/software/tcltk/license.html |
| OpenSSL（`libcrypto-3.dll`、`libssl-3.dll`，随 Python 的 `ssl` 模块分发） | 3.x | Apache-2.0 | https://www.openssl.org/source/license.html |
| libffi（`libffi-8.dll`） | 3.4.x | MIT | https://github.com/libffi/libffi/blob/master/LICENSE |
| zlib（`zlib1.dll`） | 1.3.x | zlib License | https://zlib.net/zlib_license.html |
| Microsoft Visual C++ 运行库与通用 C 运行时（`VCRUNTIME140.dll`、`VCRUNTIME140_1.dll`、`ucrtbase.dll`、`api-ms-win-*.dll`） | — | Microsoft 软件许可条款（可再发行组件） | https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist |

## 二、Python 第三方库

| 组件 | 版本 | 许可证 | 许可证全文 |
| --- | --- | --- | --- |
| NumPy（`numpy/`、`numpy.libs/`） | 2.2.6 | BSD-3-Clause | https://numpy.org/doc/stable/license.html |
| OpenCV（`cv2/`） | 4.12.0 | Apache-2.0 | https://github.com/opencv/opencv/blob/4.x/LICENSE |
| opencv-python（OpenCV 的 Python 封装与打包） | 4.12.0.88 | MIT | https://github.com/opencv/opencv-python/blob/master/LICENSE.txt |
| Pillow（`PIL/`） | 12.2.0 | MIT-CMU（HPND） | https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| pywin32（`win32/`、`pywin32_system32/`、`_wmi.pyd`） | 311 | PSF License Agreement | https://github.com/mhammond/pywin32/blob/main/LICENSE.txt |
| charset-normalizer（`charset_normalizer/`） | — | MIT | https://github.com/jawah/charset_normalizer/blob/master/LICENSE |

## 三、打包工具

| 组件 | 版本 | 许可证 | 说明 |
| --- | --- | --- | --- |
| PyInstaller（其引导程序 bootloader 被编译进 exe） | 6.14.2 | GPL-2.0-or-later，**附特别例外条款** | 该例外明确允许使用 PyInstaller 打包并以**任意许可证**（含专有许可证）分发被打包的应用程序。本项目按 GPL-3.0 分发，与 GPL-2.0-or-later 兼容。许可证与例外条款：https://pyinstaller.org/en/stable/license.html |

## 四、许可证兼容性说明

- 上述第三方组件全部采用**宽松型（permissive）**许可证（PSF / BSD / MIT / Apache-2.0 / zlib），
  均可与 **GPL-3.0** 兼容并被一同分发；其中 Apache-2.0 与 GPL-3.0 兼容（与 GPL-2.0 不兼容，
  本项目选择 GPL-3.0 无此问题）。
- 本项目的源代码以 GPL-3.0 授权；第三方组件仍按各自许可证授权，本项目不对其主张任何权利。
- 再分发者需要同时遵守：本项目的 GPL-3.0（提供完整源代码）**以及**上表各组件的许可证
  （保留其版权声明与许可证文本）。

## 五、本项目的许可证摘要

《图片加密解密工具》Copyright (C) 2026 贾京健

本程序是自由软件：你可以依据自由软件基金会发布的 **GNU 通用公共许可证第 3 版**
（或你选择的任何更新版本）的条款重新分发和/或修改它。

本程序的发布是希望它有用，但**不提供任何担保**，甚至不包括对适销性或特定用途适用性的默示担保。
详见 [LICENSE](LICENSE)。

---

*若你是再分发者且需要一份把上述声明汇总在一起的文本，请直接使用本文件。*
