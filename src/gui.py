import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from utils import get_decrypted_directory, get_content_directory, get_encrypted_directory, set_content_directory
from encryption import encrypt_image
from decryption import decrypt_image
from simple_video_encryption import encrypt_video_simple
from simple_video_decryption import decrypt_video_simple
from theme import AppTheme
from opencv_accelerator import check_opencv_accel_available, get_opencv_accel_info
import threading
import queue


class MediaCryptoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("媒体加密解密工具")
        self.root.geometry("600x600")
        self.root.resizable(False, False)
        
        AppTheme.apply_theme(root)

        self.media_path = tk.StringVar()
        self.key_path = tk.StringVar()
        self.media_type = tk.StringVar(value="image")
        self.operation = tk.StringVar(value="encrypt")
        self.progress_var = tk.DoubleVar()
        
        self.hardware_accel_available = check_opencv_accel_available()
        self.hardware_accel_info = get_opencv_accel_info() if self.hardware_accel_available else None

        self.queue = queue.Queue()
        self.is_processing = False
        self.cancel_flag = False

        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, style='App.TFrame', padding=AppTheme.SPACING['xl'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="媒体加密解密工具", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, AppTheme.SPACING['xl']))

        dir_frame = ttk.LabelFrame(main_frame, text="存储位置", style='Card.TLabelframe', padding=AppTheme.SPACING['lg'])
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, AppTheme.SPACING['lg']))
        
        ttk.Label(dir_frame, text="存储目录:", style='Card.TLabel').grid(row=0, column=0, sticky=tk.W, pady=AppTheme.SPACING['sm'])
        self.dir_path_var = tk.StringVar(value=get_content_directory())
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_path_var, width=40, style='Normal.TEntry')
        self.dir_entry.grid(row=0, column=1, padx=AppTheme.SPACING['md'], pady=AppTheme.SPACING['sm'])
        dir_button = ttk.Button(dir_frame, text="选择...", style='Small.TButton', command=self.browse_directory)
        dir_button.grid(row=0, column=2, padx=AppTheme.SPACING['md'], pady=AppTheme.SPACING['sm'])

        self.type_frame = ttk.LabelFrame(main_frame, text="类型选择", style='Card.TLabelframe', padding=AppTheme.SPACING['lg'])
        type_frame = self.type_frame
        type_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, AppTheme.SPACING['lg']))

        ttk.Radiobutton(type_frame, text="图片", variable=self.media_type, value="image", style='Card.TRadiobutton').grid(row=0, column=0, padx=AppTheme.SPACING['xl'], pady=AppTheme.SPACING['sm'])
        ttk.Radiobutton(type_frame, text="视频", variable=self.media_type, value="video", style='Card.TRadiobutton').grid(row=0, column=1, padx=AppTheme.SPACING['xl'], pady=AppTheme.SPACING['sm'])

        ttk.Label(main_frame, text="文件路径:", style='Normal.TLabel').grid(row=3, column=0, sticky=tk.W, pady=AppTheme.SPACING['sm'])
        self.media_path_entry = ttk.Entry(main_frame, textvariable=self.media_path, width=48, style='Normal.TEntry')
        self.media_path_entry.grid(row=3, column=1, padx=AppTheme.SPACING['md'], pady=AppTheme.SPACING['sm'])
        ttk.Button(main_frame, text="浏览...", style='Small.TButton', command=self.browse_media).grid(row=3, column=2, padx=AppTheme.SPACING['md'], pady=AppTheme.SPACING['sm'])

        self.operation_frame = ttk.LabelFrame(main_frame, text="操作选择", style='Card.TLabelframe', padding=AppTheme.SPACING['lg'])
        operation_frame = self.operation_frame
        operation_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, AppTheme.SPACING['lg']))

        ttk.Radiobutton(operation_frame, text="加密", variable=self.operation, value="encrypt", style='Card.TRadiobutton').grid(row=0, column=0, padx=AppTheme.SPACING['xl'], pady=AppTheme.SPACING['sm'])
        ttk.Radiobutton(operation_frame, text="解密", variable=self.operation, value="decrypt", style='Card.TRadiobutton').grid(row=0, column=1, padx=AppTheme.SPACING['xl'], pady=AppTheme.SPACING['sm'])

        self.key_frame = ttk.Frame(main_frame, style='App.TFrame')
        ttk.Label(self.key_frame, text="密钥路径:", style='Normal.TLabel').grid(row=0, column=0, sticky=tk.W, pady=AppTheme.SPACING['sm'])
        ttk.Entry(self.key_frame, textvariable=self.key_path, width=48, style='Normal.TEntry').grid(row=0, column=1, padx=AppTheme.SPACING['md'], pady=AppTheme.SPACING['sm'])
        ttk.Button(self.key_frame, text="浏览...", style='Small.TButton', command=self.browse_key).grid(row=0, column=2, padx=AppTheme.SPACING['md'], pady=AppTheme.SPACING['sm'])

        self.operation.trace_add("write", self.toggle_key_frame)
        self.toggle_key_frame()

        self.progress_frame = ttk.Frame(main_frame, style='App.TFrame')
        self.progress_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(AppTheme.SPACING['lg'], 0))
        
        ttk.Label(self.progress_frame, text="进度:", style='Normal.TLabel').pack(side=tk.LEFT, padx=(0, AppTheme.SPACING['md']), pady=AppTheme.SPACING['sm'])
        progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, length=0, mode='determinate', style='Normal.Horizontal.TProgressbar')
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=AppTheme.SPACING['sm'])

        button_frame = ttk.Frame(main_frame, style='App.TFrame')
        button_frame.grid(row=7, column=0, columnspan=3, pady=AppTheme.SPACING['xl'])
        
        self.execute_btn = ttk.Button(button_frame, text="执行操作", style='Primary.TButton', command=self.execute_operation, width=15)
        self.execute_btn.pack(side=tk.LEFT, padx=AppTheme.SPACING['md'])
        
        self.cancel_btn = ttk.Button(button_frame, text="取消", style='Secondary.TButton', command=self.cancel_operation, width=15, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=AppTheme.SPACING['md'])

        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main_frame, textvariable=self.status_var, style='Success.TLabel').grid(row=8, column=0, columnspan=3, pady=(AppTheme.SPACING['md'], 0))

    def toggle_key_frame(self, *args):
        if self.operation.get() == "decrypt":
            self.key_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W+tk.E, pady=(0, AppTheme.SPACING['lg']))
        else:
            self.key_frame.grid_remove()

    def browse_directory(self):
        directory = filedialog.askdirectory(title="选择存储目录")
        if directory:
            self.dir_path_var.set(directory)
            set_content_directory(directory)

    def browse_media(self):
        if self.media_type.get() == "image":
            file_path = filedialog.askopenfilename(
                filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("所有文件", "*.*")]
            )
        else:
            file_path = filedialog.askopenfilename(
                filetypes=[("视频文件", "*.mp4;*.avi;*.mov;*.wmv;*.mkv"), ("所有文件", "*.*")]
            )
        if file_path:
            self.media_path.set(file_path)

    def browse_key(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("密钥文件", "*.key"), ("所有文件", "*.*")]
        )
        if file_path:
            self.key_path.set(file_path)

    def execute_operation(self):
        if not self.media_path.get():
            messagebox.showerror("错误", "请选择文件")
            return

        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请稍候...")
            return

        selected_dir = self.dir_path_var.get()
        if selected_dir != get_content_directory():
            set_content_directory(selected_dir)

        self.progress_var.set(0)
        self.is_processing = True
        self.cancel_flag = False
        
        self.execute_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)

        thread = threading.Thread(target=self._execute_operation_thread, daemon=True)
        thread.start()

    def cancel_operation(self):
        if self.is_processing:
            self.cancel_flag = True
            self.queue.put(('status', "正在取消..."))
            self.cancel_btn.config(state=tk.DISABLED)

    def _execute_operation_thread(self):
        try:
            if self.operation.get() == "encrypt":
                if self.media_type.get() == "image":
                    self._encrypt_image_thread()
                else:
                    self._encrypt_video_thread()
            else:
                if not self.key_path.get():
                    self.queue.put(('error', "请选择密钥文件"))
                    return
                if self.media_type.get() == "image":
                    self._decrypt_image_thread()
                else:
                    self._decrypt_video_thread()
        except Exception as e:
            self.queue.put(('error', str(e)))

    def check_queue(self):
        try:
            while True:
                msg_type, msg_data = self.queue.get_nowait()

                if msg_type == 'progress':
                    self.progress_var.set(msg_data)
                elif msg_type == 'status':
                    self.status_var.set(msg_data)
                elif msg_type == 'success':
                    self.is_processing = False
                    self.execute_btn.config(state=tk.NORMAL)
                    self.cancel_btn.config(state=tk.DISABLED)
                    self.progress_var.set(100)
                    self.show_success_dialog(msg_data['title'], msg_data['message'], msg_data['directory'])
                elif msg_type == 'error':
                    self.is_processing = False
                    self.execute_btn.config(state=tk.NORMAL)
                    self.cancel_btn.config(state=tk.DISABLED)
                    messagebox.showerror("操作失败", f"发生错误: {msg_data}")
                    self.status_var.set(f"操作失败: {msg_data}")
                elif msg_type == 'cancelled':
                    self.is_processing = False
                    self.execute_btn.config(state=tk.NORMAL)
                    self.cancel_btn.config(state=tk.DISABLED)
                    self.status_var.set("操作已取消")

        except queue.Empty:
            pass

        self.root.after(100, self.check_queue)

    def _encrypt_image_thread(self):
        media_path = self.media_path.get()

        self.queue.put(('status', "正在加密..."))
        self.queue.put(('progress', 0))

        def progress_callback(progress):
            if self.cancel_flag:
                raise Exception("操作已取消")
            self.queue.put(('progress', progress))

        try:
            encrypted_image_path, key_path = encrypt_image(media_path, "", progress_callback)
        except Exception as e:
            if "取消" in str(e):
                self.queue.put(('cancelled', None))
                return
            raise

        encrypted_dir = get_encrypted_directory()
        self.queue.put(('status', f"加密成功！文件保存在: {encrypted_dir}"))
        self.queue.put(('success', {
            'title': "成功",
            'message': f"加密成功！文件保存在:\n{encrypted_dir}",
            'directory': encrypted_dir
        }))

    def _decrypt_image_thread(self):
        media_path = self.media_path.get()
        key_path = self.key_path.get()

        self.queue.put(('status', "正在解密..."))
        self.queue.put(('progress', 0))

        def progress_callback(progress):
            if self.cancel_flag:
                raise Exception("操作已取消")
            self.queue.put(('progress', progress))

        try:
            output_image_path = decrypt_image(media_path, key_path, progress_callback)
        except Exception as e:
            if "取消" in str(e):
                self.queue.put(('cancelled', None))
                return
            raise

        decrypted_dir = get_decrypted_directory()
        self.queue.put(('status', f"解密成功！文件保存在: {decrypted_dir}"))
        self.queue.put(('success', {
            'title': "成功",
            'message': f"解密成功！文件保存在:\n{decrypted_dir}",
            'directory': decrypted_dir
        }))

    def _encrypt_video_thread(self):
        media_path = self.media_path.get()

        self.queue.put(('status', "正在加密视频..."))
        self.queue.put(('progress', 0))

        def status_callback(status):
            if self.cancel_flag:
                raise Exception("操作已取消")
            self.queue.put(('status', status))

        def progress_callback(progress):
            if self.cancel_flag:
                raise Exception("操作已取消")
            self.queue.put(('progress', progress))

        try:
            encrypted_video_path, key_path = encrypt_video_simple(
                media_path, "",
                status_callback=status_callback, progress_callback=progress_callback
            )
        except Exception as e:
            if "取消" in str(e):
                self.queue.put(('cancelled', None))
                return
            raise

        encrypted_dir = get_encrypted_directory()
        self.queue.put(('status', f"视频加密成功！文件保存在: {encrypted_dir}"))
        self.queue.put(('success', {
            'title': "成功",
            'message': f"视频加密成功！文件保存在:\n{encrypted_dir}",
            'directory': encrypted_dir
        }))

    def _decrypt_video_thread(self):
        media_path = self.media_path.get()
        key_path = self.key_path.get()

        self.queue.put(('status', "正在解密视频..."))
        self.queue.put(('progress', 0))

        def status_callback(status):
            if self.cancel_flag:
                raise Exception("操作已取消")
            self.queue.put(('status', status))

        def progress_callback(progress):
            if self.cancel_flag:
                raise Exception("操作已取消")
            self.queue.put(('progress', progress))

        try:
            output_video_path = decrypt_video_simple(
                media_path, key_path,
                status_callback, progress_callback
            )
        except Exception as e:
            if "取消" in str(e):
                self.queue.put(('cancelled', None))
                return
            raise

        decrypted_dir = get_decrypted_directory()
        self.queue.put(('status', f"视频解密成功！文件保存在: {decrypted_dir}"))
        self.queue.put(('success', {
            'title': "成功",
            'message': f"视频解密成功！文件保存在:\n{decrypted_dir}",
            'directory': decrypted_dir
        }))

    def show_success_dialog(self, title, message, directory):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.configure(bg=AppTheme.COLORS['background'])

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        content_frame = ttk.Frame(dialog, style='App.TFrame', padding=AppTheme.SPACING['xl'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(content_frame, text=message, style='Normal.TLabel', wraplength=340).pack(pady=(0, AppTheme.SPACING['lg']))

        button_frame = ttk.Frame(content_frame, style='App.TFrame')
        button_frame.pack()

        ttk.Button(button_frame, text="打开文件夹", style='Small.TButton',
                  command=lambda: self.open_directory(directory)).pack(side=tk.LEFT, padx=AppTheme.SPACING['md'])

        ttk.Button(button_frame, text="关闭", style='Small.TButton', command=dialog.destroy).pack(side=tk.LEFT, padx=AppTheme.SPACING['md'])

        dialog.transient(self.root)
        dialog.focus_set()
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

    def open_directory(self, path):
        if os.path.exists(path):
            os.startfile(path)
