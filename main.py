# main.py - الملف الرئيسي للتطبيق
"""
WhatsApp Sender Pro - نظام إرسال رسائل WhatsApp تلقائي مع إدارة تراخيص متقدمة
الإصدار: 1.0.0
"""

import sys
import os
from pathlib import Path

# إضافة المسار إلى sys.path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# يجب أن تكون الاستيرادات هكذا لأن utils خارج app
from utils.logger import setup_logger
from app.core.license_validator import LicenseValidator
from app.ui.user_interface import WhatsAppSenderApp
from app.core.hwid_generator import HWIDGenerator
from app.services.firestore_service import FirestoreService
from app.core.update_checker import UpdateChecker
from app.core.encryption_service import EncryptionService

import tkinter as tk
from tkinter import messagebox
import threading

class WhatsAppSenderPro:
    def __init__(self):
        """تهيئة التطبيق الرئيسي"""
        self.logger = setup_logger("main_app")
        self.hwid = HWIDGenerator.generate()
        self.license_validator = LicenseValidator()
        self.encryption_service = EncryptionService()
        self.firestore_service = None
        self.app = None
        
    def initialize_firebase(self):
        """تهيئة اتصال Firebase"""
        try:
            self.firestore_service = FirestoreService()
            self.firestore_service.initialize()
            return True
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة Firebase: {e}")
            return False
    
    def check_license(self):
        """فحص الترخيص"""
        try:
            # قراءة الترخيص المحلي
            license_file = current_dir / "license.key"
            if license_file.exists():
                with open(license_file, 'r') as f:
                    license_key = f.read().strip()
                
                # فك تشفير الترخيص
                decrypted_license = self.encryption_service.decrypt(license_key)
                
                # التحقق من الترخيص
                if self.license_validator.validate(decrypted_license, self.hwid):
                    # التحقق من صلاحية الترخيص عبر Firebase
                    if self.firestore_service:
                        is_valid = self.firestore_service.validate_license(decrypted_license, self.hwid)
                        if is_valid:
                            return True
            return False
        except Exception as e:
            self.logger.error(f"خطأ في فحص الترخيص: {e}")
            return False
    
    def show_license_window(self):
        """عرض نافذة إدخال الترخيص"""
        license_window = tk.Toplevel()
        license_window.title("تفعيل الترخيص")
        license_window.geometry("400x300")
        license_window.configure(bg="#f0f0f0")
        
        # عناصر واجهة الترخيص
        tk.Label(license_window, text="WhatsApp Sender Pro", 
                font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=20)
        
        tk.Label(license_window, text="أدخل مفتاح الترخيص:", 
                font=("Arial", 12), bg="#f0f0f0").pack()
        
        license_entry = tk.Entry(license_window, width=40, font=("Arial", 12))
        license_entry.pack(pady=10, padx=20)
        
        tk.Label(license_window, text=f"معرف الجهاز: {self.hwid}", 
                font=("Arial", 10), bg="#f0f0f0", fg="#666").pack(pady=5)
        
        def activate_license():
            """تفعيل الترخيص"""
            license_key = license_entry.get().strip()
            if license_key:
                # تشفير وحفظ الترخيص
                encrypted_key = self.encryption_service.encrypt(license_key)
                with open(current_dir / "license.key", 'w') as f:
                    f.write(encrypted_key)
                
                # التحقق من الترخيص
                if self.check_license():
                    messagebox.showinfo("نجاح", "تم تفعيل الترخيص بنجاح!")
                    license_window.destroy()
                    self.start_main_app()
                else:
                    messagebox.showerror("خطأ", "الترخيص غير صالح أو منتهي الصلاحية")
            else:
                messagebox.showwarning("تحذير", "يرجى إدخال مفتاح الترخيص")
        
        tk.Button(license_window, text="تفعيل", command=activate_license,
                 bg="#4CAF50", fg="white", font=("Arial", 12), 
                 padx=20, pady=5).pack(pady=20)
        
        # رابط لشراء ترخيص
        tk.Label(license_window, text="شراء ترخيص جديد", 
                font=("Arial", 10, "underline"), 
                fg="blue", cursor="hand2").pack()
        
        license_window.mainloop()
    
    def start_main_app(self):
        """بدء التطبيق الرئيسي"""
        self.app = WhatsAppSenderApp(self.hwid, self.firestore_service)
        self.app.run()
    
    def run(self):
        """تشغيل التطبيق"""
        self.logger.info("بدء تشغيل WhatsApp Sender Pro")
        
        # تهيئة Firebase
        if not self.initialize_firebase():
            messagebox.showerror("خطأ", "تعذر الاتصال بخادم المصادقة")
            return
        
        # التحقق من التحديثات
        update_checker = UpdateChecker()
        if update_checker.check_for_updates():
            if messagebox.askyesno("تحديث", "يوجد تحديث جديد. هل تريد التحديث الآن؟"):
                update_checker.download_update()
                return
        
        # التحقق من الترخيص
        if self.check_license():
            self.start_main_app()
        else:
            self.show_license_window()

if __name__ == "__main__":
    # إنشاء المجلدات الأساسية
    folders = ['app/core', 'app/ui', 'app/services', 'app/assets',
               'config', 'database/migrations', 'utils', 'tests', 'logs']
    
    for folder in folders:
        os.makedirs(current_dir / folder, exist_ok=True)
    
    # تشغيل التطبيق
    app = WhatsAppSenderPro()
    app.run()