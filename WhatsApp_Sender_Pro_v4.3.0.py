# ============================================================
# WhatsApp Sender Pro - Professional Edition
# Version: 4.3.0
# Build Date: 2026-02-03
# Build Number: 20260203
# Developer: Ahmed Tharwat
# Contact: +201061007999 | ahmed.tharwat19@gmail.com
# ============================================================

import sys
import os
import subprocess
import time
import json
import random
import shutil
import logging
import threading
import atexit
import hashlib
import platform
import uuid
import base64
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

# ================= AUTO INSTALL =================
REQUIRED_PACKAGES = [
    "selenium", "webdriver-manager", "pyperclip", "pillow", "psutil", "chromedriver-autoinstaller==0.6.0",
    "PyQt6", "pandas", "openpyxl", "arabic-reshaper", "python-bidi",
    "requests", "cryptography", "deep-translator", "pywin32",
]

def ensure_packages():
    """تثبيت المكتبات المطلوبة تلقائياً - مرة واحدة فقط"""
    import subprocess
    import sys
    
    # إنشاء ملف علامة لتتبع التثبيت
    installed_file = Path(__file__).parent / "installed.txt"
    
    # التحقق إذا كانت المكتبات مثبتة مسبقاً
    if installed_file.exists():
        print("✅ المكتبات مثبتة بالفعل")
        return
    
    print("📦 تثبيت المكتبات المطلوبة لأول مرة...")
    
    # إنشاء قائمة المكتبات التي تحتاج للتثبيت
    packages_to_install = []
    
    for package in REQUIRED_PACKAGES:
        try:
            # معالجة PyQt6 بشكل خاص
            if package == "PyQt6":
                __import__("PyQt6.QtWidgets")
            elif package == "python-bidi":
                __import__("bidi")
            elif package == "deep-translator":
                __import__("deep_translator")
            else:
                # استخراج اسم الحزمة بدون إصدار
                package_name = package.split("==")[0]
                __import__(package_name)
            print(f"✅ {package_name if 'package_name' in locals() else package} - مثبت بالفعل")
        except ImportError:
            packages_to_install.append(package)
            print(f"❌ {package} - غير مثبت")
    
    # تثبيت المكتبات المفقودة فقط
    if packages_to_install:
        print(f"\n📦 جاري تثبيت {len(packages_to_install)} مكتبة...")
        for i, package in enumerate(packages_to_install, 1):
            print(f"\n[{i}/{len(packages_to_install)}] 📦 جاري تثبيت {package}...")
            try:
                # استخدام pip مع خيارات لتقليل الرسائل
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    package, 
                    "--quiet",  # تقليل الإخراج
                    "--disable-pip-version-check"  # عدم التحقق من إصدار pip
                ])
                print(f"✅ تم تثبيت {package} بنجاح")
            except subprocess.CalledProcessError as e:
                print(f"❌ فشل تثبيت {package}: {e}")
                # يمكنك اختيار ما إذا تريد الاستمرار أو التوقف
                continue
        
        # حفظ علامة أن المكتبات تم تثبيتها
        try:
            with open(installed_file, 'w') as f:
                f.write(f"المكتبات مثبتة بتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"إصدار بايثون: {sys.version}\n")
            print("\n✅ تم تثبيت جميع المكتبات بنجاح!")
        except:
            pass
    else:
        print("\n✅ جميع المكتبات مثبتة بالفعل!")
        # حفظ علامة حتى لو كانت كل المكتبات مثبتة
        try:
            with open(installed_file, 'w') as f:
                f.write(f"المكتبات مثبتة بالفعل بتاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        except:
            pass
    
    print("-" * 50)

# استدعاء الدالة مرة واحدة
ensure_packages()

# ================= IMPORTS =================
# يجب استيراد PyQt6 أولاً
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings, QSize
from PyQt6.QtGui import QIcon, QColor, QFont, QPalette, QLinearGradient, QBrush, QPainter, QPixmap,QAction

# استيراد المكتبات الأخرى
import psutil
import pyperclip
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= DEVELOPER PASSWORD =================
DEVELOPER_PASSWORD = "Admin@2026"  # كلمة سر المطور - يمكن تغييرها

# ================= APP METADATA =================
APP_NAME = "WhatsApp Sender Pro"
VERSION = "4.3.3"
BUILD_DATE = "2026-02-03"
BUILD_NUMBER = "20260203"
DEVELOPER = "Ahmed Tharwat"
PHONE = "+201061007999"
EMAIL = "ahmed.tharwat19@gmail.com"
WEBSITE = ""
PRICING_TIER = "PROFESSIONAL"

# ================= PATHS =================
APP_DIR = Path(__file__).parent.absolute()
HOME = Path.home()
CONFIG_DIR = APP_DIR / "config"
LOGS_DIR = APP_DIR / "logs"
FONTS_DIR = APP_DIR / "fonts"
LICENSE_FILE = CONFIG_DIR / "license.dat"
CONFIG_FILE = CONFIG_DIR / "settings.json"

for dir_path in [CONFIG_DIR, LOGS_DIR, FONTS_DIR]:
    dir_path.mkdir(exist_ok=True)

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================= TRANSLATION SYSTEM =================
class TranslationManager:
    """نظام الترجمة المتكامل"""
    
    def __init__(self):
        self.current_language = "ar"
        self.translations = {}
        self.load_translations()
        
    def load_translations(self):
        """تحميل الترجمات"""
        try:
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source='auto', target='ar')
        except:
            self.translator = None
            
        # ترجمات عربية
        self.translations = {
            "ar": {
                # مصطلحات المطور
                "developer_access": "دخول المطور",
                "enter_developer_password": "أدخل كلمة مرور المطور للوصول",
                "password": "كلمة المرور",
                "enter_password": "أدخل كلمة المرور",
                "incorrect_password": "كلمة مرور غير صحيحة",
                "developer_license_generator": "مولد تراخيص المطور",
                "developer_control_panel": "لوحة تحكم المطور",
                "developer_info": "معلومات المطور",
                "create_new_license": "إنشاء ترخيص جديد",
                "buyer_name": "اسم المشتري",
                "buyer_hardware_id": "Hardware ID الخاص بالمشتري",
                "generate_random": "توليد عشوائي",
                "create_license": "إنشاء ترخيص",
                "fill_all_required_fields": "يرجى ملء جميع الحقول المطلوبة",
                "subscription_type": "نوع الاشتراك",
                "license_info": "معلومات الترخيص",
                "license_key": "مفتاح الترخيص",
                "buyer": "المشتري",
                "device_id": "معرف الجهاز",
                "expiry_date": "تاريخ الانتهاء",
                "activation_instructions": "تعليمات التفعيل",
                "send_license_key_to_buyer": "أرسل مفتاح الترخيص للمشتري",
                "in_app_press_license_button": "في التطبيق، اضغط على زر 'الترخيص'",
                "enter_license_key_and_activate": "أدخل مفتاح الترخيص واضغط تفعيل",
                "note_works_on_one_device": "ملاحظة: هذا المفتاح يعمل على جهاز واحد فقط",
                "encrypted_data": "البيانات المشفرة",
                "license_created_successfully": "تم إنشاء الترخيص بنجاح",
                "copy_license": "نسخ الترخيص",
                "license_copied_to_clipboard": "تم نسخ الترخيص إلى الحافظة",
                "save_file": "حفظ الملف",
                "no_license_to_save": "لا يوجد ترخيص لحفظه",
                "save_license_file": "حفظ ملف الترخيص",
                "license_saved_to": "تم حفظ ملف الترخيص في",
                "failed_to_save_file": "فشل حفظ الملف",
                
                # الترجمة العامة (كل النصوص تترجم)
                "app_title": "WhatsApp Sender Pro",
                "welcome": "مرحباً بك",
                "select_language": "اختر اللغة",
                "continue": "متابعة",
                "settings": "الإعدادات",
                "contacts": "جهات الاتصال",
                "messages": "الرسائل",
                "send": "إرسال",
                "logs": "السجلات",
                "license": "الترخيص",
                "trial": "نسخة تجريبية",
                "expired": "منتهية الصلاحية",
                "active": "نشط",
                "days_remaining": "أيام متبقية",
                "hardware_id": "معرف الجهاز",
                "subscription": "الاشتراك",
                "monthly": "شهري",
                "quarterly": "ربع سنوي",
                "half_yearly": "نصف سنوي",
                "yearly": "سنوي",
                "price": "السعر",
                "activate": "تفعيل",
                "buy_now": "شراء الآن",
                "contact_support": "التواصل مع الدعم",
                "phone": "الهاتف",
                "email": "البريد الإلكتروني",
                "open_whatsapp": "فتح واتساب",
                "status": "الحالة",
                "ready": "جاهز",
                "sending": "جاري الإرسال",
                "completed": "مكتمل",
                "failed": "فاشل",
                "success": "نجاح",
                "progress": "التقدم",
                "total": "الإجمالي",
                "remaining": "المتبقي",
                "stop": "إيقاف",
                "start": "بدء",
                "save": "حفظ",
                "load": "تحميل",
                "clear": "مسح",
                "delete": "حذف",
                "edit": "تعديل",
                "add": "إضافة",
                "cancel": "إلغاء",
                "ok": "موافق",
                "yes": "نعم",
                "no": "لا",
                "error": "خطأ",
                "warning": "تحذير",
                "info": "معلومات",
                "success_message": "تمت العملية بنجاح",
                "error_message": "حدث خطأ",
                "confirm": "تأكيد",
                "are_you_sure": "هل أنت متأكد؟",
                "exit": "خروج",
                "close": "إغلاق",
                "about": "حول",
                "help": "مساعدة",
                "update": "تحديث",
                "version": "الإصدار",
                "build": "البناء",
                "developer": "المطور",
                "all_rights_reserved": "جميع الحقوق محفوظة",
                "trial_version": "نسخة تجريبية - 30 يوم",
                "trial_expired": "انتهت النسخة التجريبية",
                "enter_license": "أدخل مفتاح الترخيص",
                "activate_license": "تفعيل الترخيص",
                "invalid_license": "مفتاح ترخيص غير صالح",
                "license_activated": "تم تفعيل الترخيص بنجاح",
                "subscription_prices": "أسعار الاشتراكات",
                "monthly_price": "500 ج.م",
                "quarterly_price": "1200 ج.م",
                "half_yearly_price": "2000 ج.م",
                "yearly_price": "3800 ج.م",
                "contact_developer": "تواصل مع المطور للشراء",
                "whatsapp_status": "حالة واتساب",
                "connected": "متصل",
                "disconnected": "غير متصل",
                "connecting": "جاري الاتصال",
                "qr_scan": "امسح رمز QR",
                "message_template": "قالب الرسالة",
                "variables": "المتغيرات",
                "name_variable": "{name} - اسم المرسل إليه",
                "phone_variable": "{phone} - رقم الهاتف",
                "date_variable": "{date} - التاريخ الحالي",
                "number_variable": "{number} - رقم التسلسل",
                "image_settings": "إعدادات الصورة",
                "add_text_to_image": "إضافة نص على الصورة",
                "text_color": "لون النص",
                "text_size": "حجم النص",
                "font": "الخط",
                "frame": "إطار",
                "background": "خلفية",
                "contacts_file": "ملف جهات الاتصال",
                "excel_csv": "Excel أو CSV",
                "load_contacts": "تحميل جهات الاتصال",
                "contacts_loaded": "تم تحميل جهات الاتصال",
                "invalid_numbers": "أرقام غير صالحة",
                "valid_numbers": "أرقام صالحة",
                "delay_settings": "إعدادات التأخير",
                "delay_minutes": "تأخير البدء (دقائق)",
                "delay_seconds": "تأخير بين الرسائل (ثواني)",
                "random_delay": "تأخير عشوائي",
                "sending_settings": "إعدادات الإرسال",
                "extract_names": "استخراج الأسماء من واتساب",
                "send_image": "إرسال صورة",
                "send_message": "إرسال رسالة نصية",
                "logs_and_reports": "السجلات والتقارير",
                "activity_log": "سجل النشاطات",
                "send_report": "تقرير الإرسال",
                "export_report": "تصدير التقرير",
                "clear_logs": "مسح السجلات",
                "save_logs": "حفظ السجلات",
                "no_logs": "لا توجد سجلات",
                "search": "بحث",
                "filter": "تصفية",
                "date": "التاريخ",
                "time": "الوقت",
                "contact": "جهة الاتصال",
                "message": "الرسالة",
                "status_col": "الحالة",
                "language_changed": "تم تغيير اللغة",
                "restart_required": "يرجى إعادة تشغيل التطبيق",
                "appearance": "المظهر",
                "theme": "السمة",
                "light": "فاتح",
                "dark": "داكن",
                "auto": "تلقائي",
                "font_size": "حجم الخط",
                "small": "صغير",
                "medium": "متوسط",
                "large": "كبير",
                "sidebar": "الشريط الجانبي",
                "show_sidebar": "إظهار الشريط الجانبي",
                "hide_sidebar": "إخفاء الشريط الجانبي",
                "dashboard": "لوحة التحكم",
                "statistics": "الإحصائيات",
                "sent_today": "مرسلة اليوم",
                "sent_this_week": "مرسلة هذا الأسبوع",
                "sent_this_month": "مرسلة هذا الشهر",
                "total_sent": "إجمالي المرسل",
                "success_rate": "نسبة النجاح",
                "failed_count": "عدد الفاشل",
                "pending_count": "قيد الانتظار",
                "no_image_selected": "لم يتم اختيار صورة",
                "select_image": "اختيار صورة",
                "view": "عرض",
                "number": "الرقم",
                "whatsapp_opened": "تم فتح واتساب",
                "whatsapp_error": "خطأ في فتح واتساب",
                "enter": "دخول",
                "days": "أيام",
                "errors": "أخطاء",
                "warnings": "تحذيرات",
                "show_window": "إظهار النافذة",
                "start_sending": "بدء الإرسال",
                "stop_sending": "إيقاف الإرسال",
                "hide_application": "إخفاء التطبيق",
                "hide_application_question": "هل تريد إخفاء التطبيق إلى System Tray؟\n\nنعم: يخفي إلى System Tray\nلا: يغلق التطبيق",
                "app_running_in_background": "التطبيق يعمل في الخلفية",
                "choose_your_preferred_language": "Choose your preferred language / اختر لغتك المفضلة",
                "how_to_get_license_key": "كيفية الحصول على مفتاح ترخيص",
                "copy_hardware_id_above": "انسخ معرف الجهاز (Hardware ID) أعلاه",
                "contact_developer_via": "تواصل مع المطور عبر",
                "whatsapp": "واتساب",
                "send_hardware_id_and_choose_plan": "أرسل معرف الجهاز واختر باقة الاشتراك المناسبة",
                "receive_license_within_24_hours": "ستستلم مفتاح الترخيص خلال 24 ساعة",
                "logs_saved_to": "تم حفظ السجلات في",
                "error_saving_logs": "خطأ في حفظ السجلات",
                "export_report_coming_soon": "ميزة تصدير التقارير قريباً",
                "choose_color": "اختر لون",
            },
            "en": {
                # Developer terms
                "developer_access": "Developer Access",
                "enter_developer_password": "Enter developer password to access",
                "password": "Password",
                "enter_password": "Enter password",
                "incorrect_password": "Incorrect password",
                "developer_license_generator": "Developer License Generator",
                "developer_control_panel": "Developer Control Panel",
                "developer_info": "Developer Information",
                "create_new_license": "Create New License",
                "buyer_name": "Buyer Name",
                "buyer_hardware_id": "Buyer's Hardware ID",
                "generate_random": "Generate Random",
                "create_license": "Create License",
                "fill_all_required_fields": "Please fill all required fields",
                "subscription_type": "Subscription Type",
                "license_info": "License Information",
                "license_key": "License Key",
                "buyer": "Buyer",
                "device_id": "Device ID",
                "expiry_date": "Expiry Date",
                "activation_instructions": "Activation Instructions",
                "send_license_key_to_buyer": "Send license key to buyer",
                "in_app_press_license_button": "In the app, press the 'License' button",
                "enter_license_key_and_activate": "Enter license key and press activate",
                "note_works_on_one_device": "Note: This key works on one device only",
                "encrypted_data": "Encrypted Data",
                "license_created_successfully": "License created successfully",
                "copy_license": "Copy License",
                "license_copied_to_clipboard": "License copied to clipboard",
                "save_file": "Save File",
                "no_license_to_save": "No license to save",
                "save_license_file": "Save License File",
                "license_saved_to": "License saved to",
                "failed_to_save_file": "Failed to save file",
                
                # إضافة ترجمات إنجليزية للأقسام الأخرى
                "app_title": "WhatsApp Sender Pro",
                "welcome": "Welcome",
                "select_language": "Select Language",
                "continue": "Continue",
                "settings": "Settings",
                "contacts": "Contacts",
                "messages": "Messages",
                "send": "Send",
                "logs": "Logs",
                "license": "License",
                "trial": "Trial",
                "expired": "Expired",
                "active": "Active",
                "days_remaining": "Days Remaining",
                "hardware_id": "Hardware ID",
                "subscription": "Subscription",
                "monthly": "Monthly",
                "quarterly": "Quarterly",
                "half_yearly": "Half Yearly",
                "yearly": "Yearly",
                "price": "Price",
                "activate": "Activate",
                "buy_now": "Buy Now",
                "contact_support": "Contact Support",
                "phone": "Phone",
                "email": "Email",
                "open_whatsapp": "Open WhatsApp",
                "status": "Status",
                "ready": "Ready",
                "sending": "Sending",
                "completed": "Completed",
                "failed": "Failed",
                "success": "Success",
                "progress": "Progress",
                "total": "Total",
                "remaining": "Remaining",
                "stop": "Stop",
                "start": "Start",
                "save": "Save",
                "load": "Load",
                "clear": "Clear",
                "delete": "Delete",
                "edit": "Edit",
                "add": "Add",
                "cancel": "Cancel",
                "ok": "OK",
                "yes": "Yes",
                "no": "No",
                "error": "Error",
                "warning": "Warning",
                "info": "Info",
                "success_message": "Operation completed successfully",
                "error_message": "An error occurred",
                "confirm": "Confirm",
                "are_you_sure": "Are you sure?",
                "exit": "Exit",
                "close": "Close",
                "about": "About",
                "help": "Help",
                "update": "Update",
                "version": "Version",
                "build": "Build",
                "developer": "Developer",
                "all_rights_reserved": "All rights reserved",
                "trial_version": "Trial Version - 30 days",
                "trial_expired": "Trial expired",
                "enter_license": "Enter license key",
                "activate_license": "Activate License",
                "invalid_license": "Invalid license key",
                "license_activated": "License activated successfully",
                "subscription_prices": "Subscription Prices",
                "monthly_price": "500 EGP",
                "quarterly_price": "1200 EGP",
                "half_yearly_price": "2000 EGP",
                "yearly_price": "3800 EGP",
                "contact_developer": "Contact developer for purchase",
                "whatsapp_status": "WhatsApp Status",
                "connected": "Connected",
                "disconnected": "Disconnected",
                "connecting": "Connecting",
                "qr_scan": "Scan QR Code",
                "message_template": "Message Template",
                "variables": "Variables",
                "name_variable": "{name} - Recipient name",
                "phone_variable": "{phone} - Phone number",
                "date_variable": "{date} - Current date",
                "number_variable": "{number} - Serial number",
                "image_settings": "Image Settings",
                "add_text_to_image": "Add text to image",
                "text_color": "Text Color",
                "text_size": "Text Size",
                "font": "Font",
                "frame": "Frame",
                "background": "Background",
                "contacts_file": "Contacts File",
                "excel_csv": "Excel or CSV",
                "load_contacts": "Load Contacts",
                "contacts_loaded": "Contacts loaded",
                "invalid_numbers": "Invalid numbers",
                "valid_numbers": "Valid numbers",
                "delay_settings": "Delay Settings",
                "delay_minutes": "Start delay (minutes)",
                "delay_seconds": "Delay between messages (seconds)",
                "random_delay": "Random delay",
                "sending_settings": "Sending Settings",
                "extract_names": "Extract names from WhatsApp",
                "send_image": "Send image",
                "send_message": "Send text message",
                "logs_and_reports": "Logs and Reports",
                "activity_log": "Activity Log",
                "send_report": "Send Report",
                "export_report": "Export Report",
                "clear_logs": "Clear Logs",
                "save_logs": "Save Logs",
                "no_logs": "No logs",
                "search": "Search",
                "filter": "Filter",
                "date": "Date",
                "time": "Time",
                "contact": "Contact",
                "message": "Message",
                "status_col": "Status",
                "language_changed": "Language changed",
                "restart_required": "Please restart the application",
                "appearance": "Appearance",
                "theme": "Theme",
                "light": "Light",
                "dark": "Dark",
                "auto": "Auto",
                "font_size": "Font Size",
                "small": "Small",
                "medium": "Medium",
                "large": "Large",
                "sidebar": "Sidebar",
                "show_sidebar": "Show Sidebar",
                "hide_sidebar": "Hide Sidebar",
                "dashboard": "Dashboard",
                "statistics": "Statistics",
                "sent_today": "Sent Today",
                "sent_this_week": "Sent This Week",
                "sent_this_month": "Sent This Month",
                "total_sent": "Total Sent",
                "success_rate": "Success Rate",
                "failed_count": "Failed Count",
                "pending_count": "Pending Count",
                "no_image_selected": "No image selected",
                "select_image": "Select Image",
                "view": "View",
                "number": "Number",
                "whatsapp_opened": "WhatsApp opened",
                "whatsapp_error": "WhatsApp error",
                "enter": "Enter",
                "days": "days",
                "errors": "Errors",
                "warnings": "Warnings",
                "show_window": "Show Window",
                "start_sending": "Start Sending",
                "stop_sending": "Stop Sending",
                "hide_application": "Hide Application",
                "hide_application_question": "Do you want to hide the application to System Tray?\n\nYes: Hide to System Tray\nNo: Close application",
                "app_running_in_background": "Application running in background",
                "choose_your_preferred_language": "Choose your preferred language",
                "how_to_get_license_key": "How to get license key",
                "copy_hardware_id_above": "Copy hardware ID above",
                "contact_developer_via": "Contact developer via",
                "whatsapp": "WhatsApp",
                "send_hardware_id_and_choose_plan": "Send hardware ID and choose subscription plan",
                "receive_license_within_24_hours": "You will receive license key within 24 hours",
                "logs_saved_to": "Logs saved to",
                "error_saving_logs": "Error saving logs",
                "export_report_coming_soon": "Export report feature coming soon",
                "choose_color": "Choose Color",
            }
        }
        
        # تحميل الترجمات للغات الأخرى من العربية
        for lang_code in ["fr", "es"]:
            if lang_code != "ar" and lang_code != "en" and self.translator:
                self.translations[lang_code] = {}
                for key, arabic_text in self.translations["ar"].items():
                    try:
                        translated = self.translator.translate(arabic_text, target=lang_code)
                        self.translations[lang_code][key] = translated
                    except:
                        self.translations[lang_code][key] = arabic_text
        
    def translate(self, key, target_lang=None):
        """ترجمة مفتاح معين"""
        lang = target_lang or self.current_language
        
        if lang in self.translations and key in self.translations[lang]:
            return self.translations[lang][key]
        
        if key in self.translations.get("ar", {}):
            return self.translations["ar"][key]
        
        return key
    
    def set_language(self, lang_code):
        """تغيير اللغة الحالية"""
        self.current_language = lang_code
        self.save_settings()
        
    def get_available_languages(self):
        """الحصول على اللغات المتاحة"""
        return {
            "ar": "العربية",
            "en": "English",
            "fr": "Français",
            "es": "Español"
        }
    
    def save_settings(self):
        """حفظ إعدادات اللغة"""
        settings = {"language": self.current_language}
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f)
        except Exception as e:
            logger.error(f"Error saving language settings: {e}")
    
    def load_settings(self):
        """تحميل إعدادات اللغة"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_language = settings.get("language", "ar")
        except Exception as e:
            logger.error(f"Error loading language settings: {e}")

# إنشاء مدير الترجمة العالمي
translator = TranslationManager()
translator.load_settings()

# ================= DEVELOPER LOCK DIALOG =================
class DeveloperLockDialog(QDialog):
    """حوار قفل المطور"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔒 " + translator.translate("developer_access"))
        self.setFixedSize(450, 300)  # زيادة الحجم
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # العنوان
        title = QLabel("🔒 " + translator.translate("developer_access"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            padding: 15px;
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            border-radius: 10px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # وصف
        desc = QLabel(translator.translate("enter_developer_password"))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #666; font-size: 14px; margin: 10px 0;")
        layout.addWidget(desc)
        
        # حقل كلمة المرور
        password_layout = QVBoxLayout()
        password_layout.setSpacing(8)
        
        password_label = QLabel(translator.translate("password") + ":")
        password_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText(translator.translate("enter_password"))
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                font-size: 14px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #6c5ce7;
                background: #f8f9ff;
            }
        """)
        self.password_input.returnPressed.connect(self.check_password)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # رسالة الخطأ
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            color: #e74c3c;
            font-size: 13px;
            padding: 8px;
            background: #ffeaea;
            border-radius: 6px;
            border: 1px solid #ffcccc;
        """)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        enter_btn = QPushButton("🔓 " + translator.translate("enter"))
        enter_btn.setMinimumSize(120, 45)
        enter_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #27ae60 0%, #219653 100%);
                box-shadow: 0 3px 10px rgba(46, 204, 113, 0.3);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
        """)
        enter_btn.clicked.connect(self.check_password)
        
        cancel_btn = QPushButton(translator.translate("cancel"))
        cancel_btn.setMinimumSize(120, 45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #7f8c8d;
                box-shadow: 0 3px 10px rgba(149, 165, 166, 0.3);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(enter_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        # تلميح
        hint = QLabel("💡 Developer Password: " + DEVELOPER_PASSWORD)
        hint.setStyleSheet("color: #7f8c8d; font-size: 12px; text-align: center; margin-top: 20px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)
    
    def check_password(self):
        """التحقق من كلمة المرور"""
        entered_password = self.password_input.text().strip()
        
        if entered_password == DEVELOPER_PASSWORD:
            self.accept()
        else:
            self.error_label.setText("❌ " + translator.translate("incorrect_password"))
            self.error_label.setVisible(True)
            self.password_input.clear()
            self.password_input.setFocus()
            
            # تأثير اهتزاز
            self.shake_dialog()
    
    def shake_dialog(self):
        """تأثير اهتزاز للحوار"""
        import math
        pos = self.pos()
        for i in range(1, 10):
            x = pos.x() + math.sin(i * 0.5) * 5
            self.move(int(x), pos.y())
            QApplication.processEvents()
            time.sleep(0.02)
        self.move(pos)
        
# ================= DEVELOPER LICENSE GENERATOR =================
class DeveloperLicenseGenerator(QDialog):
    """شاشة المطور لإنشاء تراخيص"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👨‍💻 " + translator.translate("developer_license_generator"))
        self.setMinimumSize(1200, 900)  # زيادة الحجم
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # العنوان
        title = QLabel("🔧 " + translator.translate("developer_control_panel"))
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # معلومات المطور
        info_group = QGroupBox("📋 " + translator.translate("developer_info"))
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #667eea;
                border-radius: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #667eea;
            }
        """)
        info_layout = QVBoxLayout(info_group)
        
        dev_info = QLabel(f"""
        <div style='font-size: 14px; line-height: 1.6;'>
        <b style='color: #333; font-size: 15px;'>👨‍💻 {translator.translate('developer')}:</b> {DEVELOPER}<br>
        <b style='color: #333; font-size: 15px;'>📱 {translator.translate('phone')}:</b> {PHONE}<br>
        <b style='color: #333; font-size: 15px;'>📧 {translator.translate('email')}:</b> {EMAIL}<br>
        <b style='color: #333; font-size: 15px;'>🚀 {translator.translate('version')}:</b> v{VERSION}<br>
        <b style='color: #333; font-size: 15px;'>🏷️ {translator.translate('pricing_tier')}:</b> {PRICING_TIER}
        </div>
        """)
        dev_info.setStyleSheet("padding: 15px; background: #f8f9fa; border-radius: 8px;")
        info_layout.addWidget(dev_info)
        
        layout.addWidget(info_group)
        
        # إنشاء ترخيص
        create_group = QGroupBox("🔐 " + translator.translate("create_new_license"))
        create_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #28a745;
                border-radius: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                color: #28a745;
            }
        """)
        create_layout = QVBoxLayout(create_group)
        create_layout.setSpacing(15)
        
        # معلومات المشتري
        buyer_layout = QFormLayout()
        buyer_layout.setSpacing(12)
        buyer_layout.setContentsMargins(10, 10, 10, 10)
        
        # اسم المشتري
        self.buyer_name = QLineEdit()
        self.buyer_name.setPlaceholderText(translator.translate("buyer_name"))
        self.buyer_name.setMinimumHeight(40)
        self.buyer_name.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        buyer_layout.addRow("👤 " + translator.translate("buyer_name") + ":", self.buyer_name)
        
        # هاتف المشتري
        self.buyer_phone = QLineEdit()
        self.buyer_phone.setPlaceholderText(translator.translate("phone"))
        self.buyer_phone.setMinimumHeight(40)
        self.buyer_phone.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        buyer_layout.addRow("📱 " + translator.translate("phone") + ":", self.buyer_phone)
        
        # إيميل المشتري
        self.buyer_email = QLineEdit()
        self.buyer_email.setPlaceholderText(translator.translate("email"))
        self.buyer_email.setMinimumHeight(40)
        self.buyer_email.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        buyer_layout.addRow("📧 " + translator.translate("email") + ":", self.buyer_email)
        
        create_layout.addLayout(buyer_layout)
        
        # نوع الاشتراك
        plan_layout = QHBoxLayout()
        plan_layout.setSpacing(10)
        
        plan_label = QLabel("📅 " + translator.translate("subscription_type") + ":")
        plan_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.plan_combo = QComboBox()
        self.plan_combo.setMinimumHeight(40)
        self.plan_combo.addItems([
            "📊 " + translator.translate("monthly") + " - 500 ج.م (30 يوم)",
            "📈 " + translator.translate("quarterly") + " - 1200 ج.م (90 يوم)", 
            "📉 " + translator.translate("half_yearly") + " - 2000 ج.م (180 يوم)",
            "🚀 " + translator.translate("yearly") + " - 3800 ج.م (365 يوم)"
        ])
        self.plan_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
                selection-background-color: #007bff;
                selection-color: white;
            }
        """)
        
        plan_layout.addWidget(plan_label)
        plan_layout.addWidget(self.plan_combo)
        plan_layout.addStretch()
        
        create_layout.addLayout(plan_layout)
        
        # Hardware ID
        hwid_layout = QHBoxLayout()
        hwid_layout.setSpacing(10)
        
        hwid_label = QLabel("🆔 " + translator.translate("hardware_id") + ":")
        hwid_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.hwid_input = QLineEdit()
        self.hwid_input.setPlaceholderText(translator.translate("buyer_hardware_id"))
        self.hwid_input.setMinimumHeight(40)
        self.hwid_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        
        generate_btn = QPushButton("🎲 " + translator.translate("generate_random"))
        generate_btn.setMinimumHeight(40)
        generate_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        generate_btn.clicked.connect(self.generate_random_hwid)
        
        hwid_layout.addWidget(hwid_label)
        hwid_layout.addWidget(self.hwid_input, stretch=1)
        hwid_layout.addWidget(generate_btn)
        
        create_layout.addLayout(hwid_layout)
        
        # زر الإنشاء - الإصلاح هنا
        create_btn = QPushButton("🚀 " + translator.translate("create_license"))
        create_btn.setMinimumHeight(60)  # زيادة الارتفاع
        create_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 15px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                border: none;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #20c997 0%, #28a745 100%);
                border: 2px solid #1e7e34;
                padding: 10px 20px;
            }
            QPushButton:pressed {
                transform: translateY(0);
            }
        """)
        create_btn.clicked.connect(self.generate_license)
        create_layout.addWidget(create_btn)
        
        layout.addWidget(create_group)
        
        # إنشاء حاوية قابلة للتمرير لعرض الترخيص
        license_scroll = QScrollArea()
        license_scroll.setWidgetResizable(True)
        license_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                background: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #e9ecef;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #6c757d;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #495057;
            }
        """)
        
        license_container = QWidget()
        license_container_layout = QVBoxLayout(license_container)
        
        # عنوان عرض الترخيص
        display_label = QLabel("📄 " + translator.translate("license_info"))
        display_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 15px;
            background: #e9ecef;
            border-radius: 8px;
        """)
        license_container_layout.addWidget(display_label)
        
        # عرض الترخيص المنشأ
        self.license_display = QTextEdit()
        self.license_display.setReadOnly(True)
        self.license_display.setMinimumHeight(200)
        self.license_display.setStyleSheet("""
            QTextEdit {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        license_container_layout.addWidget(self.license_display)
        
        license_scroll.setWidget(license_container)
        layout.addWidget(license_scroll, stretch=1)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        copy_btn = QPushButton("📋 " + translator.translate("copy_license"))
        copy_btn.setMinimumHeight(45)
        copy_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: #138496;
                box-shadow: 0 3px 10px rgba(23, 162, 184, 0.3);
            }
        """)
        copy_btn.clicked.connect(self.copy_license)
        
        save_btn = QPushButton("💾 " + translator.translate("save_file"))
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: #218838;
                box-shadow: 0 3px 10px rgba(40, 167, 69, 0.3);
            }
        """)
        save_btn.clicked.connect(self.save_license_file)
        
        close_btn = QPushButton("❌ " + translator.translate("close"))
        close_btn.setMinimumHeight(45)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                padding: 12px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: #c82333;
                box-shadow: 0 3px 10px rgba(220, 53, 69, 0.3);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)


    def generate_random_hwid(self):
        """توليد Hardware ID عشوائي"""
        hwid = base64.b32encode(hashlib.md5(str(uuid.uuid4()).encode()).digest()).decode()[:16]
        self.hwid_input.setText(hwid.upper())
        self.hwid_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 14px;
                border: 2px solid #28a745;
                border-radius: 8px;
                background: #f8fff9;
                font-weight: bold;
                color: #155724;
            }
        """)
    
    def generate_license(self):
        """إنشاء ترخيص"""
        # جمع المعلومات
        buyer_name = self.buyer_name.text().strip()
        buyer_phone = self.buyer_phone.text().strip()
        buyer_email = self.buyer_email.text().strip()
        hwid = self.hwid_input.text().strip()
        
        if not all([buyer_name, hwid]):
            QMessageBox.warning(self, translator.translate("warning"), translator.translate("fill_all_required_fields"))
            return
        
        # تحديد نوع الاشتراك
        plan_map = {
            "📊 " + translator.translate("monthly") + " - 500 ج.م (30 يوم)": "monthly",
            "📈 " + translator.translate("quarterly") + " - 1200 ج.م (90 يوم)": "quarterly", 
            "📉 " + translator.translate("half_yearly") + " - 2000 ج.م (180 يوم)": "half_yearly",
            "🚀 " + translator.translate("yearly") + " - 3800 ج.م (365 يوم)": "yearly"
        }
        selected_plan = self.plan_combo.currentText()
        plan_code = plan_map.get(selected_plan, "monthly")
        
        # حساب تاريخ الانتهاء
        plan_days = {
            "monthly": 30,
            "quarterly": 90,
            "half_yearly": 180,
            "yearly": 365
        }
        
        expiry_date = (datetime.now() + timedelta(days=plan_days.get(plan_code, 30))).strftime("%Y-%m-%d")
        expiry_datetime = (datetime.now() + timedelta(days=plan_days.get(plan_code, 30))).isoformat()
        
        # إنشاء مفتاح الترخيص
        key_base = f"{hwid}_whatsapp_pro_{plan_code.upper()}_{VERSION.replace('.', '_')}"
        key_hash = hashlib.sha256(key_base.encode()).hexdigest()[:20].upper()
        license_key = f"WSP-{plan_code[:3].upper()}-{key_hash}"
        
        # إنشاء بيانات الترخيص
        license_data = {
            "license_key": license_key,
            "plan": plan_code,
            "expiry_date": expiry_datetime,
            "hardware_id": hwid,
            "buyer_info": {
                "name": buyer_name,
                "phone": buyer_phone,
                "email": buyer_email
            },
            "generated_date": datetime.now().isoformat(),
            "version": VERSION,
            "developer": DEVELOPER,
            "developer_contact": PHONE,
            "developer_email": EMAIL
        }
        
        # تشفير البيانات
        from cryptography.fernet import Fernet
        
        def generate_key():
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'whatsapp_sender_pro_salt_v4',
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(b'whatsapp_sender_pro_secret_key_2026'))
        
        key = generate_key()
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(license_data).encode()).decode()
        
        # عرض الترخيص بشكل منسق
        display_text = f"""
╔{'═' * 75}╗
║{'📋 ' + translator.translate('license_info').center(73)}║
╠{'═' * 75}╣
║ 🔑  {translator.translate('license_key')}: {license_key:<50}║
╠{'─' * 75}╣
║ 👤  {translator.translate('buyer')}: {buyer_name:<55}║
║ 📱  {translator.translate('phone')}: {buyer_phone if buyer_phone else 'N/A':<55}║
║ 📧  {translator.translate('email')}: {buyer_email if buyer_email else 'N/A':<55}║
╠{'─' * 75}╣
║ 📅  {translator.translate('subscription_type')}: {plan_code.capitalize():<55}║
║ 🆔  {translator.translate('device_id')}: {hwid:<55}║
║ ⏰  {translator.translate('expiry_date')}: {expiry_date:<55}║
╠{'═' * 75}╣
║{'📝 ' + translator.translate('activation_instructions').center(73)}║
╠{'─' * 75}╣
║ 1. {translator.translate('send_license_key_to_buyer'):<70}║
║ 2. {translator.translate('in_app_press_license_button'):<70}║
║ 3. {translator.translate('enter_license_key_and_activate'):<70}║
║                                                                           ║
║ ⚠️  {translator.translate('note_works_on_one_device'):<70}║
╠{'═' * 75}╣
║{'🔒 ' + translator.translate('encrypted_data').center(73)}║
╠{'─' * 75}╣
║ {encrypted_data[:70]:<73}║
║ {encrypted_data[70:140] if len(encrypted_data) > 70 else '':<73}║
║ {encrypted_data[140:210] if len(encrypted_data) > 140 else '':<73}║
║ {encrypted_data[210:280] if len(encrypted_data) > 210 else '':<73}║
║ {encrypted_data[280:350] if len(encrypted_data) > 280 else '':<73}║
╚{'═' * 75}╝
"""
        
        self.license_display.setText(display_text)
        self.current_license_data = encrypted_data
        
        # إضافة نغمة نجاح
        QApplication.beep()
        
        QMessageBox.information(self, "✅ " + translator.translate("success"), 
                              translator.translate("license_created_successfully"))
        

    def copy_license(self):
        """نسخ الترخيص إلى الحافظة"""
        if hasattr(self, 'current_license_data') and self.current_license_data:
            pyperclip.copy(self.current_license_data)
            QMessageBox.information(self, translator.translate("success"), 
                                  translator.translate("license_copied_to_clipboard"))
        else:
            QMessageBox.warning(self, translator.translate("warning"), 
                              translator.translate("no_license_to_save"))

    def save_license_file(self):
        """حفظ ملف الترخيص"""
        if not hasattr(self, 'current_license_data') or not self.current_license_data:
            QMessageBox.warning(self, translator.translate("warning"), 
                              translator.translate("no_license_to_save"))
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, translator.translate("save_license_file"),
            str(APP_DIR / f"license_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dat"),
            "License Files (*.dat);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.current_license_data)
                QMessageBox.information(self, translator.translate("success"), 
                                      f"{translator.translate('license_saved_to')}: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, translator.translate("error"), 
                                   f"{translator.translate('failed_to_save_file')}: {e}")
                
