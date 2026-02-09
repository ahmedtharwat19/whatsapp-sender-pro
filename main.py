#!/usr/bin/env python3
"""
WhatsApp Sender Pro - Professional Edition
الإصدار المحسّن والمقسّم لسهولة الصيانة والتطوير
"""

import sys
import os
import traceback
from pathlib import Path

# الحصول على المسار الحالي
current_dir = Path(__file__).parent
project_dir = current_dir.parent

print(f"📁 المشروع: {project_dir}")
print(f"📁 المصدر: {current_dir}")

def install_requirements():
    """تثبيت المتطلبات تلقائياً"""
    print("📦 تثبيت المتطلبات...")
    
    try:
        import subprocess
        import importlib
        
        # قائمة المكتبات المطلوبة
        requirements = [
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
        
        for package in requirements:
            package_name = package.split("==")[0]
            try:
                if package_name == "PyQt6":
                    __import__("PyQt6.QtWidgets")
                elif package_name == "python-bidi":
                    __import__("bidi")
                elif package_name == "deep-translator":
                    __import__("deep_translator")
                else:
                    __import__(package_name)
                print(f"✅ {package_name} مثبت بالفعل")
            except ImportError:
                print(f"📦 جاري تثبيت {package}...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", package,
                        "--quiet", "--disable-pip-version-check"
                    ])
                    print(f"✅ تم تثبيت {package}")
                except Exception as e:
                    print(f"❌ فشل تثبيت {package}: {e}")
        
        print("🎉 تم تثبيت جميع المتطلبات بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تثبيت المتطلبات: {e}")
        return False

def check_directories():
    """التحقق من وجود المجلدات المطلوبة"""
    directories = [
        project_dir / "data" / "config",
        project_dir / "data" / "logs", 
        project_dir / "data" / "fonts",
        project_dir / "data" / "temp",
        project_dir / "assets" / "icons"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"📁 {directory.name} - جاهز")

def main():
    """الدالة الرئيسية"""
    try:
        # التحقق من المجلدات
        check_directories()
        
        # تثبيت المتطلبات
        if not install_requirements():
            print("❌ فشل في تثبيت المتطلبات")
            input("اضغط Enter للخروج...")
            return
        
        print("🚀 بدء تشغيل WhatsApp Sender Pro...")
        
        # استيراد PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QIcon
        
        # استيراد وحداتنا
        sys.path.insert(0, str(current_dir))
        
        from src.ui.main_window import WhatsAppSenderPro
        from src.utils.logger import setup_logger
        
        # إعداد التطبيق
        app = QApplication(sys.argv)
        app.setApplicationName("WhatsApp Sender Pro")
        app.setApplicationVersion("4.4.0")
        
        # إعداد السجلات
        logger = setup_logger()
        logger.info("بدأ تشغيل التطبيق")
        
        # إنشاء النافذة الرئيسية
        window = WhatsAppSenderPro()
        
        # تحميل الأيقونة إذا وجدت
        icon_paths = [
            project_dir / "icon.ico",
            project_dir / "icon.png",
            project_dir / "assets" / "icons" / "icon.ico",
            project_dir / "assets" / "icons" / "icon.png"
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                app.setWindowIcon(QIcon(str(icon_path)))
                window.setWindowIcon(QIcon(str(icon_path)))
                print(f"✅ تم تحميل الأيقونة: {icon_path}")
                break
        
        window.show()
        
        print("✅ التطبيق جاهز للاستخدام!")
        
        # تشغيل التطبيق
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        traceback.print_exc()
        input("اضغط Enter للخروج...")

if __name__ == "__main__":
    main()