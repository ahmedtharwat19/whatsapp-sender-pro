"""
أدوات مساعدة متنوعة
"""

import os
import sys
import json
import csv
import random
import string
import hashlib
import uuid
import platform
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class Helpers:
    """فئة الأدوات المساعدة"""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """إنشاء سلسلة عشوائية"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def generate_uuid() -> str:
        """إنشاء UUID فريد"""
        return str(uuid.uuid4())
    
    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """الحصول على تجزئة الملف"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"خطأ في حساب تجزئة الملف: {e}")
            return ""
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """تنسيق حجم الملف"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """التحقق من صحة رقم الهاتف"""
        # تنظيف الرقم
        phone = ''.join(filter(str.isdigit, phone))
        
        # التحقق من الطول
        if len(phone) < 8 or len(phone) > 15:
            return False
        
        # يمكن إضافة المزيد من التحقق حسب البلد
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """التحقق من صحة البريد الإلكتروني"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """تطهير اسم الملف"""
        # استبدال الأحغير غير الآمنة
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # إزالة المسافات الزائدة
        filename = ' '.join(filename.split())
        
        # تقصير إذا كان طويلاً جداً
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250 - len(ext)] + ext
        
        return filename
    
    @staticmethod
    def create_backup(file_path: str, backup_dir: str = "backups") -> Optional[str]:
        """إنشاء نسخة احتياطية من الملف"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # إنشاء مجلد النسخ الاحتياطية
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            
            # اسم النسخة الاحتياطية مع التاريخ
            file_name = Path(file_path).name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_name}.{timestamp}.backup"
            backup_file = backup_path / backup_name
            
            # نسخ الملف
            import shutil
            shutil.copy2(file_path, backup_file)
            
            logger.info(f"تم إنشاء نسخة احتياطية: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return None
    
    @staticmethod
    def load_config_file(config_path: str) -> Dict[str, Any]:
        """تحميل ملف التكوين"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"ملف التكوين غير موجود: {config_path}")
                return {}
            
            if config_file.suffix == '.json':
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif config_file.suffix in ['.yaml', '.yml']:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.error(f"تنسيق ملف غير مدعوم: {config_file.suffix}")
                return {}
                
        except Exception as e:
            logger.error(f"خطأ في تحميل ملف التكوين: {e}")
            return {}
    
    @staticmethod
    def save_config_file(config_path: str, data: Dict[str, Any]) -> bool:
        """حفظ ملف التكوين"""
        try:
            config_file = Path(config_path)
            
            # إنشاء المجلد إذا لم يكن موجوداً
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            if config_file.suffix == '.json':
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif config_file.suffix in ['.yaml', '.yml']:
                import yaml
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True)
            else:
                logger.error(f"تنسيق ملف غير مدعوم: {config_file.suffix}")
                return False
            
            logger.info(f"تم حفظ ملف التكوين: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حفظ ملف التكوين: {e}")
            return False
    
    @staticmethod
    def convert_image_format(input_path: str, output_path: str, format: str = 'PNG') -> bool:
        """تحويل صيغة الصورة"""
        try:
            img = Image.open(input_path)
            
            # تحويل RGBA إذا كان PNG
            if format.upper() == 'PNG' and img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            img.save(output_path, format=format)
            logger.info(f"تم تحويل الصورة إلى {format}: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحويل صيغة الصورة: {e}")
            return False
    
    @staticmethod
    def compress_image(input_path: str, output_path: str, quality: int = 85) -> bool:
        """ضغط الصورة"""
        try:
            img = Image.open(input_path)
            
            # حفظ مع ضغط
            img.save(output_path, quality=quality, optimize=True)
            
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"تم ضغط الصورة: {compression_ratio:.1f}% تخفيض")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في ضغط الصورة: {e}")
            return False
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """الحصول على معلومات النظام"""
        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0],
            'node': platform.node(),
            'cpu_count': os.cpu_count(),
            'memory_total': None,
            'memory_available': None
        }
        
        # إضافة معلومات الذاكرة إذا كانت متاحة
        try:
            import psutil
            memory = psutil.virtual_memory()
            info['memory_total'] = Helpers.format_file_size(memory.total)
            info['memory_available'] = Helpers.format_file_size(memory.available)
        except:
            pass
        
        return info
    
    @staticmethod
    def calculate_time_remaining(start_time: datetime, current: int, total: int) -> str:
        """حساب الوقت المتبقي"""
        if current == 0:
            return "تقدير الوقت..."
        
        elapsed = datetime.now() - start_time
        time_per_item = elapsed.total_seconds() / current
        remaining_items = total - current
        remaining_seconds = time_per_item * remaining_items
        
        if remaining_seconds < 60:
            return f"{int(remaining_seconds)} ثانية"
        elif remaining_seconds < 3600:
            minutes = int(remaining_seconds / 60)
            seconds = int(remaining_seconds % 60)
            return f"{minutes}:{seconds:02d} دقيقة"
        else:
            hours = int(remaining_seconds / 3600)
            minutes = int((remaining_seconds % 3600) / 60)
            return f"{hours}:{minutes:02d} ساعة"
    
    @staticmethod
    def create_progress_bar(progress: float, width: int = 50) -> str:
        """إنشاء شريط تقدم نصي"""
        filled = int(width * progress)
        empty = width - filled
        bar = '█' * filled + '░' * empty
        percentage = int(progress * 100)
        return f"[{bar}] {percentage}%"
    
    @staticmethod
    def retry_operation(operation, max_retries=3, delay=1, backoff=2):
        """إعادة محاولة العملية في حالة الفشل"""
        import time
        
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                logger.warning(f"المحاولة {attempt + 1} فشلت: {e}")
                
                if attempt == max_retries - 1:
                    raise
                
                sleep_time = delay * (backoff ** attempt)
                time.sleep(sleep_time)
    
    @staticmethod
    def validate_csv_file(file_path: str) -> bool:
        """التحقق من صحة ملف CSV"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # قراءة أول سطرين للتحقق
                reader = csv.reader(f)
                headers = next(reader, None)
                
                if not headers:
                    return False
                
                # التحقق من وجود الأعمدة المطلوبة
                headers_lower = [h.lower() for h in headers]
                if 'phone' not in headers_lower and 'number' not in headers_lower:
                    return False
                
                # قراءة سطر إضافي للتحقق
                try:
                    next(reader)
                except StopIteration:
                    pass  # الملف يحتوي فقط على رؤوس
                
            return True
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من ملف CSV: {e}")
            return False
    
    @staticmethod
    def validate_excel_file(file_path: str) -> bool:
        """التحقق من صحة ملف Excel"""
        try:
            df = pd.read_excel(file_path, nrows=1)  # قراءة أول سطر فقط
            columns_lower = [str(col).lower() for col in df.columns]
            
            # التحقق من وجود عمود الهاتف
            if any('phone' in col or 'number' in col for col in columns_lower):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من ملف Excel: {e}")
            return False