# ================= LICENSE SYSTEM =================
class LicenseManager:
    """نظام الترخيص والتفعيل المتكامل"""
    
    def __init__(self):
        self.hardware_id = self.generate_hardware_id()
        self.trial_days = 30
        self.license_data = self.load_license()
        self.pricing = {
            "monthly": {"price": 500, "days": 30, "name_ar": translator.translate("monthly"), "name_en": "Monthly"},
            "quarterly": {"price": 1200, "days": 90, "name_ar": translator.translate("quarterly"), "name_en": "3 Months"},
            "half_yearly": {"price": 2000, "days": 180, "name_ar": translator.translate("half_yearly"), "name_en": "6 Months"},
            "yearly": {"price": 3800, "days": 365, "name_ar": translator.translate("yearly"), "name_en": "Yearly"}
        }
        
    def generate_hardware_id(self):
        """إنشاء معرف فريد للجهاز"""
        try:
            system_info = {
                "platform": platform.system(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "node": platform.node(),
                "mac": hex(uuid.getnode()),
                "install_date": self.get_install_date()
            }
            
            info_string = json.dumps(system_info, sort_keys=True)
            hardware_hash = hashlib.sha256(info_string.encode()).hexdigest()
            short_id = base64.b32encode(hashlib.md5(hardware_hash.encode()).digest()).decode()[:16]
            
            return short_id
        except Exception as e:
            logger.error(f"Error generating hardware ID: {e}")
            return str(uuid.uuid4())[:16]
    
    def get_install_date(self):
        """الحصول على تاريخ التثبيت"""
        install_file = CONFIG_DIR / "install.dat"
        if install_file.exists():
            try:
                with open(install_file, 'r') as f:
                    return f.read().strip()
            except:
                pass
        
        install_date = datetime.now().strftime("%Y-%m-%d")
        try:
            with open(install_file, 'w') as f:
                f.write(install_date)
        except:
            pass
        return install_date
    
    def load_license(self):
        """تحميل بيانات الترخيص"""
        default_license = {
            "type": "trial",
            "activated": False,
            "activation_date": None,
            "expiry_date": (datetime.now() + timedelta(days=self.trial_days)).isoformat(),
            "license_key": None,
            "hardware_id": self.hardware_id,
            "plan": None
        }
        
        try:
            if LICENSE_FILE.exists():
                with open(LICENSE_FILE, 'r') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted = self.decrypt_license(encrypted_data)
                        if decrypted:
                            return {**default_license, **decrypted}
        except Exception as e:
            logger.error(f"Error loading license: {e}")
        
        return default_license
    
    def save_license(self):
        """حفظ بيانات الترخيص"""
        try:
            encrypted = self.encrypt_license(self.license_data)
            with open(LICENSE_FILE, 'w') as f:
                f.write(encrypted)
        except Exception as e:
            logger.error(f"Error saving license: {e}")
    
    def encrypt_license(self, data):
        """تشفير بيانات الترخيص"""
        try:
            key = self.generate_key()
            f = Fernet(key)
            json_data = json.dumps(data).encode()
            return f.encrypt(json_data).decode()
        except:
            return base64.b64encode(json.dumps(data).encode()).decode()
    
    def decrypt_license(self, encrypted_data):
        """فك تشفير بيانات الترخيص"""
        try:
            key = self.generate_key()
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_data.encode())
            return json.loads(decrypted)
        except:
            try:
                return json.loads(base64.b64decode(encrypted_data).decode())
            except:
                return None
    
    def generate_key(self):
        """إنشاء مفتاح تشفير"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'whatsapp_sender_pro_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b'whatsapp_sender_secret_key'))
        return key
    
    def is_activated(self):
        """التحقق إذا كان الترخيص مفعل"""
        return self.license_data.get("activated", False)
    
    def is_trial(self):
        """التحقق إذا كانت نسخة تجريبية"""
        return self.license_data.get("type") == "trial"
    
    def get_days_remaining(self):
        """الحصول على عدد الأيام المتبقية"""
        try:
            expiry = datetime.fromisoformat(self.license_data.get("expiry_date", ""))
            remaining = (expiry - datetime.now()).days
            return max(0, remaining)
        except:
            return 0
    
    def is_expired(self):
        """التحقق إذا كان الترخيص منتهي"""
        return self.get_days_remaining() <= 0
    
    def activate_license(self, license_key):
        """تفعيل الترخيص"""
        try:
            if self.validate_license_key(license_key):
                plan = self.extract_plan_from_key(license_key)
                days = self.pricing.get(plan, {}).get("days", 30)
                
                self.license_data = {
                    "type": "premium",
                    "activated": True,
                    "activation_date": datetime.now().isoformat(),
                    "expiry_date": (datetime.now() + timedelta(days=days)).isoformat(),
                    "license_key": license_key,
                    "hardware_id": self.hardware_id,
                    "plan": plan
                }
                
                self.save_license()
                return True, translator.translate("license_activated")
            else:
                return False, translator.translate("invalid_license")
        except Exception as e:
            logger.error(f"Error activating license: {e}")
            return False, str(e)
    

    def validate_license_key(self, key):
        """التحقق من صحة مفتاح الترخيص"""
        if not key or len(key) < 10:
            return False
        
        # محاولة فك التشفير والتحقق من البيانات
        try:
            decrypted = self.decrypt_license(key)
            if not decrypted:
                return False
            
            # التحقق من Hardware ID
            license_hwid = decrypted.get("hardware_id", "")
            if license_hwid != self.hardware_id:
                logger.warning(f"Hardware ID mismatch: {license_hwid} != {self.hardware_id}")
                return False
            
            # التحقق من تاريخ الانتهاء
            expiry_date = decrypted.get("expiry_date", "")
            if expiry_date:
                expiry = datetime.fromisoformat(expiry_date)
                if datetime.now() > expiry:
                    logger.warning("License expired")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating license: {e}")
            return False
    
    def extract_plan_from_key(self, key):
        """استخراج نوع الاشتراك من المفتاح"""
        plans = ["monthly", "quarterly", "half_yearly", "yearly"]
        for plan in plans:
            if plan.upper() in key.upper():
                return plan
        return "monthly"
    
    def get_license_info(self):
        """الحصول على معلومات الترخيص"""
        return {
            "hardware_id": self.hardware_id,
            "type": self.license_data.get("type", "trial"),
            "activated": self.is_activated(),
            "expired": self.is_expired(),
            "days_remaining": self.get_days_remaining(),
            "plan": self.license_data.get("plan"),
            "expiry_date": self.license_data.get("expiry_date")
        }

# إنشاء مدير الترخيص العالمي
license_manager = LicenseManager()

# ================= UI COMPONENTS =================
class ModernButton(QPushButton):
    """زر حديث بتصميم احترافي"""
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if icon:
            self.setIcon(icon)
        self.apply_style()
    
    def apply_style(self):
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #25D366, stop:1 #128C7E);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #128C7E, stop:1 #075E54);
            }
            QPushButton:pressed {
                background: #075E54;
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """)

