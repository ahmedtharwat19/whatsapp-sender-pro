"""
نظام الترخيص المتقدم مع ميزات أمان محسنة
"""

import json
import hashlib
import base64
import uuid
import platform
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class LicenseManager:
    """مدير الترخيص المتقدم"""
    
    # ثوابت التطبيق
    APP_NAME = "WhatsApp Sender Pro"
    VERSION = "4.4.0"
    DEVELOPER = "Ahmed Tharwat"
    DEVELOPER_EMAIL = "ahmed.tharwat19@gmail.com"
    DEVELOPER_PHONE = "+201061007999"
    
    # فترات الاشتراك (بالأيام)
    SUBSCRIPTION_PERIODS = {
        "trial": 30,
        "monthly": 30,
        "quarterly": 90,
        "half_yearly": 180,
        "yearly": 365,
        "lifetime": 36500  # 100 سنة
    }
    
    # أسعار الاشتراكات
    SUBSCRIPTION_PRICES = {
        "monthly": 500,
        "quarterly": 1200,
        "half_yearly": 2000,
        "yearly": 3800,
        "lifetime": 10000
    }
    
    def __init__(self):
        self.hardware_id = self._generate_hardware_id()
        self.license_file = self._get_license_path()
        self.license_data = self._load_license()
        self.encryption_key = self._generate_encryption_key()
        
    def _generate_hardware_id(self) -> str:
        """إنشاء معرف جهاز فريد"""
        try:
            import psutil
            
            # جمع معلومات النظام
            system_info = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "node": platform.node(),
                "mac_address": self._get_mac_address(),
                "disk_info": self._get_disk_info(),
                "cpu_cores": psutil.cpu_count(logical=False),
                "total_memory": psutil.virtual_memory().total,
                "boot_time": psutil.boot_time(),
            }
            
            # إنشاء هاش فريد
            info_string = json.dumps(system_info, sort_keys=True)
            hwid = hashlib.sha512(info_string.encode()).hexdigest()[:32]
            
            return hwid.upper()
            
        except Exception as e:
            # طريقة احتياطية
            return str(uuid.uuid4()).replace("-", "").upper()[:32]
    
    def _get_mac_address(self) -> str:
        """الحصول على عنوان MAC"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                           for ele in range(0, 8*6, 8)][::-1])
            return mac
        except:
            return "00:00:00:00:00:00"
    
    def _get_disk_info(self) -> str:
        """الحصول على معلومات القرص"""
        try:
            import psutil
            partitions = psutil.disk_partitions()
            if partitions:
                return partitions[0].device
            return "unknown"
        except:
            return "unknown"
    
    def _generate_encryption_key(self) -> bytes:
        """إنشاء مفتاح تشفير قوي"""
        # استخدام HWID كجزء من الملح
        salt = b'whatsapp_pro_salt_v4_' + self.hardware_id.encode()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=1000000,  # زيادة عدد التكرارات للأمان
        )
        
        key = base64.urlsafe_b64encode(
            kdf.derive(b'whatsapp_pro_master_key_2026_secure_v4')
        )
        
        return key
    
    def _get_license_path(self) -> Path:
        """الحصول على مسار ملف الترخيص"""
        config_dir = Path(__file__).parent.parent.parent / "data" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "license.dat"
    
    def _load_license(self) -> Dict[str, Any]:
        """تحميل بيانات الترخيص"""
        default_license = {
            "type": "trial",
            "status": "active",
            "hardware_id": self.hardware_id,
            "plan": "trial",
            "activation_date": None,
            "expiry_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "license_key": None,
            "buyer_info": {},
            "signature": None,
            "metadata": {
                "version": self.VERSION,
                "created_at": datetime.now().isoformat(),
                "last_check": None,
            }
        }
        
        try:
            if self.license_file.exists():
                with open(self.license_file, 'r') as f:
                    encrypted_data = f.read().strip()
                
                if encrypted_data:
                    decrypted = self._decrypt_data(encrypted_data)
                    if decrypted:
                        # دمج الترخيص المحمل مع الافتراضي
                        license_info = {**default_license, **decrypted}
                        
                        # التحقق من صحة الترخيص
                        if self._validate_license_integrity(license_info):
                            return license_info
                        
            return default_license
            
        except Exception as e:
            print(f"⚠️ خطأ في تحميل الترخيص: {e}")
            return default_license
    
    def _validate_license_integrity(self, license_info: Dict) -> bool:
        """التحقق من سلامة بيانات الترخيص"""
        try:
            # التحقق من الحقول المطلوبة
            required_fields = ["type", "status", "hardware_id", "expiry_date"]
            for field in required_fields:
                if field not in license_info:
                    return False
            
            # التحقق من مطابقة HWID
            if license_info["hardware_id"] != self.hardware_id:
                return False
            
            # التحقق من تاريخ الانتهاء
            expiry_date = datetime.fromisoformat(license_info["expiry_date"])
            if datetime.now() > expiry_date:
                license_info["status"] = "expired"
                return False
            
            # التحقق من التوقيع الرقمي
            if "signature" in license_info:
                signature = license_info.pop("signature")
                data_string = json.dumps(license_info, sort_keys=True)
                
                # إنشاء التوقيع المتوقع
                expected_signature = hashlib.sha256(
                    (data_string + self.hardware_id).encode()
                ).hexdigest()
                
                # إعادة التوقيع
                license_info["signature"] = signature
                
                if signature != expected_signature:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _encrypt_data(self, data: Dict) -> str:
        """تشفير البيانات"""
        try:
            fernet = Fernet(self.encryption_key)
            json_data = json.dumps(data).encode()
            encrypted = fernet.encrypt(json_data)
            return encrypted.decode()
        except Exception as e:
            print(f"❌ خطأ في تشفير البيانات: {e}")
            # طريقة احتياطية
            return base64.b64encode(json.dumps(data).encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> Optional[Dict]:
        """فك تشفير البيانات"""
        try:
            fernet = Fernet(self.encryption_key)
            decrypted = fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted)
        except Exception:
            try:
                # محاولة طريقة Base64 كاحتياطي
                decrypted = base64.b64decode(encrypted_data).decode()
                return json.loads(decrypted)
            except Exception as e:
                print(f"❌ خطأ في فك التشفير: {e}")
                return None
    
    def save_license(self) -> bool:
        """حفظ بيانات الترخيص"""
        try:
            # تحديث تاريخ آخر فحص
            self.license_data["metadata"]["last_check"] = datetime.now().isoformat()
            
            # إنشاء توقيع رقمي
            signature_data = {k: v for k, v in self.license_data.items() if k != "signature"}
            data_string = json.dumps(signature_data, sort_keys=True)
            self.license_data["signature"] = hashlib.sha256(
                (data_string + self.hardware_id).encode()
            ).hexdigest()
            
            # تشفير وحفظ البيانات
            encrypted = self._encrypt_data(self.license_data)
            
            with open(self.license_file, 'w') as f:
                f.write(encrypted)
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في حفظ الترخيص: {e}")
            return False
    
    def activate_trial(self) -> bool:
        """تفعيل النسخة التجريبية"""
        self.license_data = {
            "type": "trial",
            "status": "active",
            "hardware_id": self.hardware_id,
            "plan": "trial",
            "activation_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "license_key": "TRIAL-" + self.hardware_id[:16],
            "buyer_info": {
                "name": "تجريبي",
                "email": "",
                "phone": ""
            },
            "signature": None,
            "metadata": {
                "version": self.VERSION,
                "created_at": datetime.now().isoformat(),
                "last_check": datetime.now().isoformat(),
            }
        }
        
        return self.save_license()
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """تفعيل ترخيص"""
        try:
            # التحقق من التنسيق الأساسي
            if not license_key or len(license_key) < 20:
                return False, "مفتاح الترخيص غير صالح"
            
            # فك التشفير والتحقق
            decrypted = self._decrypt_data(license_key)
            if not decrypted:
                return False, "تعذر فك تشفير مفتاح الترخيص"
            
            # التحقق من البيانات المطلوبة
            required_fields = ["hardware_id", "expiry_date", "plan", "buyer_info"]
            for field in required_fields:
                if field not in decrypted:
                    return False, f"بيانات الترخيص ناقصة: {field}"
            
            # التحقق من مطابقة HWID
            if decrypted["hardware_id"] != self.hardware_id:
                return False, "هذا الترخيص غير مخصص لهذا الجهاز"
            
            # التحقق من تاريخ الانتهاء
            expiry_date = datetime.fromisoformat(decrypted["expiry_date"])
            if datetime.now() > expiry_date:
                return False, "الترخيص منتهي الصلاحية"
            
            # تحديث بيانات الترخيص
            self.license_data = {
                "type": "premium",
                "status": "active",
                "hardware_id": self.hardware_id,
                "plan": decrypted["plan"],
                "activation_date": datetime.now().isoformat(),
                "expiry_date": decrypted["expiry_date"],
                "license_key": license_key,
                "buyer_info": decrypted["buyer_info"],
                "signature": None,
                "metadata": {
                    "version": self.VERSION,
                    "created_at": datetime.now().isoformat(),
                    "last_check": datetime.now().isoformat(),
                }
            }
            
            # حفظ الترخيص
            if self.save_license():
                return True, "تم تفعيل الترخيص بنجاح"
            else:
                return False, "خطأ في حفظ الترخيص"
            
        except Exception as e:
            return False, f"خطأ في التفعيل: {str(e)}"
    
    def check_status(self) -> Dict[str, Any]:
        """التحقق من حالة الترخيص"""
        try:
            expiry_date = datetime.fromisoformat(self.license_data["expiry_date"])
            days_remaining = (expiry_date - datetime.now()).days
            
            return {
                "type": self.license_data["type"],
                "status": self.license_data["status"],
                "plan": self.license_data["plan"],
                "days_remaining": max(0, days_remaining),
                "is_valid": days_remaining > 0,
                "is_trial": self.license_data["type"] == "trial",
                "is_premium": self.license_data["type"] == "premium",
                "expiry_date": self.license_data["expiry_date"],
                "hardware_id": self.hardware_id,
                "buyer_info": self.license_data.get("buyer_info", {}),
            }
            
        except Exception:
            return {
                "type": "invalid",
                "status": "invalid",
                "plan": "none",
                "days_remaining": 0,
                "is_valid": False,
                "is_trial": False,
                "is_premium": False,
                "expiry_date": None,
                "hardware_id": self.hardware_id,
                "buyer_info": {},
            }
    
    def get_hardware_id(self) -> str:
        """الحصول على معرف الجهاز"""
        return self.hardware_id
    
    def is_license_valid(self) -> bool:
        """التحقق إذا كان الترخيص ساري المفعول"""
        status = self.check_status()
        return status["is_valid"]
    
    def generate_license_key(self, buyer_info: Dict, plan: str) -> Optional[str]:
        """إنشاء مفتاح ترخيص جديد (للمطور)"""
        try:
            # حساب تاريخ الانتهاء
            days = self.SUBSCRIPTION_PERIODS.get(plan, 30)
            expiry_date = datetime.now() + timedelta(days=days)
            
            # إنشاء بيانات الترخيص
            license_info = {
                "hardware_id": self.hardware_id,  # سيتغير عند التفعيل
                "plan": plan,
                "expiry_date": expiry_date.isoformat(),
                "buyer_info": buyer_info,
                "generated_at": datetime.now().isoformat(),
                "version": self.VERSION,
                "developer": self.DEVELOPER,
                "developer_email": self.DEVELOPER_EMAIL,
                "developer_phone": self.DEVELOPER_PHONE,
                "signature": None  # سيتم إضافته لاحقاً
            }
            
            # إنشاء توقيع
            signature_data = {k: v for k, v in license_info.items() if k != "signature"}
            data_string = json.dumps(signature_data, sort_keys=True)
            license_info["signature"] = hashlib.sha256(
                (data_string + self.hardware_id).encode()
            ).hexdigest()
            
            # تشفير البيانات
            license_key = self._encrypt_data(license_info)
            
            return license_key
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء مفتاح الترخيص: {e}")
            return None

# إنشاء نسخة عامة لمدير الترخيص
license_manager = LicenseManager()