#!/usr/bin/env python3
"""
WhatsApp Sender Pro - Professional Edition
الإصدار المحسّن والمقسّم لسهولة الصيانة والتطوير
"""

import sys
import os
import traceback
from pathlib import Path

# الحصول على المسار الحالي وإضافة src إلى PYTHONPATH
current_dir = Path(__file__).parent
src_dir = current_dir  # لأن main.py داخل src

# إضافة المسار إلى PYTHONPATH
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(src_dir.parent))  # إضافة المسار الرئيسي أيضاً

print(f"📁 المسار الحالي: {current_dir}")
print(f"📁 مجلد src: {src_dir}")

# تثبيت المكتبات المطلوبة أولاً
def check_and_install_dependencies():
    """التحقق من المكتبات المطلوبة وتثبيتها"""
    print("📦 التحقق من المكتبات المطلوبة...")
    
    try:
        # أولاً، تثبيت pip إذا لم يكن مثبتاً
        try:
            import pip
        except ImportError:
            print("🔧 تثبيت pip...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        
        # قائمة المكتبات الأساسية
        required_packages = [
            "PyQt6",
            "selenium",
            "webdriver-manager",
            "pandas",
            "Pillow",
            "cryptography",
            "requests",
            "pyperclip",
            "psutil",
            "arabic-reshaper",
            "python-bidi",
            "deep-translator",
            "openpyxl",
            "python-dotenv",
            "PyAutoGUI",
            "chromedriver-autoinstaller==0.6.0"
        ]
        
        # تثبيت المكتبات
        import subprocess
        import importlib
        
        for package in required_packages:
            package_name = package.split("==")[0]
            try:
                # محاولة استيراد المكتبة
                if package_name == "PyQt6":
                    __import__("PyQt6.QtWidgets")
                elif package_name == "python-bidi":
                    __import__("bidi")
                elif package_name == "deep-translator":
                    __import__("deep_translator")
                else:
                    __import__(package_name)
                print(f"✅ {package_name} - مثبت بالفعل")
            except ImportError:
                print(f"📦 تثبيت {package}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
                    print(f"✅ تم تثبيت {package} بنجاح")
                except subprocess.CalledProcessError as e:
                    print(f"❌ فشل تثبيت {package}: {e}")
        
        print("✅ جميع المكتبات مثبتة وجاهزة")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تثبيت المكتبات: {e}")
        print(traceback.format_exc())
        return False

def main():
    """الدالة الرئيسية للتشغيل"""
    # التحقق من المكتبات أولاً
    if not check_and_install_dependencies():
        print("❌ فشل في تثبيت المكتبات المطلوبة")
        input("اضغط Enter للخروج...")
        sys.exit(1)
    
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtCore import QTranslator, QLocale, QLibraryInfo
        from PyQt6.QtGui import QIcon
        
        # استيراد الموديولات باستخدام المسار الصحيح
        # استيراد مباشر من المجلدات الحالية
        from ui.main_window import WhatsAppSenderPro
        from utils.logger import setup_logger
        from config.settings import AppSettings
        
        print("🚀 بدء تشغيل WhatsApp Sender Pro...")
        
        # إعداد التطبيق
        app = QApplication(sys.argv)
        app.setApplicationName("WhatsApp Sender Pro")
        app.setApplicationVersion("4.4.0")
        app.setOrganizationName("Ahmed Tharwat")
        
        # إعداد الترجمة
        translator = QTranslator()
        locale = QLocale.system().name()
        
        # محاولة تحميل ترجمة Qt
        if translator.load(f"qt_{locale}", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
            app.installTranslator(translator)
        
        # تحميل إعدادات التطبيق
        settings = AppSettings()
        
        # إعداد السجلات
        logger = setup_logger()
        logger.info("تشغيل WhatsApp Sender Pro v4.4.0")
        
        # إنشاء النافذة الرئيسية
        window = WhatsAppSenderPro()
        
        # محاولة تحميل الأيقونة
        try:
            # البحث في مسارات مختلفة للأيقونة
            base_dir = current_dir.parent  # المسار الرئيسي للمشروع
            icon_paths = [
                str(base_dir / "assets" / "icons" / "icon.ico"),
                str(base_dir / "assets" / "icons" / "icon.png"),
                str(base_dir / "icon.ico"),
                str(base_dir / "icon.png"),
            ]
            
            for path in icon_paths:
                if Path(path).exists():
                    app.setWindowIcon(QIcon(path))
                    window.setWindowIcon(QIcon(path))
                    print(f"✅ تم تحميل الأيقونة من: {path}")
                    break
        except Exception as e:
            print(f"⚠️ تعذر تحميل الأيقونة: {e}")
        
        window.show()
        
        # تشغيل التطبيق
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        print(traceback.format_exc())
        input("اضغط Enter للخروج...")
        sys.exit(1)

if __name__ == "__main__":
    main()