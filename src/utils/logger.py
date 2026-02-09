"""
نظام السجلات المتقدم
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler

class AppLogger:
    """مدير سجلات التطبيق"""
    
    def __init__(self, name: str = "WhatsAppSenderPro"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # إعداد تنسيق السجلات
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # معالج الملفات الدوارة
        self._setup_file_handler(formatter)
        
        # معالج وحدة التحكم
        self._setup_console_handler(formatter)
        
        # منع انتشار السجلات
        self.logger.propagate = False
    
    def _setup_file_handler(self, formatter: logging.Formatter):
        """إعداد معالج الملفات"""
        try:
            # إنشاء مجلد السجلات
            logs_dir = Path(__file__).parent.parent.parent / "data" / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # إنشاء ملف السجل اليومي
            log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            
            # معالج الملفات الدوارة (10 ملفات × 5MB لكل)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=10,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"❌ خطأ في إعداد سجلات الملفات: {e}")
    
    def _setup_console_handler(self, formatter: logging.Formatter):
        """إعداد معالج وحدة التحكم"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """سجل تصحيح"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """سجل معلومات"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """سجل تحذير"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """سجل خطأ"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """سجل حرج"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, exc_info=True, **kwargs):
        """سجل استثناء"""
        self.logger.exception(message, *args, exc_info=exc_info, **kwargs)
    
    def log_sending(self, contact_name: str, phone: str, status: str, details: str = ""):
        """سجل عملية إرسال"""
        self.info(f"📤 الإرسال | {contact_name} ({phone}) | {status} | {details}")
    
    def log_license(self, action: str, status: str, details: str = ""):
        """سجل نشاط الترخيص"""
        self.info(f"🔐 الترخيص | {action} | {status} | {details}")
    
    def log_system(self, action: str, status: str, details: str = ""):
        """سجل نشاط النظام"""
        self.info(f"⚙️ النظام | {action} | {status} | {details}")
    
    def get_log_files(self) -> list:
        """الحصول على قائمة ملفات السجلات"""
        logs_dir = Path(__file__).parent.parent.parent / "data" / "logs"
        if logs_dir.exists():
            return sorted(logs_dir.glob("*.log"), reverse=True)
        return []
    
    def cleanup_old_logs(self, max_files: int = 30):
        """تنظيف السجلات القديمة"""
        try:
            log_files = self.get_log_files()
            if len(log_files) > max_files:
                for old_log in log_files[max_files:]:
                    old_log.unlink()
                    self.info(f"🗑️ تم حذف سجل قديم: {old_log.name}")
        except Exception as e:
            self.error(f"خطأ في تنظيف السجلات القديمة: {e}")

def setup_logger(name: str = "WhatsAppSenderPro") -> AppLogger:
    """إعداد وإرجاع مدير السجلات"""
    return AppLogger(name)

# إنشاء نسخة عامة من السجل
logger = setup_logger()