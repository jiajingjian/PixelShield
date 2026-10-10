version = "1.0.0"
# 版本号
# #1.0.0升级了视频加密和进度条功能
import tkinter as tk
from gui import MediaCryptoGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaCryptoGUI(root)
    root.mainloop()
