# app/core/license_validator.py
"""
متحقق الترخيص - للتحقق من صلاحية التراخيص
"""

import hashlib
import json
from datetime import datetime, timedelta
import logging
from cryptography.fernet import Fernet
import base64

class LicenseValidator:
    def __init__(self, secret_key=None):
        """تهيئة متحقق الترخيص"""
        self.logger = logging.getLogger(__name__)
        self.secret_key = secret_key or "your-secret-key-here-change-in-production"
        self.license_data = None
        
    def validate(self, license_key, hwid):
        """التحقق من صلاحية الترخيص"""
        try:
            # فك تشفير مفتاح الترخيص
            license_data = self._decrypt_license(license_key)
            if not license_data:
                return False
            
            # التحقق من HWID
            if license_data.get('hwid') != hwid:
                self.logger.warning("HWID غير مطابق")
                return False
            
            # التحقق من تاريخ الانتهاء
            expiry_date_str = license_data.get('expiry_date')
            if expiry_date_str:
                expiry_date = datetime.fromisoformat(expiry_date_str)
                if datetime.now() > expiry_date:
                    self.logger.warning("الترخيص منتهي الصلاحية")
                    return False
            
            # التحقق من النوع
            license_type = license_data.get('type', 'trial')
            if license_type == 'trial':
                # التحقق من عدد الاستخدامات
                uses = license_data.get('uses', 0)
                max_uses = license_data.get('max_uses', 50)
                if uses >= max_uses:
                    self.logger.warning("تم تجاوز الحد المسموح للنسخة التجريبية")
                    return False
            
            # تحديث عدد الاستخدامات
            license_data['uses'] = license_data.get('uses', 0) + 1
            license_data['last_used'] = datetime.now().isoformat()
            
            self.license_data = license_data
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الترخيص: {e}")
            return False
    
    def _decrypt_license(self, encrypted_key):
        """فك تشفير مفتاح الترخيص"""
        try:
            # تحويل المفتاح السري إلى مفتاح Fernet مناسب
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.secret_key.encode()).digest()
            )
            
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_key.encode())
            
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            self.logger.error(f"خطأ في فك تشفير الترخيص: {e}")
            return None
    
    def generate_license(self, license_type, duration_days, hwid=None, max_uses=None):
        """إنشاء ترخيص جديد"""
        try:
            license_data = {
                'type': license_type,
                'created_date': datetime.now().isoformat(),
                'expiry_date': (datetime.now() + timedelta(days=duration_days)).isoformat(),
                'hwid': hwid,
                'max_uses': max_uses or {
                    'trial': 50,
                    '1_month': 1000,
                    '3_months': 3000,
                    '6_months': 6000,
                    '9_months': 9000,
                    '1_year': 12000
                }.get(license_type, 1000),
                'uses': 0,
                'plan': license_type,
                'status': 'active'
            }
            
            # تشفير بيانات الترخيص
            key = base64.urlsafe_b64encode(
                hashlib.sha256(self.secret_key.encode()).digest()
            )
            
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(json.dumps(license_data).encode())
            
            return encrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء الترخيص: {e}")
            return None
    
    def get_license_info(self):
        """الحصول على معلومات الترخيص"""
        if self.license_data:
            return {
                'type': self.license_data.get('type'),
                'expiry_date': self.license_data.get('expiry_date'),
                'uses': self.license_data.get('uses', 0),
                'max_uses': self.license_data.get('max_uses'),
                'plan': self.license_data.get('plan')
            }
        return None