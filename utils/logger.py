"""
أداة التسجيل (Logging) المتقدمة
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from pathlib import Path
import colorlog

class CustomLogger:
    """فئة تسجيل مخصصة"""
    
    def __init__(self, name, log_dir="logs", level=logging.INFO):
        """تهيئة المسجل"""
        self.name = name
        self.log_dir = Path(log_dir)
        self.level = level
        
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        self.log_dir.mkdir(exist_ok=True)
        
        # إعداد المسجل
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # منع نشر السجلات إلى المسجلين الأساسيين
        self.logger.propagate = False
        
        # إعداد الصيغ
        self.setup_formatters()
        
        # إعداد المعالجات
        self.setup_handlers()
    
    def setup_formatters(self):
        """إعداد صيغ التسجيل"""
        # صيغة مفصلة للملف
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # صيغة مبسطة للوحدة
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # صيغة ملونة للوحدة
        self.colored_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    
    def setup_handlers(self):
        """إعداد معالجات التسجيل"""
        # محو أي معالجات موجودة
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 1. معالج وحدة التحكم (ملون)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(self.colored_formatter)
        self.logger.addHandler(console_handler)
        
        # 2. معالج ملف عام (يدور يومياً)
        general_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_dir / 'app.log',
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        general_handler.setLevel(self.level)
        general_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(general_handler)
        
        # 3. معالج ملف الأخطاء (يدور أسبوعياً)
        error_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.log_dir / 'error.log',
            when='W0',
            interval=1,
            backupCount=12,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(error_handler)
        
        # 4. معالج ملف الأنشطة
        activity_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'activity.log',
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        activity_handler.setLevel(logging.INFO)
        activity_handler.setFormatter(self.simple_formatter)
        self.logger.addHandler(activity_handler)
    
    def get_logger(self):
        """الحصول على كائن التسجيل"""
        return self.logger
    
    def log_activity(self, user, action, details=None, level='info'):
        """تسجيل نشاط المستخدم"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'action': action,
            'details': details or {}
        }
        
        log_message = f"ACTIVITY - User: {user}, Action: {action}"
        if details:
            log_message += f", Details: {json.dumps(details, ensure_ascii=False)}"
        
        if level == 'info':
            self.logger.info(log_message)
        elif level == 'warning':
            self.logger.warning(log_message)
        elif level == 'error':
            self.logger.error(log_message)
        
        # حفظ في ملف أنشاط منفصل
        activity_log = self.log_dir / 'user_activities.json'
        try:
            activities = []
            if activity_log.exists():
                with open(activity_log, 'r', encoding='utf-8') as f:
                    activities = json.load(f)
            
            activities.append(log_data)
            
            with open(activity_log, 'w', encoding='utf-8') as f:
                json.dump(activities, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save activity log: {e}")
    
    def log_performance(self, operation, duration_ms, details=None):
        """تسجيل أداء العملية"""
        log_message = f"PERFORMANCE - Operation: {operation}, Duration: {duration_ms}ms"
        if details:
            log_message += f", Details: {details}"
        
        self.logger.info(log_message)
        
        # حفظ في ملف أداء
        perf_log = self.log_dir / 'performance.json'
        try:
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'duration_ms': duration_ms,
                'details': details or {}
            }
            
            perf_entries = []
            if perf_log.exists():
                with open(perf_log, 'r', encoding='utf-8') as f:
                    perf_entries = json.load(f)
            
            perf_entries.append(performance_data)
            
            with open(perf_log, 'w', encoding='utf-8') as f:
                json.dump(perf_entries, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save performance log: {e}")
    
    def cleanup_old_logs(self, days_to_keep=30):
        """تنظيف السجلات القديمة"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob('*.log*'):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file.name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")


def setup_logger(name='whatsapp_sender_pro', log_dir='logs', level=logging.INFO):
    """إعداد المسجل الرئيسي"""
    return CustomLogger(name, log_dir, level).get_logger()


# مسجل افتراضي
default_logger = setup_logger()

# دوال اختصار
def debug(msg, *args, **kwargs):
    default_logger.debug(msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    default_logger.info(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    default_logger.warning(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    default_logger.error(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
    default_logger.critical(msg, *args, **kwargs)

def exception(msg, *args, **kwargs):
    default_logger.exception(msg, *args, **kwargs)