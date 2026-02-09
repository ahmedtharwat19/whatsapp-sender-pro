"""
نظام الترجمة المتكامل
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

class Language(Enum):
    """اللغات المتاحة"""
    ARABIC = "ar"
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"

class TranslationManager:
    """مدير الترجمة"""
    
    def __init__(self):
        self.current_language = Language.ARABIC
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_all_translations()
    
    def _load_all_translations(self):
        """تحميل جميع الترجمات"""
        # الترجمات المضمنة
        self.translations = {
            "ar": self._get_arabic_translations(),
            "en": self._get_english_translations(),
        }
        
        # محاولة تحميل ملفات خارجية
        self._load_external_translations()
    
    def _load_external_translations(self):
        """تحميل الترجمات من ملفات خارجية"""
        translations_dir = Path(__file__).parent.parent.parent / "data" / "translations"
        
        if translations_dir.exists():
            for lang_file in translations_dir.glob("*.json"):
                lang_code = lang_file.stem
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"⚠️ خطأ في تحميل ترجمة {lang_code}: {e}")
    
    def _get_arabic_translations(self) -> Dict[str, str]:
        """الترجمة العربية"""
        return {
            # مصطلحات عامة
            "app_title": "WhatsApp Sender Pro",
            "welcome": "مرحباً بك",
            "dashboard": "لوحة التحكم",
            "settings": "الإعدادات",
            "contacts": "جهات الاتصال",
            "messages": "الرسائل",
            "send": "إرسال",
            "start": "بدء",
            "stop": "إيقاف",
            "pause": "إيقاف مؤقت",
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
            "close": "إغلاق",
            "exit": "خروج",
            "help": "مساعدة",
            "about": "حول",
            "version": "الإصدار",
            "build": "رقم البناء",
            "developer": "المطور",
            
            # حالة التطبيق
            "ready": "جاهز",
            "sending": "جاري الإرسال",
            "completed": "مكتمل",
            "failed": "فاشل",
            "success": "نجاح",
            "error": "خطأ",
            "warning": "تحذير",
            "info": "معلومات",
            "connected": "متصل",
            "disconnected": "غير متصل",
            "connecting": "جاري الاتصال",
            
            # الترخيص
            "license": "الترخيص",
            "trial": "تجريبي",
            "premium": "مميز",
            "expired": "منتهي",
            "active": "نشط",
            "days_remaining": "أيام متبقية",
            "activate": "تفعيل",
            "activation": "تفعيل",
            "hardware_id": "معرف الجهاز",
            "subscription": "اشتراك",
            "monthly": "شهري",
            "quarterly": "ربع سنوي",
            "half_yearly": "نصف سنوي",
            "yearly": "سنوي",
            "lifetime": "مدى الحياة",
            
            # واتساب
            "whatsapp": "واتساب",
            "open_whatsapp": "فتح واتساب",
            "whatsapp_status": "حالة واتساب",
            "qr_scan": "مسح رمز QR",
            "scan_qr_code": "امسح رمز QR",
            
            # الرسائل
            "message": "رسالة",
            "message_template": "قالب الرسالة",
            "variables": "المتغيرات",
            "name_variable": "{name} - اسم المستلم",
            "phone_variable": "{phone} - رقم الهاتف",
            "date_variable": "{date} - التاريخ",
            "time_variable": "{time} - الوقت",
            "number_variable": "{number} - الرقم التسلسلي",
            
            # الصور
            "image": "صورة",
            "images": "صور",
            "select_image": "اختر صورة",
            "image_settings": "إعدادات الصورة",
            "add_text_to_image": "إضافة نص على الصورة",
            "text_color": "لون النص",
            "text_size": "حجم النص",
            "font": "الخط",
            "frame": "إطار",
            "background": "خلفية",
            "no_image_selected": "لم يتم اختيار صورة",
            
            # جهات الاتصال
            "contact": "جهة اتصال",
            "contacts_list": "قائمة جهات الاتصال",
            "load_contacts": "تحميل جهات الاتصال",
            "import_contacts": "استيراد جهات الاتصال",
            "export_contacts": "تصدير جهات الاتصال",
            "contacts_loaded": "تم تحميل جهات الاتصال",
            "invalid_numbers": "أرقام غير صالحة",
            "valid_numbers": "أرقام صالحة",
            "phone_number": "رقم الهاتف",
            
            # الإعدادات
            "delay_settings": "إعدادات التأخير",
            "delay_between_messages": "تأخير بين الرسائل",
            "start_delay": "تأخير البدء",
            "random_delay": "تأخير عشوائي",
            "sending_settings": "إعدادات الإرسال",
            "extract_names": "استخراج الأسماء",
            "send_image": "إرسال صورة",
            "send_message": "إرسال رسالة",
            "max_errors": "الحد الأقصى للأخطاء",
            "retry_count": "عدد المحاولات",
            
            # السجلات والتقارير
            "logs": "السجلات",
            "reports": "التقارير",
            "activity_log": "سجل النشاط",
            "export_report": "تصدير التقرير",
            "clear_logs": "مسح السجلات",
            "save_logs": "حفظ السجلات",
            
            # المطور
            "developer_access": "دخول المطور",
            "developer_tools": "أدوات المطور",
            "license_generator": "مولد التراخيص",
            "create_license": "إنشاء ترخيص",
            "buyer_name": "اسم المشتري",
            "buyer_email": "بريد المشتري",
            "buyer_phone": "هاتف المشتري",
            
            # إحصائيات
            "statistics": "الإحصائيات",
            "total_sent": "إجمالي المرسل",
            "success_rate": "معدل النجاح",
            "failed_count": "عدد الفاشل",
            "pending_count": "قيد الانتظار",
            "sent_today": "مرسلة اليوم",
            "sent_this_week": "مرسلة هذا الأسبوع",
            "sent_this_month": "مرسلة هذا الشهر",
            
            # أسعار
            "pricing": "الأسعار",
            "price": "السعر",
            "currency_egp": "ج.م",
            "buy_now": "اشتر الآن",
            "contact_developer": "تواصل مع المطور",
            "contact_support": "اتصل بالدعم",
            
            # رسائل النجاح
            "success_message": "تمت العملية بنجاح",
            "operation_completed": "تم إكمال العملية",
            "saved_successfully": "تم الحفظ بنجاح",
            "loaded_successfully": "تم التحميل بنجاح",
            
            # رسائل الخطأ
            "error_message": "حدث خطأ",
            "operation_failed": "فشلت العملية",
            "invalid_input": "إدخال غير صالح",
            "file_not_found": "الملف غير موجود",
            "permission_denied": "تم رفض الإذن",
            "network_error": "خطأ في الشبكة",
            
            # تأكيدات
            "are_you_sure": "هل أنت متأكد؟",
            "confirm_delete": "تأكيد الحذف",
            "confirm_exit": "تأكيد الخروج",
            "confirm_stop": "تأكيد الإيقاف",
            
            # تعليمات
            "instructions": "التعليمات",
            "how_to_use": "كيفية الاستخدام",
            "step_by_step": "خطوة بخطوة",
            "tips": "نصائح",
            
            # تحديثات
            "update": "تحديث",
            "check_for_updates": "التحقق من التحديثات",
            "update_available": "تحديث متاح",
            "up_to_date": "أحدث إصدار",
            
            # النسخ الاحتياطي
            "backup": "نسخ احتياطي",
            "restore": "استعادة",
            "auto_backup": "نسخ احتياطي تلقائي",
            
            # مظهر
            "appearance": "المظهر",
            "theme": "السمة",
            "light": "فاتح",
            "dark": "داكن",
            "auto": "تلقائي",
            "language": "اللغة",
            "font_size": "حجم الخط",
            "small": "صغير",
            "medium": "متوسط",
            "large": "كبير",
            
            # أدوات
            "tools": "الأدوات",
            "utilities": "الأدوات المساعدة",
            "converter": "محول",
            "validator": "مدقق",
            "formatter": "منسق",
        }
    
    def _get_english_translations(self) -> Dict[str, str]:
        """English translations"""
        # This would auto-translate from Arabic or have manual translations
        return {
            "app_title": "WhatsApp Sender Pro",
            "welcome": "Welcome",
            "dashboard": "Dashboard",
            "settings": "Settings",
            "contacts": "Contacts",
            "messages": "Messages",
            "send": "Send",
            "start": "Start",
            "stop": "Stop",
            "pause": "Pause",
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
            "close": "Close",
            "exit": "Exit",
            "help": "Help",
            "about": "About",
            "version": "Version",
            "build": "Build",
            "developer": "Developer",
            "ready": "Ready",
            "sending": "Sending",
            "completed": "Completed",
            "failed": "Failed",
            "success": "Success",
            "error": "Error",
            "warning": "Warning",
            "info": "Info",
            "connected": "Connected",
            "disconnected": "Disconnected",
            "connecting": "Connecting",
        }
    
    def set_language(self, language: Language):
        """تغيير اللغة"""
        self.current_language = language
    
    def get(self, key: str, default: str = None) -> str:
        """الحصول على ترجمة"""
        lang_code = self.current_language.value
        
        if lang_code in self.translations and key in self.translations[lang_code]:
            return self.translations[lang_code][key]
        
        # البحث في اللغة الإنجليزية كبديل
        if "en" in self.translations and key in self.translations["en"]:
            return self.translations["en"][key]
        
        # البحث في العربية كبديل نهائي
        if "ar" in self.translations and key in self.translations["ar"]:
            return self.translations["ar"][key]
        
        return default or key
    
    def translate(self, key: str, **kwargs) -> str:
        """ترجمة نص مع استبدال المتغيرات"""
        text = self.get(key, key)
        
        # استبدال المتغيرات
        for k, v in kwargs.items():
            text = text.replace(f"{{{k}}}", str(v))
        
        return text
    
    def get_available_languages(self) -> Dict[str, Dict[str, str]]:
        """الحصول على اللغات المتاحة"""
        return {
            "ar": {"name": "العربية", "native": "العربية", "flag": "🇸🇦"},
            "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
            "fr": {"name": "French", "native": "Français", "flag": "🇫🇷"},
            "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸"},
        }

# إنشاء نسخة عامة من مدير الترجمة
translator = TranslationManager()