import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import numpy as np
import random
import pickle

# 确保content目录存在
CONTENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'content')
if not os.path.exists(CONTENT_DIR):
    os.makedirs(CONTENT_DIR)

class ImageCryptoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片加密解密工具")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # 设置中文字体样式
        self.style = ttk.Style()
        self.style.configure('Custom.TLabel', font=('SimHei', 10))
        self.style.configure('Custom.TEntry', font=('SimHei', 10))
        self.style.configure('Custom.TRadiobutton', font=('SimHei', 10))

        # 变量初始化
        self.image_path = tk.StringVar()
        self.key_path = tk.StringVar()
        self.operation = tk.StringVar(value="encrypt")

        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 图片选择区域
        ttk.Label(main_frame, text="图片路径:", style='Custom.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.image_path, width=50, style='Custom.TEntry').grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="浏览...", command=self.browse_image).grid(row=0, column=2, padx=5, pady=5)

        # 操作选择区域
        operation_frame = ttk.LabelFrame(main_frame, text="操作选择", padding="10")
        operation_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        ttk.Radiobutton(operation_frame, text="加密", variable=self.operation, value="encrypt", style='Custom.TRadiobutton').grid(row=0, column=0, padx=20, pady=5)
        ttk.Radiobutton(operation_frame, text="解密", variable=self.operation, value="decrypt", style='Custom.TRadiobutton').grid(row=0, column=1, padx=20, pady=5)

        # 密钥路径区域(解密时显示)
        self.key_frame = ttk.Frame(main_frame)
        ttk.Label(self.key_frame, text="密钥路径:", style='Custom.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.key_frame, textvariable=self.key_path, width=50, style='Custom.TEntry').grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.key_frame, text="浏览...", command=self.browse_key).grid(row=0, column=2, padx=5, pady=5)

        # 绑定操作选择事件
        self.operation.trace_add("write", self.toggle_key_frame)
        self.toggle_key_frame()  # 初始状态

        # 执行按钮
        ttk.Button(main_frame, text="执行操作", command=self.execute_operation, width=20).grid(row=3, column=0, columnspan=3, pady=20)

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var, style='Custom.TLabel', foreground="blue").grid(row=4, column=0, columnspan=3, pady=10)

    def toggle_key_frame(self, *args):
        if self.operation.get() == "decrypt":
            self.key_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E)
        else:
            self.key_frame.grid_remove()

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("所有文件", "*.*")]
        )
        if file_path:
            self.image_path.set(file_path)

    def browse_key(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("密钥文件", "*.key"), ("所有文件", "*.*")]
        )
        if file_path:
            self.key_path.set(file_path)

    def execute_operation(self):
        if not self.image_path.get():
            messagebox.showerror("错误", "请选择图片文件")
            return

        try:
            if self.operation.get() == "encrypt":
                self.encrypt_image()
            else:
                if not self.key_path.get():
                    messagebox.showerror("错误", "请选择密钥文件")
                    return
                self.decrypt_image()
        except Exception as e:
            messagebox.showerror("操作失败", f"发生错误: {str(e)}")
            self.status_var.set(f"操作失败: {str(e)}")

    def encrypt_image(self):
        image_path = self.image_path.get()
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        output_dir = os.path.join(CONTENT_DIR, image_name)

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 加密参数
        encrypted_image_path = os.path.join(output_dir, "encrypted.png")
        key_path = os.path.join(output_dir, "secret.key")

        # 执行加密
        self.status_var.set("正在加密...")
        self.root.update()

        # 调用加密函数
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        pixel_count = width * height
        indices = list(range(pixel_count))
        random.shuffle(indices)

        # 保存密钥
        with open(key_path, 'wb') as f:
            pickle.dump(indices, f)

        # 加密像素
        pixels = np.array(img)
        flat_pixels = pixels.reshape(-1, 3)
        encrypted_flat = flat_pixels[indices]
        encrypted_pixels = encrypted_flat.reshape(height, width, 3)

        # 保存加密图片
        encrypted_img = Image.fromarray(encrypted_pixels.astype('uint8'))
        encrypted_img.save(encrypted_image_path)

        # 加密成功提示
        self.status_var.set(f"加密成功！文件保存在: {output_dir}")
        self.show_success_dialog("成功", f"加密成功！文件保存在:\n{output_dir}", output_dir)

    def decrypt_image(self):
        image_path = self.image_path.get()
        key_path = self.key_path.get()
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        output_dir = os.path.join(CONTENT_DIR, f"{image_name}_decrypted")

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_image_path = os.path.join(output_dir, "decrypted.png")

        # 执行解密
        self.status_var.set("正在解密...")
        self.root.update()

        # 调用解密函数
        encrypted_img = Image.open(image_path).convert('RGB')
        width, height = encrypted_img.size

        # 加载密钥
        with open(key_path, 'rb') as f:
            indices = pickle.load(f)

        # 创建恢复索引
        recover_indices = [0] * len(indices)
        for original_idx, new_idx in enumerate(indices):
            recover_indices[new_idx] = original_idx

        # 解密像素
        pixels = np.array(encrypted_img)
        flat_encrypted = pixels.reshape(-1, 3)
        decrypted_flat = flat_encrypted[recover_indices]
        decrypted_pixels = decrypted_flat.reshape(height, width, 3)
        
        # 创建解密图像对象（缺失的关键行）
        decrypted_img = Image.fromarray(decrypted_pixels.astype('uint8'))
        
        # 保存解密图片
        decrypted_dir = os.path.join(CONTENT_DIR, '已解密')
        if not os.path.exists(decrypted_dir):
            os.makedirs(decrypted_dir)
        
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_decrypted{ext}"
        output_image_path = os.path.join(decrypted_dir, output_filename)
        decrypted_img.save(output_image_path)

        # 解密成功提示
        self.status_var.set(f"解密成功！文件保存在: {decrypted_dir}")
        self.show_success_dialog("成功", f"解密成功！文件保存在:\n{decrypted_dir}", decrypted_dir)

    def show_success_dialog(self, title, message, directory):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x180")
        dialog.resizable(False, False)

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")  # 修正后的正确语法

        ttk.Label(dialog, text=message, wraplength=350).pack(padx=20, pady=20)

        # 创建按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        # 打开文件夹按钮
        ttk.Button(button_frame, text="打开文件夹", 
                  command=lambda: self.open_directory(directory)).pack(side=tk.LEFT, padx=10)
        
        # 关闭按钮
        ttk.Button(button_frame, text="关闭", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

        # 设置模态窗口
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def open_directory(self, path):
        if os.path.exists(path):
            os.startfile(path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCryptoGUI(root)
    root.mainloop()