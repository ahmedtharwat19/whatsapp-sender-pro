"""
ملف الأنماط والتنسيقات لواجهة المستخدم
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

class Styles:
    """فئة الأنماط للتطبيق"""
    
    @staticmethod
    def configure_styles():
        """تكوين الأنماط"""
        # أنماط ttk الأساسية
        style = ttk.Style()
        
        # تخصيص الأزرار
        style.configure('Accent.TButton',
                       background='#4CAF50',
                       foreground='white',
                       padding=10,
                       font=('Arial', 11, 'bold'))
        
        style.map('Accent.TButton',
                 background=[('active', '#45a049')])
        
        # تخصيص التسميات
        style.configure('Title.TLabel',
                       font=('Arial', 16, 'bold'),
                       foreground='#333333')
        
        style.configure('Subtitle.TLabel',
                       font=('Arial', 12),
                       foreground='#666666')
        
        # تخصيص الإطارات
        style.configure('Card.TFrame',
                       background='white',
                       relief='raised',
                       borderwidth=1)
        
        # تخصيص مربعات النص
        style.configure('Success.TLabel',
                       foreground='#4CAF50',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Error.TLabel',
                       foreground='#f44336',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Warning.TLabel',
                       foreground='#ff9800',
                       font=('Arial', 10, 'bold'))
        
        # أنماط customtkinter
        ctk.set_appearance_mode("light")  # أو "dark"
        ctk.set_default_color_theme("green")  # أو "blue", "dark-blue"
    
    @staticmethod
    def get_color_theme(mode="light"):
        """الحصول على سمة الألوان"""
        if mode == "light":
            return {
                'bg': '#f0f0f0',
                'fg': '#333333',
                'accent': '#4CAF50',
                'secondary': '#2196F3',
                'warning': '#ff9800',
                'danger': '#f44336',
                'success': '#4CAF50',
                'card_bg': '#ffffff',
                'border': '#dddddd'
            }
        else:  # dark mode
            return {
                'bg': '#121212',
                'fg': '#ffffff',
                'accent': '#4CAF50',
                'secondary': '#2196F3',
                'warning': '#ff9800',
                'danger': '#f44336',
                'success': '#4CAF50',
                'card_bg': '#1e1e1e',
                'border': '#333333'
            }
    
    @staticmethod
    def create_styled_button(parent, text, command=None, style="primary", width=None):
        """إنشاء زر مخصص"""
        colors = Styles.get_color_theme()
        
        if style == "primary":
            bg = colors['accent']
            fg = 'white'
        elif style == "secondary":
            bg = colors['secondary']
            fg = 'white'
        elif style == "danger":
            bg = colors['danger']
            fg = 'white'
        else:
            bg = '#e0e0e0'
            fg = colors['fg']
        
        btn = tk.Button(parent,
                       text=text,
                       bg=bg,
                       fg=fg,
                       font=('Arial', 10, 'bold'),
                       padx=15,
                       pady=8,
                       command=command,
                       relief='flat',
                       cursor='hand2')
        
        if width:
            btn.config(width=width)
        
        # تأثير التحويم
        def on_enter(e):
            if style == "primary":
                btn.config(bg='#45a049')
            elif style == "secondary":
                btn.config(bg='#1976D2')
            elif style == "danger":
                btn.config(bg='#d32f2f')
            else:
                btn.config(bg='#d0d0d0')
        
        def on_leave(e):
            if style == "primary":
                btn.config(bg=colors['accent'])
            elif style == "secondary":
                btn.config(bg=colors['secondary'])
            elif style == "danger":
                btn.config(bg=colors['danger'])
            else:
                btn.config(bg='#e0e0e0')
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    @staticmethod
    def create_styled_frame(parent, title=None, padding=10, style="card"):
        """إنشاء إطار مخصص"""
        colors = Styles.get_color_theme()
        
        if style == "card":
            frame = tk.Frame(parent,
                            bg=colors['card_bg'],
                            relief='solid',
                            borderwidth=1)
        else:
            frame = tk.Frame(parent, bg=colors['bg'])
        
        if title:
            title_label = tk.Label(frame,
                                  text=title,
                                  bg=colors['card_bg'] if style == "card" else colors['bg'],
                                  fg=colors['fg'],
                                  font=('Arial', 12, 'bold'))
            title_label.pack(pady=(0, padding))
        
        return frame
    
    @staticmethod
    def create_styled_entry(parent, placeholder="", width=30):
        """إنشاء حقل إدخال مخصص"""
        colors = Styles.get_color_theme()
        
        frame = tk.Frame(parent, bg=colors['bg'])
        
        entry = tk.Entry(frame,
                        width=width,
                        font=('Arial', 11),
                        relief='solid',
                        borderwidth=1,
                        bg='white',
                        fg=colors['fg'])
        
        if placeholder:
            entry.insert(0, placeholder)
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg=colors['fg'])
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(fg='#999999')
            
            entry.config(fg='#999999')
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        
        entry.pack(pady=5)
        return frame, entry
    
    @staticmethod
    def create_progress_bar(parent, length=300, mode='determinate'):
        """إنشاء شريط تقدم مخصص"""
        colors = Styles.get_color_theme()
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Custom.Horizontal.TProgressbar",
                       background=colors['accent'],
                       troughcolor=colors['border'],
                       bordercolor=colors['border'],
                       lightcolor=colors['accent'],
                       darkcolor=colors['accent'])
        
        progress = ttk.Progressbar(parent,
                                  style="Custom.Horizontal.TProgressbar",
                                  length=length,
                                  mode=mode)
        
        return progress
    
    @staticmethod
    def create_styled_treeview(parent, columns):
        """إنشاء Treeview مخصص"""
        colors = Styles.get_color_theme()
        
        style = ttk.Style()
        style.configure("Treeview",
                       background=colors['card_bg'],
                       foreground=colors['fg'],
                       fieldbackground=colors['card_bg'],
                       borderwidth=0)
        
        style.configure("Treeview.Heading",
                       background=colors['accent'],
                       foreground='white',
                       relief='flat',
                       font=('Arial', 10, 'bold'))
        
        style.map("Treeview.Heading",
                 background=[('active', '#45a049')])
        
        tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # تخصيص علامات التبويب
        tree.tag_configure('oddrow', background=colors['bg'])
        tree.tag_configure('evenrow', background=colors['card_bg'])
        
        return tree
    
    @staticmethod
    def apply_rtl_styling(widget):
        """تطبيق أنماط من اليمين لليسار"""
        widget.option_add('*justify', 'right')
        widget.option_add('*Text.direction', 'rtl')
        
        # تحديث الخط ليدعم العربية
        font = ('Tahoma', 11)  # خط يدعم العربية
        widget.option_add('*Font', font)
        
        # توجيه القوائم
        widget.option_add('*Menu.direction', 'right')
        
    @staticmethod
    def apply_ltr_styling(widget):
        """تطبيق أنماط من اليسار لليمين"""
        widget.option_add('*justify', 'left')
        widget.option_add('*Text.direction', 'ltr')
        
        # الخط للغات اللاتينية
        font = ('Arial', 11)
        widget.option_add('*Font', font)