class CardWidget(QFrame):
    """واجهة بطاقة حديثة"""
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            CardWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding-bottom: 10px;
                border-bottom: 2px solid #25D366;
            """)
            self.layout.addWidget(title_label)

# ================= SIDE PANE =================
class SidePane(QFrame):
    """الشريط الجانبي للسجلات"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350)
        self.setStyleSheet("""
            SidePane {
                background-color: #f8f9fa;
                border-left: 1px solid #dee2e6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # عنوان السجلات
        header = QLabel("📋 " + translator.translate("activity_log"))
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding: 10px;
            background: #e9ecef;
            border-radius: 8px;
        """)
        layout.addWidget(header)
        
        # شريط البحث
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(translator.translate("search"))
        self.search_input.setStyleSheet("""
            padding: 8px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background: white;
        """)
        self.search_input.textChanged.connect(self.filter_logs)
        
        search_btn = QPushButton("🔍")
        search_btn.setFixedWidth(40)
        search_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # عرض السجلات
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_display)
        
        # أزرار التحكم في السجلات
        buttons_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ " + translator.translate("clear"))
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_logs)
        
        self.save_btn = QPushButton("💾 " + translator.translate("save"))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        self.save_btn.clicked.connect(self.save_logs)
        
        self.export_btn = QPushButton("📊 " + translator.translate("export_report"))
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        self.export_btn.clicked.connect(self.export_report)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.export_btn)
        layout.addLayout(buttons_layout)
        
        # معلومات سريعة
        self.stats_label = QLabel("📊 " + translator.translate("statistics"))
        self.stats_label.setStyleSheet("""
            font-size: 12px;
            color: #6c757d;
            padding: 10px;
            background: #e9ecef;
            border-radius: 6px;
        """)
        layout.addWidget(self.stats_label)
        
        self.logs = []
        
    def add_log(self, message, level="INFO"):
        """إضافة سجل جديد"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append({"time": timestamp, "level": level, "message": message, "full": log_entry})
        
        color = "#000000"
        if level == "ERROR":
            color = "#dc3545"
        elif level == "WARNING":
            color = "#ffc107"
        elif level == "SUCCESS":
            color = "#28a745"
        
        self.log_display.append(f'<span style="color: {color};">{log_entry}</span>')
        
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        self.update_stats()
    
    def filter_logs(self, text):
        """تصفية السجلات"""
        self.log_display.clear()
        for log in self.logs:
            if text.lower() in log["message"].lower() or text.lower() in log["level"].lower():
                self.log_display.append(log["full"])
    
    def clear_logs(self):
        """مسح السجلات"""
        self.logs = []
        self.log_display.clear()
        self.add_log("Logs cleared", "INFO")
    
    def save_logs(self):
        """حفظ السجلات"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, translator.translate("save_logs"),
            str(LOGS_DIR / f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"),
            "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for log in self.logs:
                        f.write(log["full"] + "\n")
                self.add_log(translator.translate("logs_saved_to") + f": {file_path}", "SUCCESS")
            except Exception as e:
                self.add_log(translator.translate("error_saving_logs") + f": {e}", "ERROR")
    
    def export_report(self):
        """تصدير تقرير"""
        self.add_log(translator.translate("export_report_coming_soon"), "INFO")
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        total = len(self.logs)
        errors = len([l for l in self.logs if l["level"] == "ERROR"])
        warnings = len([l for l in self.logs if l["level"] == "WARNING"])
        
        stats_text = f"📊 {translator.translate('total')}: {total} | ❌ {translator.translate('errors')}: {errors} | ⚠️ {translator.translate('warnings')}: {warnings}"
        self.stats_label.setText(stats_text)

# ================= LANGUAGE SELECTION DIALOG =================
class LanguageSelectionDialog(QDialog):
    """حوار اختيار اللغة"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translator.translate("select_language"))
        self.setFixedSize(500, 400)
        self.selected_language = "ar"
        
        self.setup_ui()
        self.apply_modern_style()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        welcome_label = QLabel("🌍 " + translator.translate("select_language"))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #25D366;
            margin-bottom: 20px;
        """)
        layout.addWidget(welcome_label)
        
        desc_label = QLabel(translator.translate("choose_your_preferred_language"))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        languages = translator.get_available_languages()
        
        for code, name in languages.items():
            btn = QPushButton(f"{self.get_language_flag(code)} {name}")
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 2px solid #dee2e6;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: bold;
                    color: #333;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #25D366;
                }
            """)
            btn.clicked.connect(lambda checked, c=code: self.select_language(c))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        version_label = QLabel(f"{APP_NAME} v{VERSION}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #999; font-size: 12px;")
        layout.addWidget(version_label)
    
    def get_language_flag(self, code):
        flags = {"ar": "🇸🇦", "en": "🇬🇧", "fr": "🇫🇷", "es": "🇪🇸"}
        return flags.get(code, "🌐")
    
    def select_language(self, code):
        self.selected_language = code
        translator.set_language(code)
        self.accept()
    
    def apply_modern_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)

# ================= LICENSE DIALOG =================
class LicenseDialog(QDialog):
    """حوار الترخيص والتفعيل"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translator.translate("license"))
        self.setMinimumSize(700, 600)
        self.setup_ui()
        self.load_license_info()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("🔐 " + translator.translate("license"))
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        self.info_group = QGroupBox(translator.translate("subscription"))
        self.info_group.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout = QVBoxLayout(self.info_group)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 8px;")
        info_layout.addWidget(self.status_label)
        
        self.hardware_label = QLabel(f"{translator.translate('hardware_id')}: {license_manager.hardware_id}")
        self.hardware_label.setStyleSheet("font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 6px;")
        self.hardware_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addWidget(self.hardware_label)
        
        layout.addWidget(self.info_group)
        
        tabs = QTabWidget()
        
        activation_tab = QWidget()
        activation_layout = QVBoxLayout(activation_tab)
        
        if license_manager.is_trial() and not license_manager.is_expired():
            trial_info = QLabel(f"🎁 {translator.translate('trial_version')}: {license_manager.get_days_remaining()} {translator.translate('days_remaining')}")
            trial_info.setStyleSheet("""
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            """)
            activation_layout.addWidget(trial_info)
        elif license_manager.is_expired():
            expired_info = QLabel(f"⛔ {translator.translate('trial_expired')}")
            expired_info.setStyleSheet("""
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            """)
            activation_layout.addWidget(expired_info)
        
        key_layout = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText(translator.translate("enter_license"))
        self.key_input.setStyleSheet("padding: 12px; font-size: 14px; border: 2px solid #dee2e6; border-radius: 8px;")
        
        activate_btn = ModernButton(translator.translate("activate"))
        activate_btn.clicked.connect(self.activate_license)
        
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(activate_btn)
        activation_layout.addLayout(key_layout)
        
        instructions = QLabel(f"""
        <h3>{translator.translate('how_to_get_license_key')}:</h3>
        <ol>
            <li>{translator.translate('copy_hardware_id_above')}</li>
            <li>{translator.translate('contact_developer_via')}:</li>
            <ul>
                <li>📱 {translator.translate('whatsapp')}: +201061007999</li>
                <li>📧 {translator.translate('email')}: ahmed.tharwat19@gmail.com</li>
            </ul>
            <li>{translator.translate('send_hardware_id_and_choose_plan')}</li>
            <li>{translator.translate('receive_license_within_24_hours')}</li>
        </ol>
        """)
        instructions.setStyleSheet("font-size: 13px; color: #555;")
        instructions.setWordWrap(True)
        activation_layout.addWidget(instructions)
        
        activation_layout.addStretch()
        tabs.addTab(activation_tab, translator.translate("activate_license"))
        
        pricing_tab = QWidget()
        pricing_layout = QVBoxLayout(pricing_tab)
        
        pricing_title = QLabel("💼 " + translator.translate("subscription_prices"))
        pricing_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-bottom: 15px;")
        pricing_layout.addWidget(pricing_title)
        
        plans_grid = QGridLayout()
        plans_grid.setSpacing(15)
        
        plans = [
            ("monthly", translator.translate("monthly_price"), "30 " + translator.translate("days"), "#17a2b8"),
            ("quarterly", translator.translate("quarterly_price"), "90 " + translator.translate("days"), "#28a745"),
            ("half_yearly", translator.translate("half_yearly_price"), "180 " + translator.translate("days"), "#ffc107"),
            ("yearly", translator.translate("yearly_price"), "365 " + translator.translate("days"), "#dc3545"),
        ]
        
        for i, (plan, price, duration, color) in enumerate(plans):
            card = CardWidget()
            card.setStyleSheet(f"""
                CardWidget {{
                    background-color: white;
                    border-radius: 12px;
                    border: 2px solid {color};
                }}
            """)
            
            plan_name = QLabel(translator.translate(plan))
            plan_name.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
            plan_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            plan_price = QLabel(price)
            plan_price.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
            plan_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            plan_duration = QLabel(duration)
            plan_duration.setStyleSheet("font-size: 14px; color: #666;")
            plan_duration.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            card.layout.addWidget(plan_name)
            card.layout.addWidget(plan_price)
            card.layout.addWidget(plan_duration)
            
            plans_grid.addWidget(card, i // 2, i % 2)
        
        pricing_layout.addLayout(plans_grid)
        
        contact_btn = ModernButton("📞 " + translator.translate("contact_support"))
        contact_btn.clicked.connect(self.contact_support)
        pricing_layout.addWidget(contact_btn)
        
        pricing_layout.addStretch()
        tabs.addTab(pricing_tab, translator.translate("subscription_prices"))
        
        layout.addWidget(tabs)
        
        close_btn = ModernButton(translator.translate("close"))
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def load_license_info(self):
        """تحميل معلومات الترخيص"""
        info = license_manager.get_license_info()
        
        if info["activated"] and not info["expired"]:
            status_text = f"✅ {translator.translate('active')} - {info['days_remaining']} {translator.translate('days_remaining')}"
            self.status_label.setStyleSheet("""
                font-size: 16px; 
                padding: 10px; 
                border-radius: 8px;
                background: #d4edda;
                color: #155724;
            """)
        elif info["expired"]:
            status_text = f"⛔ {translator.translate('expired')}"
            self.status_label.setStyleSheet("""
                font-size: 16px; 
                padding: 10px; 
                border-radius: 8px;
                background: #f8d7da;
                color: #721c24;
            """)
        else:
            status_text = f"🎁 {translator.translate('trial')} - {info['days_remaining']} {translator.translate('days_remaining')}"
            self.status_label.setStyleSheet("""
                font-size: 16px; 
                padding: 10px; 
                border-radius: 8px;
                background: #fff3cd;
                color: #856404;
            """)
        
        self.status_label.setText(status_text)
    
    def activate_license(self):
        """تفعيل الترخيص"""
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, translator.translate("warning"), translator.translate("enter_license"))
            return
        
        success, message = license_manager.activate_license(key)
        if success:
            QMessageBox.information(self, translator.translate("success"), message)
            self.load_license_info()
        else:
            QMessageBox.critical(self, translator.translate("error"), message)
    
    def contact_support(self):
        """التواصل مع الدعم"""
        import webbrowser
        webbrowser.open(f"https://wa.me/{PHONE}")

