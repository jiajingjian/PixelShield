import tkinter as tk
from tkinter import ttk


class AppTheme:
    """应用主题配置类"""
    
    # 颜色配置
    COLORS = {
        'primary': '#2563EB',
        'primary_dark': '#1D4ED8',
        'primary_light': '#3B82F6',
        'success': '#10B981',
        'success_dark': '#059669',
        'warning': '#F59E0B',
        'danger': '#EF4444',
        'background': '#F8FAFC',
        'surface': '#FFFFFF',
        'surface_hover': '#F1F5F9',
        'text_primary': '#1E293B',
        'text_secondary': '#64748B',
        'text_disabled': '#94A3B8',
        'border': '#E2E8F0',
        'border_focus': '#94A3B8',
        'progress': '#10B981',
        'progress_bg': '#E2E8F0'
    }
    
    # 字体配置
    FONTS = {
        'title': ('Microsoft YaHei UI', 14, 'bold'),
        'heading': ('Microsoft YaHei UI', 12, 'bold'),
        'normal': ('Microsoft YaHei UI', 10),
        'small': ('Microsoft YaHei UI', 9),
        'mono': ('Consolas', 10)
    }
    
    # 间距配置
    SPACING = {
        'xs': 2,
        'sm': 4,
        'md': 8,
        'lg': 12,
        'xl': 16,
        'xxl': 20
    }
    
    # 圆角配置
    BORDER_WIDTH = {
        'thin': 1,
        'normal': 2,
        'thick': 3
    }
    
    @classmethod
    def apply_theme(cls, root):
        """应用主题到根窗口"""
        style = ttk.Style()
        
        # 尝试使用现代主题
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 配置根窗口背景
        root.configure(bg=cls.COLORS['background'])
        
        # 配置 TFrame 样式
        style.configure('App.TFrame', background=cls.COLORS['background'])
        style.configure('Card.TFrame', background=cls.COLORS['surface'], relief='flat')
        
        # 配置 TLabelFrame 样式
        style.configure('Card.TLabelframe', 
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['heading'])
        style.configure('Card.TLabelframe.Label', 
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['heading'])
        
        # 配置 TLabel 样式
        style.configure('Normal.TLabel', 
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['normal'])
        style.configure('Secondary.TLabel', 
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_secondary'],
                       font=cls.FONTS['small'])
        style.configure('Card.TLabel', 
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['normal'])
        style.configure('Title.TLabel', 
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['title'])
        style.configure('Success.TLabel', 
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['success'],
                       font=cls.FONTS['normal'])
        
        # 配置 TButton 样式
        style.configure('Primary.TButton', 
                       font=cls.FONTS['normal'],
                       padding=(cls.SPACING['lg'], cls.SPACING['md']),
                       foreground='white',
                       background=cls.COLORS['primary'])
        
        style.configure('Success.TButton', 
                       font=cls.FONTS['normal'],
                       padding=(cls.SPACING['lg'], cls.SPACING['md']),
                       foreground='white',
                       background=cls.COLORS['success'])
        
        style.configure('Secondary.TButton', 
                       font=cls.FONTS['normal'],
                       padding=(cls.SPACING['lg'], cls.SPACING['md']),
                       foreground='white',
                       background='#DC2626')
        
        style.configure('Small.TButton', 
                       font=cls.FONTS['small'],
                       padding=(cls.SPACING['md'], cls.SPACING['sm']),
                       foreground='#1E293B',
                       background='#FFFFFF')
        
        # 配置 TEntry 样式
        style.configure('Normal.TEntry', 
                       font=cls.FONTS['normal'],
                       fieldbackground=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=cls.BORDER_WIDTH['normal'])
        style.map('Normal.TEntry',
                  fieldbackground=[('readonly', cls.COLORS['surface_hover'])],
                  bordercolor=[('focus', cls.COLORS['primary']),
                               ('!focus', cls.COLORS['border'])])
        
        # 配置 TRadiobutton 样式
        style.configure('Normal.TRadiobutton', 
                       font=cls.FONTS['normal'],
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_primary'])
        style.configure('Card.TRadiobutton', 
                       font=cls.FONTS['normal'],
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'])
        style.map('Normal.TRadiobutton',
                  background=[('active', cls.COLORS['surface_hover']),
                             ('selected', cls.COLORS['primary'])],
                  foreground=[('selected', 'white')])
        
        # 配置 TCheckbutton 样式
        style.configure('Normal.TCheckbutton', 
                       font=cls.FONTS['normal'],
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text_primary'])
        style.configure('Card.TCheckbutton', 
                       font=cls.FONTS['normal'],
                       background=cls.COLORS['surface'],
                       foreground=cls.COLORS['text_primary'])
        style.map('Normal.TCheckbutton',
                  background=[('active', cls.COLORS['surface_hover']),
                             ('selected', cls.COLORS['primary'])],
                  foreground=[('selected', 'white')])
        
        # 配置 TProgressbar 样式
        style.configure('Normal.Horizontal.TProgressbar',
                       thickness=16,
                       troughcolor=cls.COLORS['progress_bg'],
                       background=cls.COLORS['progress'],
                       bordercolor=cls.COLORS['border'],
                       lightcolor=cls.COLORS['progress'],
                       darkcolor=cls.COLORS['success_dark'])
        
        # 配置 Tooltip 样式
        style.configure('Tooltip.TLabel',
                       background='#FFFBEB',
                       foreground='#78350F',
                       font=cls.FONTS['small'],
                       borderwidth=1,
                       relief='solid',
                       padding=(cls.SPACING['md'], cls.SPACING['sm']))
    
    @classmethod
    def create_tooltip(cls, widget, text):
        """创建工具提示"""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+0+0")
        tooltip.withdraw()
        
        label = ttk.Label(tooltip, text=text, style='Tooltip.TLabel')
        label.pack()
        
        def on_enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def on_leave(event):
            tooltip.withdraw()
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        
        return tooltip
