# app/ui/user_interface.py
"""
واجهة المستخدم الرئيسية - الشاشة الرئيسية للتطبيق
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
from pathlib import Path
import threading
import queue
import logging
from datetime import datetime

class WhatsAppSenderApp:
    def __init__(self, hwid, firestore_service=None):
        """تهيئة واجهة المستخدم"""
        self.logger = logging.getLogger(__name__)
        self.hwid = hwid
        self.firestore_service = firestore_service
        self.whatsapp_manager = None
        self.message_sender = None
        
        # إنشاء النافذة الرئيسية
        self.root = tk.Tk()
        self.root.title("WhatsApp Sender Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # إعداد النمط
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # قائمة اللغات
        self.languages = {
            'ar': {'name': 'العربية', 'dir': 'rtl'},
            'en': {'name': 'English', 'dir': 'ltr'},
            'fr': {'name': 'Français', 'dir': 'ltr'},
            'es': {'name': 'Español', 'dir': 'ltr'}
        }
        self.current_language = 'ar'
        
        # تهيئة الواجهة
        self.init_ui()
        
        # تحميل الترجمات
        self.load_translations()
        
    def init_ui(self):
        """تهيئة عناصر واجهة المستخدم"""
        # شريط القائمة
        self.create_menu_bar()
        
        # إطار الشريط العلوي
        self.create_top_bar()
        
        # إطار المحتوى الرئيسي
        self.create_main_content()
        
        # شريط الحالة
        self.create_status_bar()
        
    def create_menu_bar(self):
        """إنشاء شريط القائمة"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="الملف", menu=file_menu)
        file_menu.add_command(label="فتح ملف جهات اتصال")
        file_menu.add_command(label="حفظ المشروع")
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # قائمة التحرير
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="تحرير", menu=edit_menu)
        
        # قائمة اللغة
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="اللغة", menu=lang_menu)
        
        for lang_code, lang_info in self.languages.items():
            lang_menu.add_command(
                label=lang_info['name'],
                command=lambda lc=lang_code: self.change_language(lc)
            )
        
        # قائمة المساعدة
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="عن البرنامج")
        help_menu.add_command(label="الدعم الفني")
        
    def create_top_bar(self):
        """إنشاء الشريط العلوي"""
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # شعار التطبيق
        logo_label = ttk.Label(top_frame, text="WhatsApp Sender Pro", 
                              font=("Arial", 20, "bold"))
        logo_label.pack(side=tk.LEFT)
        
        # معلومات الترخيص
        self.license_info = ttk.Label(top_frame, text="الترخيص: تجريبي", 
                                     font=("Arial", 10))
        self.license_info.pack(side=tk.RIGHT)
        
        # معلومات الجهاز
        device_info = ttk.Label(top_frame, text=f"معرف الجهاز: {self.hwid[:8]}...", 
                               font=("Arial", 9))
        device_info.pack(side=tk.RIGHT, padx=10)
        
    def create_main_content(self):
        """إنشاء المحتوى الرئيسي"""
        # إطار رئيسي مع علامات التبويب
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # علامة تبويب الإرسال
        self.create_send_tab()
        
        # علامة تبويب الإعدادات
        self.create_settings_tab()
        
        # علامة تبويب السجل
        self.create_log_tab()
        
    def create_send_tab(self):
        """إنشاء علامة تبويب الإرسال"""
        send_frame = ttk.Frame(self.notebook)
        self.notebook.add(send_frame, text="إرسال الرسائل")
        
        # إطار جهات الاتصال
        contacts_frame = ttk.LabelFrame(send_frame, text="جهات الاتصال")
        contacts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # شريط أدوات جهات الاتصال
        contacts_toolbar = ttk.Frame(contacts_frame)
        contacts_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(contacts_toolbar, text="تحميل من ملف", 
                  command=self.load_contacts_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(contacts_toolbar, text="إضافة يدويًا").pack(side=tk.LEFT, padx=2)
        ttk.Button(contacts_toolbar, text="حذف المحدد").pack(side=tk.LEFT, padx=2)
        
        # شجرة عرض جهات الاتصال
        columns = ('name', 'phone', 'status')
        self.contacts_tree = ttk.Treeview(contacts_frame, columns=columns, 
                                         show='headings', height=10)
        
        self.contacts_tree.heading('name', text='الاسم')
        self.contacts_tree.heading('phone', text='رقم الهاتف')
        self.contacts_tree.heading('status', text='الحالة')
        
        self.contacts_tree.column('name', width=200)
        self.contacts_tree.column('phone', width=150)
        self.contacts_tree.column('status', width=100)
        
        scrollbar = ttk.Scrollbar(contacts_frame, orient=tk.VERTICAL, 
                                 command=self.contacts_tree.yview)
        self.contacts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.contacts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # إطار الرسالة
        message_frame = ttk.LabelFrame(send_frame, text="الرسالة")
        message_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # حقل الرسالة
        self.message_text = tk.Text(message_frame, height=8, font=("Arial", 11))
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # أزرار تنسيق
        format_toolbar = ttk.Frame(message_frame)
        format_toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(format_toolbar, text="B", width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(format_toolbar, text="I", width=3).pack(side=tk.LEFT, padx=1)
        ttk.Button(format_toolbar, text="U", width=3).pack(side=tk.LEFT, padx=1)
        
        # إطار الصورة
        image_frame = ttk.LabelFrame(send_frame, text="الصورة")
        image_frame.pack(fill=tk.X, padx=5, pady=5)
        
        image_toolbar = ttk.Frame(image_frame)
        image_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(image_toolbar, text="اختيار صورة", 
                  command=self.select_image).pack(side=tk.LEFT, padx=2)
        
        # إعدادات النص على الصورة
        text_settings_frame = ttk.Frame(image_frame)
        text_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(text_settings_frame, text="لون النص:").pack(side=tk.LEFT, padx=5)
        
        self.text_color = tk.StringVar(value="white")
        color_combo = ttk.Combobox(text_settings_frame, textvariable=self.text_color,
                                  values=["white", "black", "red", "green", "blue", 
                                          "yellow", "cyan", "magenta"])
        color_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(text_settings_frame, text="موضع النص:").pack(side=tk.LEFT, padx=5)
        
        self.text_position = tk.StringVar(value="bottom")
        position_combo = ttk.Combobox(text_settings_frame, textvariable=self.text_position,
                                     values=["top", "bottom", "center"])
        position_combo.pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        self.progress = ttk.Progressbar(send_frame, mode='determinate')
        self.progress.pack(fill=tk.X, padx=5, pady=10)
        
        # أزرار التحكم
        control_frame = ttk.Frame(send_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="بدء الإرسال", 
                                   command=self.start_sending)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(control_frame, text="إيقاف", 
                                  command=self.stop_sending, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.test_btn = ttk.Button(control_frame, text="اختبار الاتصال", 
                                  command=self.test_connection)
        self.test_btn.pack(side=tk.LEFT, padx=10)
        
    def create_settings_tab(self):
        """إنشاء علامة تبويب الإعدادات"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="الإعدادات")
        
        # إعدادات WhatsApp
        whatsapp_frame = ttk.LabelFrame(settings_frame, text="إعدادات WhatsApp")
        whatsapp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(whatsapp_frame, text="وقت التأخير بين الرسائل (ثانية):").grid(row=0, column=0, padx=5, pady=5)
        self.delay_var = tk.StringVar(value="2")
        ttk.Entry(whatsapp_frame, textvariable=self.delay_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # إعدادات المظهر
        appearance_frame = ttk.LabelFrame(settings_frame, text="المظهر")
        appearance_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(appearance_frame, text="السمة:").grid(row=0, column=0, padx=5, pady=5)
        self.theme_var = tk.StringVar(value="light")
        ttk.Combobox(appearance_frame, textvariable=self.theme_var, 
                    values=["light", "dark"]).grid(row=0, column=1, padx=5, pady=5)
        
        # إعدادات التحديث التلقائي
        update_frame = ttk.LabelFrame(settings_frame, text="التحديثات")
        update_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_update_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(update_frame, text="التحديث التلقائي", 
                       variable=self.auto_update_var).pack(anchor=tk.W, padx=5, pady=5)
        
    def create_log_tab(self):
        """إنشاء علامة تبويب السجل"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="سجل النشاط")
        
        # مربع النص للسجل
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Courier", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # شريط أدوات السجل
        log_toolbar = ttk.Frame(log_frame)
        log_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_toolbar, text="مسح السجل", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_toolbar, text="حفظ السجل", 
                  command=self.save_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_toolbar, text="تصدير", 
                  command=self.export_log).pack(side=tk.LEFT, padx=2)
        
    def create_status_bar(self):
        """إنشاء شريط الحالة"""
        self.status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="جاهز")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.connection_label = ttk.Label(self.status_bar, text="WhatsApp: غير متصل")
        self.connection_label.pack(side=tk.RIGHT, padx=10)
        
    def load_translations(self):
        """تحميل ملفات الترجمة"""
        self.translations = {
            'ar': {
                'app_title': 'WhatsApp Sender Pro',
                'send_tab': 'إرسال الرسائل',
                'contacts': 'جهات الاتصال',
                'load_file': 'تحميل من ملف',
                'message': 'الرسالة',
                'image': 'الصورة',
                'text_color': 'لون النص',
                'text_position': 'موضع النص',
                'start_sending': 'بدء الإرسال',
                'stop': 'إيقاف',
                'test_connection': 'اختبار الاتصال',
                'settings': 'الإعدادات',
                'activity_log': 'سجل النشاط',
                'ready': 'جاهز',
                'whatsapp_connected': 'WhatsApp: متصل',
                'whatsapp_disconnected': 'WhatsApp: غير متصل'
            },
            'en': {
                'app_title': 'WhatsApp Sender Pro',
                'send_tab': 'Send Messages',
                'contacts': 'Contacts',
                'load_file': 'Load from File',
                'message': 'Message',
                'image': 'Image',
                'text_color': 'Text Color',
                'text_position': 'Text Position',
                'start_sending': 'Start Sending',
                'stop': 'Stop',
                'test_connection': 'Test Connection',
                'settings': 'Settings',
                'activity_log': 'Activity Log',
                'ready': 'Ready',
                'whatsapp_connected': 'WhatsApp: Connected',
                'whatsapp_disconnected': 'WhatsApp: Disconnected'
            }
        }
    
    def change_language(self, lang_code):
        """تغيير اللغة"""
        self.current_language = lang_code
        lang_info = self.languages.get(lang_code, {'dir': 'ltr'})
        
        # تغيير اتجاه النص
        if lang_info['dir'] == 'rtl':
            self.root.option_add('*justify', 'right')
        else:
            self.root.option_add('*justify', 'left')
        
        # تحديث النصوص
        self.update_texts()
    
    def update_texts(self):
        """تحديث النصوص بناءً على اللغة"""
        trans = self.translations.get(self.current_language, {})
        
        # تحديث عناصر الواجهة
        self.root.title(trans.get('app_title', 'WhatsApp Sender Pro'))
        self.status_label.config(text=trans.get('ready', 'Ready'))
        
    def load_contacts_file(self):
        """تحميل جهات اتصال من ملف"""
        file_path = filedialog.askopenfilename(
            title="اختر ملف جهات الاتصال",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # هنا سيتم استدعاء دالة تحميل جهات الاتصال
                self.log(f"تم تحميل الملف: {file_path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر تحميل الملف:\n{str(e)}")
    
    def select_image(self):
        """اختيار صورة"""
        file_path = filedialog.askopenfilename(
            title="اختر صورة",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.log(f"تم اختيار الصورة: {file_path}")
    
    def start_sending(self):
        """بدء عملية الإرسال"""
        # التحقق من اتصال WhatsApp
        if not self.whatsapp_manager or not self.whatsapp_manager.is_running:
            if not self.connect_whatsapp():
                return
        
        # بدء الإرسال في thread منفصل
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        sending_thread = threading.Thread(target=self._send_messages)
        sending_thread.daemon = True
        sending_thread.start()
    
    def _send_messages(self):
        """دالة الإرسال (تعمل في thread منفصل)"""
        try:
            # هنا سيتم استدعاء دالة الإرسال الفعلية
            self.log("بدأت عملية الإرسال...")
            
            # محاكاة عملية الإرسال
            for i in range(10):
                if not self.sending_active:
                    break
                
                self.progress['value'] = (i + 1) * 10
                self.root.update_idletasks()
                
                self.log(f"إرسال الرسالة {i + 1}...")
                threading.Event().wait(1)  # تأخير محاكاة
            
            self.log("اكتملت عملية الإرسال")
            
        except Exception as e:
            self.log(f"خطأ في الإرسال: {str(e)}")
        
        finally:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress['value'] = 0
    
    def stop_sending(self):
        """إيقاف عملية الإرسال"""
        self.sending_active = False
        self.log("تم إيقاف عملية الإرسال")
    
    def test_connection(self):
        """اختبار اتصال WhatsApp"""
        if self.connect_whatsapp():
            messagebox.showinfo("نجاح", "تم الاتصال بـ WhatsApp بنجاح!")
        else:
            messagebox.showerror("خطأ", "تعذر الاتصال بـ WhatsApp")
    
    def connect_whatsapp(self):
        """الاتصال بـ WhatsApp"""
        try:
            if not self.whatsapp_manager:
                from app.core.whatsapp_manager import WhatsAppManager
                self.whatsapp_manager = WhatsAppManager()
            
            if self.whatsapp_manager.open_whatsapp_web():
                self.connection_label.config(text="WhatsApp: متصل")
                self.log("تم الاتصال بـ WhatsApp بنجاح")
                return True
            else:
                self.connection_label.config(text="WhatsApp: غير متصل")
                return False
                
        except Exception as e:
            self.log(f"خطأ في الاتصال بـ WhatsApp: {str(e)}")
            return False
    
    def log(self, message):
        """إضافة رسالة إلى السجل"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
        # تحديث شريط الحالة
        self.status_label.config(text=message[:50])
    
    def clear_log(self):
        """مسح السجل"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """حفظ السجل"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"تم حفظ السجل: {file_path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر حفظ السجل:\n{str(e)}")
    
    def export_log(self):
        """تصدير السجل"""
        # يمكن توسيع هذه الدالة لتصدير بتنسيقات مختلفة
        self.save_log()
    
    def run(self):
        """تشغيل الواجهة"""
        self.root.mainloop()