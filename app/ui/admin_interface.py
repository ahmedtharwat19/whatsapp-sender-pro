# app/ui/admin_interface.py
"""
واجهة المسؤول - لإدارة التراخيص والمستخدمين
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, timedelta
import logging
from app.core.license_validator import LicenseValidator
from app.core.hwid_generator import HWIDGenerator
from app.services.firestore_service import FirestoreService

class AdminInterface:
    def __init__(self, firebase_config):
        """تهيئة واجهة المسؤول"""
        self.logger = logging.getLogger(__name__)
        self.license_validator = LicenseValidator()
        self.firestore_service = FirestoreService(firebase_config)
        
        self.root = tk.Tk()
        self.root.title("WhatsApp Sender Pro - Admin Panel")
        self.root.geometry("1000x700")
        
        self.init_ui()
        
    def init_ui(self):
        """تهيئة واجهة المستخدم"""
        # إطار رئيسي مع علامات التبويب
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # علامة تبويب إنشاء الترخيص
        self.create_license_tab()
        
        # علامة تبويب إدارة التراخيص
        self.create_manage_tab()
        
        # علامة تبويب الإحصائيات
        self.create_stats_tab()
        
    def create_license_tab(self):
        """إنشاء علامة تبويب إنشاء الترخيص"""
        license_frame = ttk.Frame(self.notebook)
        self.notebook.add(license_frame, text="إنشاء ترخيص")
        
        # معلومات الترخيص
        info_frame = ttk.LabelFrame(license_frame, text="معلومات الترخيص")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="نوع الترخيص:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.license_type = ttk.Combobox(info_frame, values=[
            'trial', '1_month', '3_months', '6_months', '9_months', '1_year'
        ])
        self.license_type.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.license_type.set('1_month')
        
        ttk.Label(info_frame, text="مدة الترخيص (أيام):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.duration = tk.StringVar(value="30")
        ttk.Entry(info_frame, textvariable=self.duration, width=10).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(info_frame, text="معرف الجهاز (اختياري):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.hwid_entry = ttk.Entry(info_frame, width=40)
        self.hwid_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # زر إنشاء HWID
        ttk.Button(info_frame, text="إنشاء HWID جديد", 
                  command=self.generate_hwid).grid(row=2, column=2, padx=5, pady=5)
        
        # معلومات العميل
        client_frame = ttk.LabelFrame(license_frame, text="معلومات العميل")
        client_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(client_frame, text="اسم العميل:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_name = ttk.Entry(client_frame, width=30)
        self.client_name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(client_frame, text="البريد الإلكتروني:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_email = ttk.Entry(client_frame, width=30)
        self.client_email.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(client_frame, text="رقم الهاتف:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.client_phone = ttk.Entry(client_frame, width=20)
        self.client_phone.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # زر إنشاء الترخيص
        ttk.Button(license_frame, text="إنشاء الترخيص", 
                  command=self.generate_license, 
                  style="Accent.TButton").pack(pady=20)
        
        # حقل عرض الترخيص
        ttk.Label(license_frame, text="مفتاح الترخيص:").pack(anchor=tk.W, padx=10)
        self.license_key_display = tk.Text(license_frame, height=5, width=60)
        self.license_key_display.pack(fill=tk.X, padx=10, pady=5)
        
        # أزرار النسخ
        button_frame = ttk.Frame(license_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="نسخ المفتاح", 
                  command=self.copy_license_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حفظ في ملف", 
                  command=self.save_license_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="إرسال بالبريد", 
                  command=self.send_license_email).pack(side=tk.LEFT, padx=5)
        
    def create_manage_tab(self):
        """إنشاء علامة تبويب إدارة التراخيص"""
        manage_frame = ttk.Frame(self.notebook)
        self.notebook.add(manage_frame, text="إدارة التراخيص")
        
        # شريط البحث
        search_frame = ttk.Frame(manage_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="بحث:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="بحث", 
                  command=self.search_licenses).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="عرض الكل", 
                  command=self.load_all_licenses).pack(side=tk.LEFT, padx=5)
        
        # شجرة عرض التراخيص
        columns = ('license_key', 'client_name', 'type', 'expiry_date', 'hwid', 'status')
        self.license_tree = ttk.Treeview(manage_frame, columns=columns, show='headings', height=20)
        
        self.license_tree.heading('license_key', text='مفتاح الترخيص')
        self.license_tree.heading('client_name', text='اسم العميل')
        self.license_tree.heading('type', text='النوع')
        self.license_tree.heading('expiry_date', text='تاريخ الانتهاء')
        self.license_tree.heading('hwid', text='معرف الجهاز')
        self.license_tree.heading('status', text='الحالة')
        
        scrollbar = ttk.Scrollbar(manage_frame, orient=tk.VERTICAL, command=self.license_tree.yview)
        self.license_tree.configure(yscrollcommand=scrollbar.set)
        
        self.license_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # أزرار الإدارة
        manage_buttons = ttk.Frame(manage_frame)
        manage_buttons.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(manage_buttons, text="تفعيل", 
                  command=self.activate_license).pack(side=tk.LEFT, padx=5)
        ttk.Button(manage_buttons, text="تعطيل", 
                  command=self.deactivate_license).pack(side=tk.LEFT, padx=5)
        ttk.Button(manage_buttons, text="تحديث", 
                  command=self.update_license).pack(side=tk.LEFT, padx=5)
        ttk.Button(manage_buttons, text="حذف", 
                  command=self.delete_license).pack(side=tk.LEFT, padx=5)
        ttk.Button(manage_buttons, text="تفاصيل", 
                  command=self.show_license_details).pack(side=tk.LEFT, padx=5)
        
    def create_stats_tab(self):
        """إنشاء علامة تبويب الإحصائيات"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="الإحصائيات")
        
        # إطار الإحصائيات
        stats_data = [
            ("إجمالي التراخيص", "150"),
            ("التراخيص النشطة", "120"),
            ("التراخيص المنتهية", "30"),
            ("الدخل الشهري", "50,000 جنيه"),
            ("المستخدمون النشطون", "85"),
            ("الرسائل المرسلة", "1,250,000")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            frame = ttk.LabelFrame(stats_frame, text=label)
            frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(frame, text=value, font=("Arial", 24, "bold")).pack(pady=20)
        
        # جعل الخلايا قابلة للتوسيع
        for i in range(2):
            stats_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            stats_frame.grid_columnconfigure(i, weight=1)
        
    def generate_hwid(self):
        """إنشاء معرف جهاز جديد"""
        hwid = HWIDGenerator.generate()
        self.hwid_entry.delete(0, tk.END)
        self.hwid_entry.insert(0, hwid)
        
    def generate_license(self):
        """إنشاء ترخيص جديد"""
        try:
            # جمع المعلومات
            license_type = self.license_type.get()
            duration = int(self.duration.get())
            hwid = self.hwid_entry.get() or None
            
            client_name = self.client_name.get()
            client_email = self.client_email.get()
            client_phone = self.client_phone.get()
            
            # التحقق من المعلومات المطلوبة
            if not client_name or not client_email:
                messagebox.showwarning("تحذير", "يرجى إدخال اسم العميل والبريد الإلكتروني")
                return
            
            # إنشاء الترخيص
            license_key = self.license_validator.generate_license(
                license_type=license_type,
                duration_days=duration,
                hwid=hwid
            )
            
            if license_key:
                # حفظ في قاعدة البيانات
                license_data = {
                    'license_key': license_key,
                    'type': license_type,
                    'client_name': client_name,
                    'client_email': client_email,
                    'client_phone': client_phone,
                    'hwid': hwid,
                    'created_date': datetime.now().isoformat(),
                    'expiry_date': (datetime.now() + timedelta(days=duration)).isoformat(),
                    'status': 'active',
                    'uses': 0
                }
                
                # حفظ في Firebase
                if self.firestore_service:
                    self.firestore_service.save_license(license_data)
                
                # عرض المفتاح
                self.license_key_display.delete(1.0, tk.END)
                self.license_key_display.insert(1.0, license_key)
                
                messagebox.showinfo("نجاح", "تم إنشاء الترخيص بنجاح!")
            else:
                messagebox.showerror("خطأ", "تعذر إنشاء الترخيص")
                
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ:\n{str(e)}")
    
    def copy_license_key(self):
        """نسخ مفتاح الترخيص"""
        license_key = self.license_key_display.get(1.0, tk.END).strip()
        if license_key:
            self.root.clipboard_clear()
            self.root.clipboard_append(license_key)
            messagebox.showinfo("نسخ", "تم نسخ مفتاح الترخيص")
    
    def save_license_file(self):
        """حفظ الترخيص في ملف"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def send_license_email(self):
        """إرسال الترخيص بالبريد الإلكتروني"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def search_licenses(self):
        """بحث التراخيص"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def load_all_licenses(self):
        """تحميل جميع التراخيص"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def activate_license(self):
        """تفعيل الترخيص"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def deactivate_license(self):
        """تعطيل الترخيص"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def update_license(self):
        """تحديث الترخيص"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def delete_license(self):
        """حذف الترخيص"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def show_license_details(self):
        """عرض تفاصيل الترخيص"""
        # سيتم تنفيذها لاحقاً
        pass
    
    def run(self):
        """تشغيل واجهة المسؤول"""
        self.root.mainloop()

# كود لإنشاء واجهة المسؤول إذا تم تشغيل الملف مباشرة
if __name__ == "__main__":
    try:
        with open("config/firebase_config.json", "r") as f:
            firebase_config = json.load(f)
        
        app = AdminInterface(firebase_config)
        app.run()
    except Exception as e:
        print(f"خطأ في تشغيل واجهة المسؤول: {e}")