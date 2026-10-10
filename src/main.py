# 1.0.0：图片像素置乱加密/解密，含进度显示与硬件加速可用性检测
version = "1.0.0"

import tkinter as tk

from gui import ImageCryptoGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCryptoGUI(root)
    root.mainloop()
