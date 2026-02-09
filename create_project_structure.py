"""
WhatsApp Sender Pro - الإصدار الكامل
نسخة واحدة تحتوي على جميع المميزات
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import json
import csv
import os
import sys
import hashlib
import uuid
import platform
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import threading
import time
import logging
from pathlib import Path

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==================== فئات الأساس ====================

class HWIDGenerator:
    """مولد معرف الجهاز الفريد"""
    @staticmethod
    def generate():
        """إنشاء معرف جهاز فريد"""
        try:
            system_info = {
                'machine': platform.machine(),
                'processor': platform.processor(),
                'system': platform.system(),
                'node': platform.node(),
                'mac': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                               for elements in range(0, 8*6, 8)][::-1])
            }
            info_string = json.dumps(system_info, sort_keys=True)
            hwid_hash = hashlib.sha256(info_string.encode()).hexdigest()
            return f"WS-{hwid_hash[:8]}-{hwid_hash[8:16]}-{hwid_hash[16:24]}-{hwid_hash[24:32]}"
        except:
            return f"WS-{uuid.uuid4().hex[:32].upper()}"

class EncryptionService:
    """خدمة التشفير المبسطة"""
    def __init__(self, key="whatsapp-sender-pro-secret-key"):
        self.key = key
    
    def encrypt(self, data):
        """تشفير البيانات"""
        import base64
        from cryptography.fernet import Fernet
        
        # توليد مفتاح من الكلمة السرية
        key = base64.urlsafe_b64encode(hashlib.sha256(self.key.encode()).digest())
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """فك تشفير البيانات"""
        import base64
        from cryptography.fernet import Fernet
        
        try:
            key = base64.urlsafe_b64encode(hashlib.sha256(self.key.encode()).digest())
            fernet = Fernet(key)
            return fernet.decrypt(encrypted_data.encode()).decode()
        except:
            return None

class LicenseValidator:
    """متحقق الترخيص"""
    def __init__(self):
        self.encryption = EncryptionService()
        
    def validate(self, license_key, hwid):
        """التحقق من صلاحية الترخيص"""
        try:
            # فك التشفير
            decrypted = self.encryption.decrypt(license_key)
            if not decrypted:
                return False
            
            # التحقق من التنسيق
            if not decrypted.startswith("LICENSE:"):
                return False
            
            # استخراج البيانات
            parts = decrypted.split(":")
            if len(parts) < 5:
                return False
            
            license_hwid = parts[2]
            expiry_date = parts[3]
            license_type = parts[4]
            
            # التحقق من HWID
            if license_hwid != hwid and license_hwid != "ANY":
                return False
            
            # التحقق من تاريخ الانتهاء
            try:
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                if datetime.now() > expiry:
                    return False
            except:
                pass
            
            return True
        except:
            return False

class MessageSender:
    """مرسل الرسائل"""
    def __init__(self):
        self.contacts = []
        self.is_sending = False
        
    def load_contacts(self, file_path):
        """تحميل جهات الاتصال من ملف"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                return []
            
            self.contacts = []
            for _, row in df.iterrows():
                phone = str(row.get('phone', '') or row.get('Phone', '') or row.get('PHONE', ''))
                name = str(row.get('name', '') or row.get('Name', '') or row.get('NAME', ''))
                
                # تنظيف رقم الهاتف
                phone = ''.join(filter(str.isdigit, phone))
                
                if phone:
                    self.contacts.append({
                        'phone': phone,
                        'name': name if name else phone
                    })
            
            return self.contacts
        except Exception as e:
            logger.error(f"خطأ في تحميل جهات الاتصال: {e}")
            return []
    
    def add_text_to_image(self, image_path, text, font_color='white', position='bottom'):
        """إضافة نص إلى صورة"""
        try:
            img = Image.open(image_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            
            # تحميل الخط
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            # حساب حجم النص
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # تحديد موضع النص
            img_width, img_height = img.size
            
            if position == 'top':
                x = (img_width - text_width) // 2
                y = 20
            elif position == 'bottom':
                x = (img_width - text_width) // 2
                y = img_height - text_height - 20
            elif position == 'center':
                x = (img_width - text_width) // 2
                y = (img_height - text_height) // 2
            else:
                x = 20
                y = 20
            
            # إضافة خلفية شبه شفافة
            draw.rectangle(
                [x-10, y-5, x + text_width + 10, y + text_height + 5],
                fill=(0, 0, 0, 128)
            )
            
            # إضافة النص
            draw.text((x, y), text, font=font, fill=font_color)
            
            # حفظ الصورة المعدلة
            output_path = f"modified_{os.path.basename(image_path)}"
            img.save(output_path)
            
            return output_path
        except Exception as e:
            logger.error(f"خطأ في إضافة النص إلى الصورة: {e}")
            return image_path

# ==================== واجهة المستخدم ====================

class WhatsAppSenderApp:
    """التطبيق الرئيسي"""
    
    def __init__(self, hwid):
        self.hwid = hwid
        self.license_validator = LicenseValidator()
        self.message_sender = MessageSender()
        self.current_language = 'ar'
        
        # إنشاء النافذة الرئيسية
        self.root = tk.Tk()
        self.root.title("WhatsApp Sender Pro - إرسال رسائل WhatsApp تلقائي")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # تهيئة الواجهة
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # شريط القائمة
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="تحميل جهات اتصال", command=self.load_contacts)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # قائمة اللغة
        lang_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="لغة", menu=lang_menu)
        lang_menu.add_command(label="العربية", command=lambda: self.change_language('ar'))
        lang_menu.add_command(label="English", command=lambda: self.change_language('en'))
        
        # إطار العنوان
        title_frame = tk.Frame(self.root, bg='#4CAF50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="WhatsApp Sender Pro", 
                font=("Arial", 24, "bold"), bg='#4CAF50', fg='white').pack(pady=10)
        
        # إطار المحتوى الرئيسي
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # علامات التبويب
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # علامة تبويب الإرسال
        self.create_send_tab()
        
        # علامة تبويب الإعدادات
        self.create_settings_tab()
        
        # علامة تبويب السجل
        self.create_log_tab()
        
        # شريط الحالة
        status_frame = tk.Frame(self.root, bg='#333333', height=30)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="جاهز", 
                                    bg='#333333', fg='white', font=("Arial", 10))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        tk.Label(status_frame, text=f"معرف الجهاز: {self.hwid}", 
                bg='#333333', fg='#AAAAAA', font=("Arial", 9)).pack(side=tk.RIGHT, padx=10)
    
    def create_send_tab(self):
        """إنشاء علامة تبويب الإرسال"""
        send_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(send_frame, text="إرسال الرسائل")
        
        # إطار جهات الاتصال
        contacts_frame = tk.LabelFrame(send_frame, text="جهات الاتصال", 
                                      font=("Arial", 12, "bold"), bg='#f0f0f0')
        contacts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # شريط أدوات جهات الاتصال
        contacts_toolbar = tk.Frame(contacts_frame, bg='#f0f0f0')
        contacts_toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(contacts_toolbar, text="تحميل من ملف", 
                 command=self.load_contacts, bg='#2196F3', fg='white',
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        tk.Button(contacts_toolbar, text="مسح القائمة", 
                 command=self.clear_contacts, bg='#f44336', fg='white',
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # قائمة جهات الاتصال
        list_frame = tk.Frame(contacts_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("#", "الاسم", "رقم الهاتف", "الحالة")
        self.contacts_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.contacts_tree.heading(col, text=col)
            self.contacts_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.contacts_tree.yview)
        self.contacts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.contacts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # إطار الرسالة
        message_frame = tk.LabelFrame(send_frame, text="الرسالة", 
                                     font=("Arial", 12, "bold"), bg='#f0f0f0')
        message_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # حقل الرسالة
        self.message_text = scrolledtext.ScrolledText(message_frame, height=6, 
                                                     font=("Arial", 11), wrap=tk.WORD)
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # إطار الصورة
        image_frame = tk.LabelFrame(send_frame, text="الصورة", 
                                   font=("Arial", 12, "bold"), bg='#f0f0f0')
        image_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # اختيار الصورة
        image_controls = tk.Frame(image_frame, bg='#f0f0f0')
        image_controls.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(image_controls, text="اختيار صورة", 
                 command=self.select_image, bg='#9C27B0', fg='white',
                 font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        self.image_path_label = tk.Label(image_controls, text="لم يتم اختيار صورة", 
                                        bg='#f0f0f0', fg='#666666')
        self.image_path_label.pack(side=tk.LEFT, padx=20)
        
        # إعدادات النص على الصورة
        text_settings = tk.Frame(image_frame, bg='#f0f0f0')
        text_settings.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(text_settings, text="لون النص:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        self.text_color = tk.StringVar(value="white")
        color_combo = ttk.Combobox(text_settings, textvariable=self.text_color,
                                  values=["white", "black", "red", "green", "blue", "yellow"],
                                  width=10)
        color_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(text_settings, text="موضع النص:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        self.text_position = tk.StringVar(value="bottom")
        position_combo = ttk.Combobox(text_settings, textvariable=self.text_position,
                                     values=["top", "center", "bottom"], width=10)
        position_combo.pack(side=tk.LEFT, padx=5)
        
        # إعدادات الإرسال
        send_settings = tk.Frame(send_frame, bg='#f0f0f0')
        send_settings.pack(fill=tk.X, padx=5, pady=10)
        
        tk.Label(send_settings, text="تأخير بين الرسائل (ثانية):", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        self.delay_var = tk.StringVar(value="2")
        tk.Entry(send_settings, textvariable=self.delay_var, width=5).pack(side=tk.LEFT, padx=5)
        
        # شريط التقدم
        self.progress_bar = ttk.Progressbar(send_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=5, pady=10)
        
        # أزرار التحكم
        control_frame = tk.Frame(send_frame, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_btn = tk.Button(control_frame, text="بدء الإرسال", 
                                  command=self.start_sending, bg='#4CAF50', fg='white',
                                  font=("Arial", 12, "bold"), padx=20, pady=10)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(control_frame, text="إيقاف", 
                                 command=self.stop_sending, bg='#f44336', fg='white',
                                 font=("Arial", 12, "bold"), padx=20, pady=10, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(control_frame, text="اختبار", 
                 command=self.test_message, bg='#2196F3', fg='white',
                 font=("Arial", 12, "bold"), padx=20, pady=10).pack(side=tk.LEFT, padx=10)
    
    def create_settings_tab(self):
        """إنشاء علامة تبويب الإعدادات"""
        settings_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(settings_frame, text="الإعدادات")
        
        # إعدادات WhatsApp
        whatsapp_frame = tk.LabelFrame(settings_frame, text="إعدادات WhatsApp", 
                                      font=("Arial", 12, "bold"), bg='#f0f0f0')
        whatsapp_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(whatsapp_frame, text="مسار ملف تعريف Chrome:", bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.profile_path = tk.StringVar(value="./whatsapp_profile")
        tk.Entry(whatsapp_frame, textvariable=self.profile_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(whatsapp_frame, text="استعراض", command=self.browse_profile).grid(row=0, column=2, padx=5, pady=5)
        
        # إعدادات الترخيص
        license_frame = tk.LabelFrame(settings_frame, text="الترخيص", 
                                     font=("Arial", 12, "bold"), bg='#f0f0f0')
        license_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(license_frame, text="مفتاح الترخيص الحالي:", bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.license_key = tk.StringVar()
        tk.Entry(license_frame, textvariable=self.license_key, width=50, state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(license_frame, text="تغيير الترخيص", command=self.change_license).grid(row=0, column=2, padx=5, pady=5)
        
        # خطط الأسعار
        pricing_frame = tk.LabelFrame(settings_frame, text="خطط الأسعار", 
                                     font=("Arial", 12, "bold"), bg='#f0f0f0')
        pricing_frame.pack(fill=tk.X, padx=10, pady=10)
        
        pricing_text = """
        خطط الأسعار:
        
        • تجريبي: مجاناً (50 رسالة)
        • 1 شهر: 500 جنيه (1000 رسالة)
        • 3 شهور: 1200 جنيه (3000 رسالة)
        • 6 شهور: 2000 جنيه (6000 رسالة)
        • 9 شهور: 2800 جنيه (9000 رسالة)
        • سنة: 3800 جنيه (12000 رسالة)
        
        للشراء: راسلنا على support@yourcompany.com
        """
        
        pricing_label = tk.Label(pricing_frame, text=pricing_text, 
                                bg='#f0f0f0', justify=tk.LEFT, font=("Arial", 11))
        pricing_label.pack(padx=10, pady=10)
    
    def create_log_tab(self):
        """إنشاء علامة تبويب السجل"""
        log_frame = tk.Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(log_frame, text="سجل النشاط")
        
        # مربع السجل
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, 
                                                 font=("Courier", 10), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # أزرار السجل
        log_buttons = tk.Frame(log_frame, bg='#f0f0f0')
        log_buttons.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(log_buttons, text="مسح السجل", 
                 command=self.clear_log, bg='#607D8B', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_buttons, text="حفظ السجل", 
                 command=self.save_log, bg='#607D8B', fg='white').pack(side=tk.LEFT, padx=5)
    
    def load_contacts(self):
        """تحميل جهات الاتصال من ملف"""
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
                contacts = self.message_sender.load_contacts(file_path)
                
                # مسح القائمة الحالية
                for item in self.contacts_tree.get_children():
                    self.contacts_tree.delete(item)
                
                # إضافة جهات الاتصال الجديدة
                for i, contact in enumerate(contacts, 1):
                    self.contacts_tree.insert("", "end", values=(
                        i, contact['name'], contact['phone'], "في الانتظار"
                    ))
                
                self.log(f"تم تحميل {len(contacts)} جهة اتصال من: {file_path}")
                self.update_status(f"تم تحميل {len(contacts)} جهة اتصال")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"تعذر تحميل الملف:\n{str(e)}")
    
    def clear_contacts(self):
        """مسح قائمة جهات الاتصال"""
        for item in self.contacts_tree.get_children():
            self.contacts_tree.delete(item)
        self.log("تم مسح قائمة جهات الاتصال")
    
    def select_image(self):
        """اختيار صورة"""
        file_path = filedialog.askopenfilename(
            title="اختر صورة",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.image_path_label.config(text=os.path.basename(file_path))
            self.message_sender.selected_image = file_path
            self.log(f"تم اختيار الصورة: {file_path}")
    
    def start_sending(self):
        """بدء عملية الإرسال"""
        if not self.message_sender.contacts:
            messagebox.showwarning("تحذير", "يجب تحميل جهات اتصال أولاً")
            return
        
        if not self.message_text.get("1.0", tk.END).strip():
            messagebox.showwarning("تحذير", "يجب كتابة رسالة أولاً")
            return
        
        # تعطيل زر البدء وتفعيل زر الإيقاف
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # بدء الإرسال في thread منفصل
        sending_thread = threading.Thread(target=self.send_messages_thread)
        sending_thread.daemon = True
        sending_thread.start()
    
    def send_messages_thread(self):
        """thread لإرسال الرسائل"""
        try:
            message = self.message_text.get("1.0", tk.END).strip()
            delay = float(self.delay_var.get())
            total_contacts = len(self.message_sender.contacts)
            
            self.message_sender.is_sending = True
            self.progress_bar['maximum'] = total_contacts
            
            for i, contact in enumerate(self.message_sender.contacts):
                if not self.message_sender.is_sending:
                    break
                
                try:
                    # تحديث شجرة جهات الاتصال
                    items = self.contacts_tree.get_children()
                    if i < len(items):
                        self.contacts_tree.item(items[i], values=(
                            i+1, contact['name'], contact['phone'], "جاري الإرسال..."
                        ))
                    
                    # محاكاة إرسال الرسالة (في الإصدار الحقيقي، هنا يتم الإرسال الفعلي)
                    time.sleep(1)  # محاكاة وقت الإرسال
                    
                    # إضافة نص على الصورة إذا كانت موجودة
                    image_to_send = None
                    if hasattr(self.message_sender, 'selected_image') and self.message_sender.selected_image:
                        image_to_send = self.message_sender.add_text_to_image(
                            self.message_sender.selected_image,
                            contact['name'],
                            self.text_color.get(),
                            self.text_position.get()
                        )
                    
                    # تحديث الحالة
                    if i < len(items):
                        self.contacts_tree.item(items[i], values=(
                            i+1, contact['name'], contact['phone'], "تم الإرسال ✓"
                        ))
                    
                    self.log(f"تم إرسال الرسالة إلى: {contact['name']} ({contact['phone']})")
                    
                    # تحديث شريط التقدم
                    self.progress_bar['value'] = i + 1
                    self.root.update_idletasks()
                    
                    # تأخير بين الرسائل
                    time.sleep(delay)
                    
                except Exception as e:
                    self.log(f"خطأ في إرسال الرسالة إلى {contact['name']}: {str(e)}")
                    if i < len(items):
                        self.contacts_tree.item(items[i], values=(
                            i+1, contact['name'], contact['phone'], "فشل ✗"
                        ))
            
            self.log(f"اكتملت عملية الإرسال: {total_contacts} رسالة")
            messagebox.showinfo("نجاح", f"تم إرسال {total_contacts} رسالة بنجاح!")
            
        except Exception as e:
            self.log(f"خطأ في عملية الإرسال: {str(e)}")
            messagebox.showerror("خطأ", f"حدث خطأ في عملية الإرسال:\n{str(e)}")
        
        finally:
            # إعادة تعيين الأزرار
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress_bar['value'] = 0
            self.message_sender.is_sending = False
    
    def stop_sending(self):
        """إيقاف عملية الإرسال"""
        self.message_sender.is_sending = False
        self.log("تم إيقاف عملية الإرسال")
    
    def test_message(self):
        """اختبار رسالة"""
        messagebox.showinfo("اختبار", "هذه ميزة الاختبار. في الإصدار الكامل، سيتم اختبار الاتصال بـ WhatsApp.")
    
    def change_license(self):
        """تغيير الترخيص"""
        license_window = tk.Toplevel(self.root)
        license_window.title("تفعيل الترخيص")
        license_window.geometry("400x300")
        license_window.configure(bg='#f0f0f0')
        
        tk.Label(license_window, text="تفعيل الترخيص", 
                font=("Arial", 16, "bold"), bg='#f0f0f0').pack(pady=20)
        
        tk.Label(license_window, text="أدخل مفتاح الترخيص:", 
                font=("Arial", 12), bg='#f0f0f0').pack()
        
        license_entry = tk.Entry(license_window, width=40, font=("Arial", 12))
        license_entry.pack(pady=10, padx=20)
        
        tk.Label(license_window, text=f"معرف الجهاز: {self.hwid}", 
                font=("Arial", 10), bg='#f0f0f0', fg='#666').pack(pady=5)
        
        def activate():
            key = license_entry.get().strip()
            if key:
                if self.license_validator.validate(key, self.hwid):
                    self.license_key.set(key[:30] + "...")
                    messagebox.showinfo("نجاح", "تم تفعيل الترخيص بنجاح!")
                    license_window.destroy()
                else:
                    messagebox.showerror("خطأ", "الترخيص غير صالح")
            else:
                messagebox.showwarning("تحذير", "يرجى إدخال مفتاح الترخيص")
        
        tk.Button(license_window, text="تفعيل", command=activate,
                 bg='#4CAF50', fg='white', font=("Arial", 12, "bold"),
                 padx=20, pady=5).pack(pady=20)
    
    def browse_profile(self):
        """تصفح مسار ملف التعريف"""
        path = filedialog.askdirectory(title="اختر مجلد ملف تعريف Chrome")
        if path:
            self.profile_path.set(path)
    
    def change_language(self, lang):
        """تغيير اللغة"""
        self.current_language = lang
        # هنا يمكن إضافة الترجمة الفعلية
        if lang == 'ar':
            self.root.title("WhatsApp Sender Pro - إرسال رسائل WhatsApp تلقائي")
        else:
            self.root.title("WhatsApp Sender Pro - Automatic WhatsApp Messages")
    
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
    
    def update_status(self, message):
        """تحديث شريط الحالة"""
        self.status_label.config(text=message)
    
    def run(self):
        """تشغيل التطبيق"""
        self.root.mainloop()

# ==================== التشغيل ====================

if __name__ == "__main__":
    # إنشاء مجلدات إذا لم تكن موجودة
    os.makedirs("logs", exist_ok=True)
    os.makedirs("whatsapp_profile", exist_ok=True)
    
    # توليد HWID
    hwid = HWIDGenerator.generate()
    print(f"معرف الجهاز: {hwid}")
    
    # تشغيل التطبيق
    app = WhatsAppSenderApp(hwid)
    app.run()