# ================= MAIN APPLICATION =================
class WhatsAppSenderPro(QMainWindow):
    """التطبيق الرئيسي المتكامل"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        # الحصول على حجم الشاشة وضبط النافذة
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # ضبط حجم النافذة (85% من الشاشة)
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        self.setMinimumSize(1200, 700)
        self.resize(window_width, window_height)
        
        # توسيط النافذة
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.move(x, y)
        
        # المتغيرات الرئيسية
        self.contacts = []
        self.image_path = None
        self.driver = None
        self.is_sending = False
        self.current_index = 0
        self.successful_count = 0
        self.failed_count = 0
        
        # الإعدادات
        self.settings = QSettings("WhatsAppSenderPro", "Settings")
        self.load_app_settings()
        
        # إعداد الواجهة
        self.setup_ui()
        self.apply_professional_theme()
        
        # التحقق من الترخيص
        self.check_license()
        
        # بدء المراقبة
        self.start_monitoring()
        
        # إعداد System Tray
        self.setup_system_tray()
        
        logger.info(f"{APP_NAME} v{VERSION} started successfully")

    def get_language_flag(self, code):
        """الحصول على علم اللغة"""
        flags = {"ar": "🇸🇦", "en": "🇬🇧", "fr": "🇫🇷", "es": "🇪🇸"}
        return flags.get(code, "🌐")   

    def setup_system_tray(self):
        """إعداد System Tray مع أيقونة مخصصة"""
        # إنشاء System Tray
        self.tray_icon = QSystemTrayIcon(self)
        
        # محاولة تحميل الأيقونة المخصصة
        icon_paths = [
            "icon.ico",
            "icon.png",
            "logo.ico",
            str(APP_DIR / "icon.ico"),
            str(APP_DIR / "icon.png"),
            str(APP_DIR / "logo.ico"),
        ]
        
        icon_loaded = False
        for path in icon_paths:
            if os.path.exists(path):
                try:
                    self.tray_icon.setIcon(QIcon(path))
                    self.setWindowIcon(QIcon(path))
                    icon_loaded = True
                    break
                except:
                    continue
        
        # إذا لم توجد أيقونة، استخدم أيقونة افتراضية
        if not icon_loaded:
            # إنشاء أيقونة بسيطة برمجياً
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # خلفية خضراء (لون واتساب)
            painter.setBrush(QColor(37, 211, 102))
            painter.drawRoundedRect(0, 0, 64, 64, 15, 15)
            
            # رسم حرف W
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(QFont("Arial", 32, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "W")
            
            painter.end()
            
            self.tray_icon.setIcon(QIcon(pixmap))
            self.setWindowIcon(QIcon(pixmap))
    
        # إنشاء قائمة System Tray
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction(translator.translate("show_window"))
        show_action.triggered.connect(self.show_normal)
        
        tray_menu.addSeparator()
        
        send_action = tray_menu.addAction(translator.translate("start_sending"))
        send_action.triggered.connect(self.start_sending)
        
        stop_action = tray_menu.addAction(translator.translate("stop_sending"))
        stop_action.triggered.connect(self.stop_sending)
        
        tray_menu.addSeparator()
        
        settings_action = tray_menu.addAction(translator.translate("settings"))
        settings_action.triggered.connect(self.show_settings)
        
        license_action = tray_menu.addAction(translator.translate("license"))
        license_action.triggered.connect(self.show_license)
        
        # إضافة خيار المطور
        developer_action = tray_menu.addAction("👨‍💻 " + translator.translate("developer_access"))
        developer_action.triggered.connect(self.show_developer_panel)

        
        language_menu = tray_menu.addMenu("🌍 " + translator.translate("language"))
    
        languages = translator.get_available_languages()
        for code, name in languages.items():
            action = QAction(f"{self.get_language_flag(code)} {name}")
            action.triggered.connect(lambda checked, c=code: self.change_language(c))
            language_menu.addAction(action)

        
        tray_menu.addSeparator()
        
        exit_action = tray_menu.addAction(translator.translate("exit"))
        exit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # ربط إشارة النقر المزدوج
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    # أضف دالة change_language:
    def change_language(self, lang_code):
        """تغيير اللغة"""
        reply = QMessageBox.question(
            self,
            translator.translate("confirm"),
            translator.translate("restart_required"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            translator.set_language(lang_code)
            QMessageBox.information(
                self,
                translator.translate("info"),
                translator.translate("language_changed") + "\n" + translator.translate("restart_required")
            )


    def on_tray_icon_activated(self, reason):
        """عند التفاعل مع أيقونة System Tray"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isHidden():
                self.show_normal()
            elif self.isMinimized():
                self.showNormal()

    def show_normal(self):
        """إظهار النافذة بشكل طبيعي"""
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    def show_developer_panel(self):
        """عرض لوحة تحكم المطور"""
        # التحقق من كلمة المرور
        dialog = DeveloperLockDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # إذا كانت كلمة المرور صحيحة، فتح لوحة المطور
            developer_dialog = DeveloperLicenseGenerator(self)
            developer_dialog.exec()
    
    def load_app_settings(self):
        """تحميل إعدادات التطبيق"""
        self.text_color = self.settings.value("text_color", (255, 215, 0))
        self.text_size = int(self.settings.value("text_size", 50))
        
        # استخدام .toBool() أو التحقق المباشر
        self.add_frame = self.settings.value("add_frame", True, type=bool)
        self.extract_names = self.settings.value("extract_names", True, type=bool)
        
        self.delay_minutes = int(self.settings.value("delay_minutes", 0))
        self.delay_seconds = int(self.settings.value("delay_seconds", 20))

        # أضف دالة show_language_dialog:
    def show_language_dialog(self):
        """عرض حوار اختيار اللغة"""
        dialog = LanguageSelectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            translator.set_language(dialog.selected_language)
            QMessageBox.information(
                self,
                translator.translate("info"),
                translator.translate("language_changed") + "\n" + translator.translate("restart_required")
            )


    def save_app_settings(self):
        """حفظ إعدادات التطبيق"""
        self.settings.setValue("text_color", self.text_color)
        self.settings.setValue("text_size", self.text_size)
        self.settings.setValue("add_frame", self.add_frame)
        self.settings.setValue("extract_names", self.extract_names)
        self.settings.setValue("delay_minutes", self.delay_minutes)
        self.settings.setValue("delay_seconds", self.delay_seconds)
    
    def setup_ui(self):
        """إعداد واجهة المستخدم الرئيسية"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # الشريط الجانبي
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # المحتوى الرئيسي
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # شريط العنوان
        header = self.create_header()
        content_layout.addWidget(header)
        
        # منطقة المحتوى مع Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # إضافة الأقسام
        self.setup_dashboard_cards()
        self.setup_message_section()
        self.setup_contacts_section()
        self.setup_settings_section()
        self.setup_control_section()
        
        # إخفاء جميع الأقسام عدا Dashboard
        self.settings_section.setVisible(False)
        
        # إضافة متغيرات لتتبع الأقسام
        self.current_section = "dashboard"

        scroll.setWidget(content_widget)
        content_layout.addWidget(scroll)
        
        # شريط الحالة السفلي
        footer = self.create_footer()
        content_layout.addWidget(footer)
        
        main_layout.addWidget(content_container, stretch=1)
        
        # Side Pane للسجلات
        self.side_pane = SidePane()
        main_layout.addWidget(self.side_pane)
    
    def create_sidebar(self):
        """إنشاء الشريط الجانبي للتنقل"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #075E54, stop:1 #128C7E);
                border-right: 1px solid #128C7E;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        # شعار التطبيق مع صورة
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setSpacing(10)
        
        # أيقونة التطبيق
        icon_label = QLabel("📱")  # يمكن استبدالها بصورة
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        logo_layout.addWidget(icon_label)
        
        # اسم التطبيق
        app_name_label = QLabel(APP_NAME)
        app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        logo_layout.addWidget(app_name_label)
        
        logo_layout.addWidget(QLabel(f"v{VERSION}"))
        
        logo_widget.setStyleSheet("""
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
        """)
        layout.addWidget(logo_widget)
        
        # أزرار التنقل
        nav_buttons = [
            ("🏠", translator.translate("dashboard"), self.show_dashboard),
            ("✉️", translator.translate("messages"), self.show_messages),
            ("👥", translator.translate("contacts"), self.show_contacts),
            ("📊", translator.translate("statistics"), self.show_statistics),
            ("⚙️", translator.translate("settings"), self.show_settings),
            ("🔐", translator.translate("license"), self.show_license),
             ("🌍", translator.translate("select_language"), self.show_language_dialog),  # إضافة زر اللغة
            ("👨‍💻", translator.translate("developer_access"), self.show_developer_panel),  # إضافة زر المطور
        ]
        
        for icon, text, callback in nav_buttons:
            btn = QPushButton(f"{icon} {text}")
            btn.setMinimumHeight(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding-left: 15px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.2);
                }
                QPushButton:pressed {
                    background: rgba(255,255,255,0.3);
                }
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # معلومات الترخيص
        self.license_widget = QLabel()
        self.license_widget.setStyleSheet("""
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
        """)
        self.license_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_license_widget()
        layout.addWidget(self.license_widget)
        
        return sidebar
    
    def create_header(self):
        """إنشاء شريط العنوان العلوي"""
        header = QFrame()
        header.setMaximumHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # عنوان الصفحة
        self.page_title = QLabel(translator.translate("dashboard"))
        self.page_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
        # حالة واتساب
        self.whatsapp_status = QLabel("⚪ " + translator.translate("disconnected"))
        self.whatsapp_status.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #666;
            padding: 8px 15px;
            background: #f8f9fa;
            border-radius: 20px;
        """)
        layout.addWidget(self.whatsapp_status)
        
        # زر فتح واتساب
        open_btn = ModernButton("🌐 " + translator.translate("open_whatsapp"))
        open_btn.setMaximumWidth(150)
        open_btn.clicked.connect(self.open_whatsapp)
        layout.addWidget(open_btn)
        
        return header
    
    def create_footer(self):
        """إنشاء شريط الحالة السفلي"""
        footer = QFrame()
        footer.setMaximumHeight(50)
        footer.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # معلومات النسخة
        version_label = QLabel(f"v{VERSION} | {translator.translate('build')}: {BUILD_NUMBER}")
        version_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(version_label)
        
        layout.addStretch()
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #25D366, stop:1 #128C7E);
                border-radius: 3px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return footer
    
    def setup_dashboard_cards(self):
        """إعداد بطاقات لوحة التحكم"""
        cards_widget = QWidget()
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setSpacing(15)
        
        # بطاقات الإحصائيات
        self.stat_cards = {}
        stats = [
            ("sent_today", "0", "📤", "#25D366"),
            ("success_rate", "0%", "✅", "#28a745"),
            ("pending_count", "0", "⏳", "#ffc107"),
            ("failed_count", "0", "❌", "#dc3545"),
        ]
        
        for key, value, icon, color in stats:
            card = self.create_stat_card(translator.translate(key), value, icon, color)
            self.stat_cards[key] = card
            cards_layout.addWidget(card)
        
        self.content_layout.addWidget(cards_widget)
    
    def create_stat_card(self, title, value, icon, color):
        """إنشاء بطاقة إحصائية"""
        card = CardWidget()
        card.setStyleSheet(f"""
            CardWidget {{
                background: white;
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = card.layout
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #666;")
        layout.addWidget(title_label)
        
        return card
    
    def setup_message_section(self):
        """إعداد قسم الرسائل"""
        section = CardWidget(translator.translate("messages"))
        
        # محرر الرسالة
        self.message_editor = QTextEdit()
        self.message_editor.setPlaceholderText(
            f"{translator.translate('message_template')}...\n"
            f"{translator.translate('name_variable')}\n"
            f"{translator.translate('phone_variable')}\n"
            f"{translator.translate('date_variable')}\n"
            f"{translator.translate('number_variable')}"
        )
        self.message_editor.setMaximumHeight(150)
        self.message_editor.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        section.layout.addWidget(self.message_editor)
        
        # إعدادات الصورة
        img_group = QGroupBox(translator.translate("image_settings"))
        img_layout = QVBoxLayout(img_group)
        
        # اختيار الصورة
        img_select_layout = QHBoxLayout()
        self.img_path_label = QLabel(translator.translate("no_image_selected"))
        self.img_path_label.setStyleSheet("color: #666; padding: 10px; background: #f8f9fa; border-radius: 6px;")
        
        select_img_btn = ModernButton("📁 " + translator.translate("select_image"))
        select_img_btn.clicked.connect(self.select_image)
        
        clear_img_btn = QPushButton("🗑️")
        clear_img_btn.setFixedWidth(50)
        clear_img_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
            }
        """)
        clear_img_btn.clicked.connect(self.clear_image)
        
        img_select_layout.addWidget(self.img_path_label, stretch=1)
        img_select_layout.addWidget(select_img_btn)
        img_select_layout.addWidget(clear_img_btn)
        img_layout.addLayout(img_select_layout)
        
        # خيارات النص على الصورة
        self.add_text_to_img = QCheckBox(translator.translate("add_text_to_image"))
        self.add_text_to_img.setChecked(True)
        img_layout.addWidget(self.add_text_to_img)
        
        # إعدادات النص
        text_settings = QHBoxLayout()
        
        # حجم الخط
        size_layout = QVBoxLayout()
        size_label = QLabel(translator.translate("text_size"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(20, 100)
        self.font_size_spin.setValue(self.text_size)
        self.font_size_spin.valueChanged.connect(self.update_text_size)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.font_size_spin)
        text_settings.addLayout(size_layout)
        
        # لون الخط
        color_layout = QVBoxLayout()
        color_label = QLabel(translator.translate("text_color"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(50, 30)
        self.update_color_button()
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_btn)
        text_settings.addLayout(color_layout)
        
        # إطار
        self.frame_check = QCheckBox(translator.translate("frame"))
        self.frame_check.setChecked(self.add_frame)
        text_settings.addWidget(self.frame_check)
        
        img_layout.addLayout(text_settings)
        section.layout.addWidget(img_group)
        
        self.content_layout.addWidget(section)
    
    def setup_contacts_section(self):
        """إعداد قسم جهات الاتصال"""
        section = CardWidget(translator.translate("contacts"))
        
        # أزرار التحكم
        controls = QHBoxLayout()
        
        load_btn = ModernButton("📂 " + translator.translate("load_contacts"))
        load_btn.clicked.connect(self.load_contacts)
        controls.addWidget(load_btn)
        
        self.contacts_count_label = QLabel("0 " + translator.translate("contacts"))
        self.contacts_count_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #25D366;")
        controls.addWidget(self.contacts_count_label)
        
        controls.addStretch()
        
        view_btn = QPushButton("👁️ " + translator.translate("view"))
        view_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
            }
        """)
        view_btn.clicked.connect(self.view_contacts)
        controls.addWidget(view_btn)
        
        section.layout.addLayout(controls)
        
        # جدول المعاينة
        self.contacts_preview = QTableWidget()
        self.contacts_preview.setColumnCount(3)
        self.contacts_preview.setHorizontalHeaderLabels([
            translator.translate("number"),
            translator.translate("contact"),
            translator.translate("phone")
        ])
        self.contacts_preview.setMaximumHeight(200)
        self.contacts_preview.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 8px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #dee2e6;
            }
        """)
        section.layout.addWidget(self.contacts_preview)
        
        self.content_layout.addWidget(section)
    
    def setup_settings_section(self):
        """إعداد قسم الإعدادات"""
        section = CardWidget(translator.translate("settings"))
        section.setVisible(False)
        self.settings_section = section
        
        # إعدادات التأخير
        delay_group = QGroupBox(translator.translate("delay_settings"))
        delay_layout = QHBoxLayout(delay_group)
        
        # تأخير البدء
        start_delay_layout = QVBoxLayout()
        start_delay_label = QLabel(translator.translate("delay_minutes"))
        self.start_delay_spin = QSpinBox()
        self.start_delay_spin.setRange(0, 120)
        self.start_delay_spin.setValue(self.delay_minutes)
        start_delay_layout.addWidget(start_delay_label)
        start_delay_layout.addWidget(self.start_delay_spin)
        delay_layout.addLayout(start_delay_layout)
        
        # تأخير بين الرسائل
        msg_delay_layout = QVBoxLayout()
        msg_delay_label = QLabel(translator.translate("delay_seconds"))
        self.msg_delay_spin = QSpinBox()
        self.msg_delay_spin.setRange(5, 300)
        self.msg_delay_spin.setValue(self.delay_seconds)
        msg_delay_layout.addWidget(msg_delay_label)
        msg_delay_layout.addWidget(self.msg_delay_spin)
        delay_layout.addLayout(msg_delay_layout)
        
        # تأخير عشوائي
        self.random_delay = QCheckBox(translator.translate("random_delay"))
        self.random_delay.setChecked(True)
        delay_layout.addWidget(self.random_delay)
        
        section.layout.addWidget(delay_group)
        
        # خيارات الإرسال
        options_group = QGroupBox(translator.translate("sending_settings"))
        options_layout = QVBoxLayout(options_group)
        
        self.extract_names_check = QCheckBox(translator.translate("extract_names"))
        self.extract_names_check.setChecked(self.extract_names)
        options_layout.addWidget(self.extract_names_check)
        
        self.send_image_check = QCheckBox(translator.translate("send_image"))
        self.send_image_check.setChecked(True)
        options_layout.addWidget(self.send_image_check)
        
        self.send_message_check = QCheckBox(translator.translate("send_message"))
        self.send_message_check.setChecked(True)
        options_layout.addWidget(self.send_message_check)
        
        section.layout.addWidget(options_group)
        
        self.content_layout.addWidget(section)
    
    def setup_control_section(self):
        """إعداد قسم التحكم"""
        section = CardWidget(translator.translate("send"))
        
        # أزرار التحكم الرئيسية
        controls = QHBoxLayout()
        
        self.start_btn = ModernButton("🚀 " + translator.translate("start"))
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #28a745, stop:1 #20c997);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #20c997, stop:1 #28a745);
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """)
        self.start_btn.clicked.connect(self.start_sending)
        controls.addWidget(self.start_btn, stretch=2)
        
        self.stop_btn = ModernButton("⛔ " + translator.translate("stop"))
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #dc3545, stop:1 #c82333);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #c82333, stop:1 #dc3545);
            }
        """)
        self.stop_btn.clicked.connect(self.stop_sending)
        controls.addWidget(self.stop_btn, stretch=1)
        
        section.layout.addLayout(controls)
        
        # معلومات التقدم
        self.progress_info = QLabel()
        self.progress_info.setStyleSheet("""
            font-size: 14px;
            color: #666;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        """)
        self.progress_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        section.layout.addWidget(self.progress_info)
        
        self.content_layout.addWidget(section)
    
    def apply_professional_theme(self):
        """تطبيق السمة الاحترافية"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #333;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #25D366;
            }
            QSpinBox {
                padding: 8px;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background: white;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #dee2e6;
            }
            QCheckBox::indicator:checked {
                background: #25D366;
                border-color: #25D366;
            }
        """)
    
    # ===== دوال التنقل =====
    def show_dashboard(self):
        self.page_title.setText(translator.translate("dashboard"))
        self.settings_section.setVisible(False)
        self.current_section = "dashboard"

    def show_messages(self):
        self.page_title.setText(translator.translate("messages"))
        self.settings_section.setVisible(False)
        self.current_section = "messages"

    def show_contacts(self):
        self.page_title.setText(translator.translate("contacts"))
        self.settings_section.setVisible(False)
        self.current_section = "contacts"

    def show_statistics(self):
        self.page_title.setText(translator.translate("statistics"))
        self.settings_section.setVisible(False)
        self.current_section = "statistics"

    def show_settings(self):
        self.page_title.setText(translator.translate("settings"))
        self.settings_section.setVisible(True)
        self.current_section = "settings"
    
    def show_license(self):
        dialog = LicenseDialog(self)
        dialog.exec()
        self.update_license_widget()
    
    # ===== دوال الترخيص =====
    def check_license(self):
        """التحقق من حالة الترخيص"""
        if license_manager.is_expired():
            QMessageBox.warning(
                self,
                translator.translate("trial_expired"),
                translator.translate("contact_developer")
            )
            self.show_license()
    
    def update_license_widget(self):
        """تحديث واجهة الترخيص"""
        info = license_manager.get_license_info()
        
        if info["activated"]:
            text = f"✅ {translator.translate('active')}\n{info['days_remaining']} {translator.translate('days')}"
            color = "#d4edda"
        elif info["expired"]:
            text = f"⛔ {translator.translate('expired')}"
            color = "#f8d7da"
        else:
            text = f"🎁 {translator.translate('trial')}\n{info['days_remaining']} {translator.translate('days')}"
            color = "#fff3cd"
        
        self.license_widget.setText(text)
        self.license_widget.setStyleSheet(f"""
            background: {color};
            color: #333;
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
        """)
    
    # ===== دوال الوظائف =====
    def log(self, message, level="INFO"):
        """إضافة سجل"""
        self.side_pane.add_log(message, level)
        logger.log(getattr(logging, level, logging.INFO), message)
    
    def update_color_button(self):
        """تحديث لون زر اللون"""
        r, g, b = self.text_color
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({r}, {g}, {b});
                border: 2px solid #dee2e6;
                border-radius: 6px;
            }}
        """)
    
    def choose_color(self):
        """اختيار لون مخصص"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = (color.red(), color.green(), color.blue())
            self.update_color_button()
            self.save_app_settings()
    
    def update_text_size(self, size):
        """تحديث حجم الخط"""
        self.text_size = size
        self.save_app_settings()
    
    def select_image(self):
        """اختيار صورة"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, translator.translate("select_image"), str(APP_DIR),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.image_path = file_path
            self.img_path_label.setText(f"📷 {Path(file_path).name}")
            self.img_path_label.setStyleSheet("""
                color: #155724;
                padding: 10px;
                background: #d4edda;
                border-radius: 6px;
                font-weight: bold;
            """)
            self.log(f"Image selected: {file_path}")
    
    def clear_image(self):
        """مسح الصورة"""
        self.image_path = None
        self.img_path_label.setText(translator.translate("no_image_selected"))
        self.img_path_label.setStyleSheet("color: #666; padding: 10px; background: #f8f9fa; border-radius: 6px;")
        self.log("Image cleared")
    
    def load_contacts(self):
        """تحميل جهات الاتصال"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, translator.translate("load_contacts"), str(APP_DIR),
            "Excel (*.xlsx);;CSV (*.csv);;JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            ext = Path(file_path).suffix.lower()
            
            if ext == '.xlsx':
                df = pd.read_excel(file_path)
            elif ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                raise ValueError("Unsupported file format")
            
            # معالجة البيانات
            self.contacts = []
            for _, row in df.iterrows():
                contact = {}
                
                # البحث عن رقم الهاتف
                for col in df.columns:
                    col_lower = str(col).lower()
                    if any(word in col_lower for word in ['phone', 'mobile', 'tel', 'هاتف', 'رقم', 'جوال']):
                        phone = str(row[col]).strip()
                        phone = ''.join(filter(str.isdigit, phone))
                        if len(phone) >= 8:
                            contact['phone'] = phone
                            break
                
                # البحث عن الاسم
                for col in df.columns:
                    col_lower = str(col).lower()
                    if any(word in col_lower for word in ['name', 'اسم', 'contact', 'جهة']):
                        contact['name'] = str(row[col])
                        break
                
                if 'phone' in contact:
                    self.contacts.append(contact)
            
            # تحديث الواجهة
            self.contacts_count_label.setText(f"{len(self.contacts)} {translator.translate('contacts')}")
            
            # تحديث جدول المعاينة
            self.contacts_preview.setRowCount(min(len(self.contacts), 10))
            for i, contact in enumerate(self.contacts[:10]):
                self.contacts_preview.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.contacts_preview.setItem(i, 1, QTableWidgetItem(contact.get('name', '')))
                self.contacts_preview.setItem(i, 2, QTableWidgetItem(contact.get('phone', '')))
            
            self.log(f"Loaded {len(self.contacts)} contacts", "SUCCESS")
            
            if len(self.contacts) == 0:
                QMessageBox.warning(self, translator.translate("warning"), "No valid phone numbers found")
            
        except Exception as e:
            self.log(f"Error loading contacts: {e}", "ERROR")
            QMessageBox.critical(self, translator.translate("error"), str(e))
    
    def view_contacts(self):
        """عرض جميع جهات الاتصال"""
        if not self.contacts:
            QMessageBox.information(self, translator.translate("info"), "No contacts loaded")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{translator.translate('contacts')} ({len(self.contacts)})")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels([
            translator.translate("number"),
            translator.translate("contact"),
            translator.translate("phone")
        ])
        table.setRowCount(len(self.contacts))
        
        for i, contact in enumerate(self.contacts):
            table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            table.setItem(i, 1, QTableWidgetItem(contact.get('name', '')))
            table.setItem(i, 2, QTableWidgetItem(contact.get('phone', '')))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        
        close_btn = ModernButton(translator.translate("close"))
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def open_whatsapp(self):
        """فتح واتساب"""
        self.log("Opening WhatsApp Web...")
        threading.Thread(target=self._open_whatsapp_thread, daemon=True).start()
    
    def _open_whatsapp_thread(self):
        """Thread لفتح واتساب"""
        try:
            # ✅ استخدام webdriver-manager بدلاً من chromedriver-autoinstaller
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            # ✅ أو يمكننا استخدام chromedriver-autoinstaller مع معالجة الأخطاء
            try:
                import chromedriver_autoinstaller
                chromedriver_autoinstaller.install()
                use_autoinstaller = True
            except ImportError:
                self.log("chromedriver-autoinstaller not installed, using webdriver-manager", "WARNING")
                use_autoinstaller = False
            
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--log-level=3")
            
            # إضافة حفظ الجلسة لتجنب مسح QR كل مرة
            options.add_argument("--user-data-dir=" + str(APP_DIR / "chrome_profile"))
            options.add_argument("--profile-directory=Default")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # إزالة علامة التشغيل الآلي
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # استخدام webdriver-manager لتثبيت وإدارة ChromeDriver
            try:
                if use_autoinstaller:
                    # باستخدام chromedriver-autoinstaller
                    self.driver = webdriver.Chrome(options=options)
                else:
                    # باستخدام webdriver-manager
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                self.log(f"Error creating Chrome driver: {e}", "ERROR")
                # محاولة الطريقة الافتراضية
                self.driver = webdriver.Chrome(options=options)
            
            # إخفاء علامات التشغيل الآلي
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except:
                pass
            
            # ترجمة الرسائل
            self.log(translator.translate("whatsapp_opened"), "SUCCESS")
            self.update_whatsapp_status("connecting")
            
            # فتح واتساب ويب
            self.driver.get("https://web.whatsapp.com")
            
            # الانتظار والتحقق من الاتصال
            try:
                # انتظار حتى 60 ثانية للاتصال
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.webdriver.common.by import By
                
                # محاولة العثور على علامات الاتصال
                try:
                    # انتظار ظهور قائمة الدردشات (دليل على الاتصال)
                    wait = WebDriverWait(self.driver, 60)
                    
                    # محاولة عدة طرق للكشف عن حالة الاتصال
                    connected_indicators = [
                        '[data-testid="chat-list"]',
                        'div[aria-label="قائمة الدردشات"]',
                        'div[aria-label="Chat list"]',
                        'div[data-asset-chat-background-light]',
                        'div[title="بحث"]',
                        'div[title="Search"]',
                    ]
                    
                    connected = False
                    for indicator in connected_indicators:
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                            if element.is_displayed():
                                connected = True
                                break
                        except:
                            continue
                    
                    if connected:
                        self.update_whatsapp_status("connected")
                        self.log(translator.translate("connected") + "!", "SUCCESS")
                    else:
                        # إذا لم تظهر قائمة الدردشات، ابحث عن رمز QR
                        try:
                            qr_element = wait.until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'canvas[aria-label="Scan me!"]')
                            ))
                            if qr_element:
                                self.update_whatsapp_status("qr_scan")
                                self.log(translator.translate("qr_scan") + "...", "INFO")
                                
                                # انتظار حتى يختفي رمز QR (تم المسح)
                                WebDriverWait(self.driver, 180).until(
                                    EC.invisibility_of_element_located(
                                        (By.CSS_SELECTOR, 'canvas[aria-label="Scan me!"]')
                                    )
                                )
                                self.update_whatsapp_status("connected")
                                self.log("QR code scanned successfully! Connected.", "SUCCESS")
                        except:
                            self.update_whatsapp_status("disconnected")
                            self.log("Could not detect WhatsApp Web state", "WARNING")
                            
                except Exception as e:
                    self.update_whatsapp_status("disconnected")
                    self.log(f"Connection error: {e}", "ERROR")
                    
            except Exception as e:
                self.update_whatsapp_status("disconnected")
                self.log(f"Connection error: {e}", "ERROR")
                
        except Exception as e:
            error_msg = f"{translator.translate('whatsapp_error')}: {str(e)}"
            self.log(error_msg, "ERROR")
            self.update_whatsapp_status("disconnected")
            
            # عرض رسالة ترحيبية
            QMessageBox.critical(
                self,
                translator.translate("error"),
                f"{translator.translate('whatsapp_error')}:\n\n{str(e)}\n\n"
                f"يرجى:\n"
                f"1. تثبيت Google Chrome\n"
                f"2. تحديث Chrome إلى آخر إصدار\n"
                f"3. إغلاق جميع نوافذ Chrome وإعادة المحاولة"
            )
    
    def update_whatsapp_status(self, status, custom_message=None):
        """تحديث حالة واتساب"""
        status_map = {
            "connected": ("🟢 ", "#d4edda", "#155724"),
            "disconnected": ("⚪ ", "#f8f9fa", "#666"),
            "connecting": ("🟡 ", "#fff3cd", "#856404"),
            "qr_scan": ("🔴 ", "#f8d7da", "#721c24"),
        }
        
        prefix, bg_color, text_color = status_map.get(status, status_map["disconnected"])
        
        if custom_message:
            text = custom_message
        else:
            text = translator.translate(status)
        
        full_text = f"{prefix}{text}"
        self.whatsapp_status.setText(full_text)
        self.whatsapp_status.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {text_color};
            padding: 8px 15px;
            background: {bg_color};
            border-radius: 20px;
        """)
    
    def start_sending(self):
        """بدء الإرسال"""
        if not self.contacts:
            QMessageBox.warning(self, translator.translate("warning"), "Please load contacts first")
            return
        
        if license_manager.is_expired():
            QMessageBox.warning(self, translator.translate("trial_expired"), translator.translate("contact_developer"))
            self.show_license()
            return
        
        # تأكيد البدء
        reply = QMessageBox.question(
            self,
            translator.translate("confirm"),
            f"{translator.translate('are_you_sure')}\n\n"
            f"Total contacts: {len(self.contacts)}\n"
            f"Message: {'Yes' if self.message_editor.toPlainText().strip() else 'No'}\n"
            f"Image: {'Yes' if self.image_path else 'No'}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # تحديث الحالة
        self.is_sending = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.contacts))
        self.progress_bar.setValue(0)
        
        # حفظ الإعدادات
        self.save_app_settings()
        
        # بدء الإرسال في Thread منفصل
        self.sending_thread = SendingThread(self)
        self.sending_thread.progress_signal.connect(self.update_progress)
        self.sending_thread.log_signal.connect(self.log)
        self.sending_thread.finished_signal.connect(self.sending_finished)
        self.sending_thread.start()
    
    def stop_sending(self):
        """إيقاف الإرسال"""
        self.is_sending = False
        if hasattr(self, 'sending_thread'):
            self.sending_thread.stop()
        self.log("Sending stopped by user", "WARNING")
        self.sending_finished()
    
    def update_progress(self, current, total, success, failed):
        """تحديث شريط التقدم"""
        self.progress_bar.setValue(current)
        self.progress_info.setText(
            f"Progress: {current}/{total} | ✅ Success: {success} | ❌ Failed: {failed}"
        )
        
        # تحديث البطاقات
        self.stat_cards["sent_today"].layout.itemAt(1).widget().setText(str(success + failed))
        success_rate = (success / (success + failed) * 100) if (success + failed) > 0 else 0
        self.stat_cards["success_rate"].layout.itemAt(1).widget().setText(f"{success_rate:.1f}%")
        self.stat_cards["pending_count"].layout.itemAt(1).widget().setText(str(total - current))
        self.stat_cards["failed_count"].layout.itemAt(1).widget().setText(str(failed))
        
        # تحديث الفهرس الحالي
        self.current_index = current
    
    def sending_finished(self):
        """انتهاء الإرسال"""
        self.is_sending = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.log("Sending process completed", "SUCCESS")
        QMessageBox.information(self, translator.translate("completed"), "Sending process completed!")
    
    def start_monitoring(self):
        """بدء مراقبة الحالة"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_status)
        self.status_timer.start(5000)
    
    def check_status(self):
        """التحقق من الحالة"""
        self.update_license_widget()
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        if self.is_sending:
            reply = QMessageBox.question(
                self,
                translator.translate("confirm"),
                "Sending is in progress. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        # اخفاء بدلاً من إغلاق
        if self.tray_icon.isVisible():
            reply = QMessageBox.question(
                self,
                translator.translate("hide_application"),
                translator.translate("hide_application_question"),
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.hide()
                self.tray_icon.showMessage(
                    "WhatsApp Sender Pro",
                    translator.translate("app_running_in_background"),
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # تنظيف الموارد
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.save_app_settings()
        self.tray_icon.hide()
        event.accept()

# ================= SENDING THREAD =================
class SendingThread(QThread):
    """Thread للإرسال"""
    progress_signal = pyqtSignal(int, int, int, int)
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.running = True
    
    def stop(self):
        self.running = False
    
    def run(self):
        """تنفيذ الإرسال الحقيقي"""
        try:
            if not self.parent.driver:
                self.log_signal.emit("WhatsApp not connected. Please open WhatsApp first.", "ERROR")
                self.finished_signal.emit()
                return
            
            total = len(self.parent.contacts)
            success = 0
            failed = 0
            
            for i, contact in enumerate(self.parent.contacts):
                if not self.running:
                    break
                
                try:
                    phone = contact.get('phone', '')
                    name = contact.get('name', '')
                    
                    self.log_signal.emit(f"📤 Sending to {name} ({phone})", "INFO")
                    
                    # إرسال حقيقي إلى WhatsApp
                    result = self.send_to_whatsapp(phone, name)
                    
                    if result:
                        success += 1
                        self.log_signal.emit(f"✅ Successfully sent to {name}", "SUCCESS")
                    else:
                        failed += 1
                        self.log_signal.emit(f"❌ Failed to send to {name}", "ERROR")
                    
                except Exception as e:
                    failed += 1
                    self.log_signal.emit(f"❌ Error sending to {contact.get('name', '')}: {str(e)}", "ERROR")
                
                self.progress_signal.emit(i + 1, total, success, failed)
                
                # تأخير بين الرسائل
                if i < total - 1 and self.running:
                    delay = random.randint(15, 30)
                    self.log_signal.emit(f"⏳ Waiting {delay} seconds...", "INFO")
                    time.sleep(delay)
            
            self.log_signal.emit(f"✅ Sending completed! Success: {success}, Failed: {failed}", "SUCCESS")
            self.finished_signal.emit()
            
        except Exception as e:
            self.log_signal.emit(f"❌ Error in sending thread: {e}", "ERROR")
            self.finished_signal.emit()

    def send_to_whatsapp(self, phone, name):
        """إرسال رسالة حقيقية إلى واتساب"""
        try:
            driver = self.parent.driver
            
            # التحقق من اتصال WhatsApp
            if not driver or "whatsapp" not in driver.current_url:
                self.log_signal.emit("WhatsApp not connected. Reopening...", "WARNING")
                return False
            
            # استيراد المكتبات المطلوبة
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            import pyperclip
            import random
            import time
            import os
            from PIL import Image, ImageDraw, ImageFont
            import win32clipboard
            from io import BytesIO
            
            # فتح دردشة جديدة
            chat_url = f"https://web.whatsapp.com/send?phone={phone}"
            driver.get(chat_url)
            time.sleep(5)  # انتظار تحميل الشات
            
            # التحقق من وجود المستخدم
            try:
                # البحث عن مربع الرسائل
                input_box = None
                selectors = [
                    "//div[@contenteditable='true'][@data-tab='10']",
                    "//div[@contenteditable='true'][@data-tab='9']",
                    "//footer//div[@contenteditable='true']",
                ]
                
                for selector in selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                input_box = element
                                break
                        if input_box:
                            break
                    except:
                        continue
                
                if not input_box:
                    self.log_signal.emit(f"Could not find message input box for {phone}", "WARNING")
                    return False
                    
            except Exception as e:
                self.log_signal.emit(f"Error finding chat: {e}", "WARNING")
                return False
            
            # === إرسال الرسالة النصية ===
            if self.parent.send_message_check.isChecked():
                try:
                    message_text = self.parent.message_editor.toPlainText()
                    
                    if message_text.strip():
                        # استبدال المتغيرات
                        message_text = message_text.replace("{name}", name if name else "عزيزي/عزيزتي")
                        message_text = message_text.replace("{phone}", phone)
                        message_text = message_text.replace("{date}", datetime.now().strftime("%Y-%m-%d"))
                        message_text = message_text.replace("{number}", str(self.parent.current_index + 1))
                        
                        # نسخ النص إلى الحافظة وإرساله
                        pyperclip.copy(message_text)
                        input_box.click()
                        time.sleep(0.5)
                        input_box.send_keys(Keys.CONTROL, "v")
                        time.sleep(1)
                        input_box.send_keys(Keys.ENTER)
                        self.log_signal.emit(f"📨 تم إرسال الرسالة النصية", "INFO")
                        
                except Exception as e:
                    self.log_signal.emit(f"⚠️ تعذر إرسال الرسالة النصية: {e}", "WARNING")
            
            # === إرسال الصورة ===
            if self.parent.image_path and os.path.exists(self.parent.image_path) and self.parent.send_image_check.isChecked():
                time.sleep(2)  # انتظار قليل بين الرسالة والصورة
                
                # إضافة النص على الصورة إذا كان مفعلاً
                image_to_send = self.parent.image_path
                if self.parent.add_text_to_img.isChecked() and name:
                    try:
                        self.log_signal.emit(f"📝 جاري كتابة الاسم '{name}' على الصورة...", "INFO")
                        
                        # استدعاء دالة إضافة النص على الصورة
                        temp_image = self.add_text_to_image_func(self.parent.image_path, name)
                        if temp_image and os.path.exists(temp_image):
                            image_to_send = temp_image
                            self.log_signal.emit(f"✅ تم إضافة النص على الصورة", "INFO")
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ تعذر إضافة النص على الصورة: {e}", "WARNING")
                        image_to_send = self.parent.image_path
                
                # إرسال الصورة
                try:
                    self.log_signal.emit(f"🖼️ جاري إرسال الصورة: {os.path.basename(image_to_send)}", "INFO")
                    
                    # فتح الصورة وتحويلها إلى BMP للنسخ
                    img = Image.open(image_to_send)
                    output = BytesIO()
                    img.convert("RGB").save(output, "BMP")
                    data = output.getvalue()[14:]
                    output.close()

                    # نسخ الصورة إلى الحافظة
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()

                    # لصق الصورة في مربع الرسائل
                    input_box.click()
                    time.sleep(0.5)
                    input_box.send_keys(Keys.CONTROL, "v")
                    time.sleep(3)  # انتظار معاينة الصورة
                    
                    # إرسال الصورة
                    send_selectors = [
                        "//*[@id='app']/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/span/div/div/span",
                        "//span[@data-icon='send']",
                        "//span[@data-icon='send']",
                        "//span[@data-testid='send']",
                        "//button[@aria-label='Send']",
                        "//div[@role='button'][@title='Send']"
                    ]
                    
                    send_button = None
                    for selector in send_selectors:
                        try:
                            element = driver.find_element(By.XPATH, selector)
                            if element.is_displayed():
                                send_button = element
                                break
                        except:
                            continue
                    
                    if send_button:
                        send_button.click()
                        time.sleep(2)
                        self.log_signal.emit(f"✅ تم إرسال الصورة", "INFO")
                    else:
                        # محاولة استخدام ENTER
                        input_box.send_keys(Keys.ENTER)
                        time.sleep(2)
                        self.log_signal.emit(f"✅ تم إرسال الصورة باستخدام ENTER", "INFO")
                    
                    # تنظيف الصورة المؤقتة
                    if image_to_send != self.parent.image_path and os.path.exists(image_to_send):
                        try:
                            os.remove(image_to_send)
                        except:
                            pass
                        
                except Exception as e:
                    self.log_signal.emit(f"❌ فشل إرسال الصورة: {e}", "ERROR")
            
            self.parent.current_index += 1
            return True
            
        except Exception as e:
            self.log_signal.emit(f"❌ خطأ في الإرسال: {e}", "ERROR")
            return False

    def add_text_to_image_func(self, image_path, recipient_name):
        """إضافة نص إلى الصورة مع دعم اللغة العربية وإطار دائري للاسم"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import os
            import time
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            # إنشاء مسار مؤقت للصورة
            timestamp = int(time.time())
            output_path = os.path.join(APP_DIR, f"temp_image_with_text_{timestamp}.jpg")
            
            # لون وحجم النص
            text_color = self.parent.text_color if hasattr(self.parent, 'text_color') else (255, 215, 0)
            text_size = self.parent.text_size if hasattr(self.parent, 'text_size') else 50
            
            # فتح الصورة
            img = Image.open(image_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            
            # تحضير النص للعرض
            display_text = f"إلى: {recipient_name}" if recipient_name else "إلى: عزيزي/عزيزتي"
            
            # فحص إذا كان النص عربي
            def is_arabic_text(text):
                return any('\u0600' <= char <= '\u06FF' for char in text) if text else False
            
            # تشكيل النص العربي إذا كان مدعوماً
            if is_arabic_text(display_text):
                try:
                    reshaped_text = arabic_reshaper.reshape(display_text)
                    display_text = get_display(reshaped_text)
                except:
                    pass
            
            # تحديد الخط المناسب
            font = None
            font_paths = [
                "C:\\Windows\\Fonts\\tahoma.ttf",
                "C:\\Windows\\Fonts\\arial.ttf",
                "C:\\Windows\\Fonts\\segoeui.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf"
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, text_size)
                        break
                    except:
                        continue
            
            if not font:
                font = ImageFont.load_default()
            
            # حساب حجم النص
            text_bbox = draw.textbbox((0, 0), display_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            img_width, img_height = img.size
            
            # ضبط حجم الخط ليناسب الصورة
            max_width = img_width * 0.8
            while text_width > max_width and text_size > 20:
                text_size = int(text_size * 0.9)
                try:
                    font = ImageFont.truetype(font.path if hasattr(font, 'path') else font_paths[0], text_size)
                    text_bbox = draw.textbbox((0, 0), display_text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                except:
                    break
            
            # حساب موضع النص - أعلى الوسط
            x = (img_width - text_width) // 2
            y = 30
            
            # إضافة إطار دائري للنص
            if hasattr(self.parent, 'frame_check') and self.parent.frame_check.isChecked():
                frame_padding = 20
                frame_radius = 15
                
                # إنشاء طبقة شفافية مؤقتة
                temp_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
                frame_draw = ImageDraw.Draw(temp_layer)
                
                # حساب موضع الإطار
                frame_box = [
                    x - frame_padding,
                    y - frame_padding,
                    x + text_width + frame_padding,
                    y + text_height + frame_padding
                ]
                
                # رسم إطار فقط (بدون تعبئة) بنفس لون النص
                frame_draw.rounded_rectangle(
                    frame_box,
                    radius=frame_radius,
                    outline=text_color + (255,),  # نفس لون النص مع شفافية كاملة
                    width=3  # سمك الإطار
                )
                
                # دمج الإطار مع الصورة الأصلية
                img = Image.alpha_composite(img, temp_layer)
                draw = ImageDraw.Draw(img)
            
            # إضافة ظل للنص
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), display_text, 
                    font=font, fill=(0, 0, 0, 100))
            
            # إضافة النص الرئيسي
            draw.text((x, y), display_text, font=font, fill=text_color)
            
            # حفظ الصورة
            img = img.convert("RGB")
            img.save(output_path, quality=95)
            
            return output_path
            
        except Exception as e:
            self.log_signal.emit(f"❌ فشل إضافة النص إلى الصورة: {e}", "ERROR")
            return image_path

# ================= MAIN ENTRY =================
def main():
    """النقطة الرئيسية للدخول"""
    # إنشاء تطبيق Qt
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    
        # إصلاح مشكلة الأيقونة في Windows
    try:
        import ctypes
        myappid = APP_NAME + VERSION
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception as e:
        logger.error(f"Failed to set app ID: {e}")

    # تحميل الإعدادات
    settings = QSettings("WhatsAppSenderPro", "Settings")
    
    # التحقق من أول تشغيل
    first_run = not settings.value("language_selected", False)
    
    if first_run:
        # عرض حوار اختيار اللغة
        lang_dialog = LanguageSelectionDialog()
        if lang_dialog.exec() == QDialog.DialogCode.Accepted:
            settings.setValue("language_selected", True)
            settings.setValue("language", lang_dialog.selected_language)
        else:
            sys.exit(0)
    
    # إنشاء النافذة الرئيسية
    window = WhatsAppSenderPro()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()