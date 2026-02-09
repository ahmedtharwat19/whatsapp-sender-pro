"""
متحقق التحديثات - للتحقق من وجود تحديثات جديدة
"""

import requests
import json
import logging
import os
import zipfile
import shutil
from pathlib import Path
from packaging import version

class UpdateChecker:
    def __init__(self, update_url=None, current_version="1.0.0"):
        """تهيئة متحقق التحديثات"""
        self.logger = logging.getLogger(__name__)
        self.update_url = update_url or "https://api.yourdomain.com/updates"
        self.current_version = current_version
        self.update_info = None
        
    def check_for_updates(self):
        """التحقق من وجود تحديثات"""
        try:
            response = requests.get(
                f"{self.update_url}/check",
                params={"version": self.current_version},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("update_available", False):
                    self.update_info = data
                    self.logger.info(f"يوجد تحديث جديد: {data.get('latest_version')}")
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من التحديثات: {e}")
            return False
    
    def get_update_info(self):
        """الحصول على معلومات التحديث"""
        return self.update_info
    
    def download_update(self, download_path="updates"):
        """تنزيل التحديث"""
        try:
            if not self.update_info:
                self.logger.error("لا توجد معلومات تحديث")
                return False
            
            download_url = self.update_info.get("download_url")
            if not download_url:
                self.logger.error("لا يوجد رابط تنزيل")
                return False
            
            # إنشاء مجلد التحميل
            download_dir = Path(download_path)
            download_dir.mkdir(exist_ok=True)
            
            # اسم الملف
            file_name = download_url.split("/")[-1]
            file_path = download_dir / file_name
            
            # تنزيل الملف
            self.logger.info(f"جاري تنزيل التحديث: {file_name}")
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"تم تنزيل التحديث: {file_path}")
            
            # فك الضغط إذا كان ملف zip
            if file_name.endswith('.zip'):
                self.extract_update(file_path, download_dir)
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تنزيل التحديث: {e}")
            return False
    
    def extract_update(self, zip_path, extract_to):
        """فك ضغط التحديث"""
        try:
            self.logger.info(f"جاري فك ضغط التحديث: {zip_path}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            self.logger.info(f"تم فك الضغط في: {extract_to}")
            
            # حذف ملف zip بعد فك الضغط
            os.remove(zip_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في فك ضغط التحديث: {e}")
            return False
    
    def install_update(self, update_path="updates"):
        """تثبيت التحديث"""
        try:
            update_dir = Path(update_path)
            if not update_dir.exists():
                self.logger.error("مجلد التحديث غير موجود")
                return False
            
            # البحث عن ملف التثبيت
            install_script = None
            for file in update_dir.rglob("*"):
                if file.name == "install.py" or file.name == "update.bat":
                    install_script = file
                    break
            
            if install_script:
                # تشغيل سكريبت التثبيت
                self.logger.info(f"جاري تشغيل سكريبت التثبيت: {install_script}")
                
                if install_script.suffix == '.py':
                    os.system(f"python {install_script}")
                elif install_script.suffix == '.bat':
                    os.system(str(install_script))
            else:
                # نسخ الملفات يدوياً
                self.copy_update_files(update_dir, Path("."))
            
            self.logger.info("تم تثبيت التحديث بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تثبيت التحديث: {e}")
            return False
    
    def copy_update_files(self, source_dir, dest_dir):
        """نسخ ملفات التحديث"""
        try:
            for item in source_dir.rglob("*"):
                if item.is_file():
                    # حساب المسار النسبي
                    relative_path = item.relative_to(source_dir)
                    dest_path = dest_dir / relative_path
                    
                    # إنشاء المجلدات إذا لزم الأمر
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # نسخ الملف
                    shutil.copy2(item, dest_path)
                    self.logger.debug(f"تم نسخ: {relative_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في نسخ ملفات التحديث: {e}")
            return False
    
    def backup_current_version(self, backup_dir="backups"):
        """إنشاء نسخة احتياطية من الإصدار الحالي"""
        try:
            backup_path = Path(backup_dir) / f"backup_v{self.current_version}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # نسخ الملفات المهمة
            important_files = [
                "main.py",
                "app/",
                "config/app_config.yaml",
                "config/firebase_config.json",
                "config/encryption_keys.json",
                "license.key"
            ]
            
            for item in important_files:
                source = Path(item)
                if source.exists():
                    if source.is_file():
                        shutil.copy2(source, backup_path / source.name)
                    elif source.is_dir():
                        dest = backup_path / source.name
                        shutil.copytree(source, dest, dirs_exist_ok=True)
            
            self.logger.info(f"تم إنشاء نسخة احتياطية في: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def rollback_update(self, backup_dir="backups"):
        """التراجع عن التحديث"""
        try:
            backup_path = Path(backup_dir) / f"backup_v{self.current_version}"
            if not backup_path.exists():
                self.logger.error("النسخة الاحتياطية غير موجودة")
                return False
            
            # استعادة الملفات
            for item in backup_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(backup_path)
                    dest_path = Path(".") / relative_path
                    
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
            
            self.logger.info("تم التراجع عن التحديث بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في التراجع عن التحديث: {e}")
            return False