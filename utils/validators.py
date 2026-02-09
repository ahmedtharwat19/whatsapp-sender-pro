"""
أدوات التحقق من صحة البيانات
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class Validators:
    """فئة أدوات التحقق"""
    
    # أنماط التحقق
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?[0-9]{8,15}$',
        'url': r'^https?://[^\s/$.?#].[^\s]*$',
        'license_key': r'^[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}$',
        'hwid': r'^WS-[A-F0-9]{8}-[A-F0-9]{8}-[A-F0-9]{8}-[A-F0-9]{8}$',
        'date_iso': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?$'
    }
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """التحقق من صحة البريد الإلكتروني"""
        if not email or not isinstance(email, str):
            return False, "البريد الإلكتروني غير صالح"
        
        email = email.strip()
        if len(email) > 254:
            return False, "البريد الإلكتروني طويل جداً"
        
        if not re.match(Validators.PATTERNS['email'], email):
            return False, "تنسيق البريد الإلكتروني غير صحيح"
        
        return True, "البريد الإلكتروني صالح"
    
    @staticmethod
    def validate_phone(phone: str, country_code: str = None) -> Tuple[bool, str]:
        """التحقق من صحة رقم الهاتف"""
        if not phone or not isinstance(phone, str):
            return False, "رقم الهاتف غير صالح"
        
        # تنظيف الرقم
        phone_clean = re.sub(r'[^0-9+]', '', phone)
        
        if not phone_clean:
            return False, "رقم الهاتف فارغ"
        
        # التحقق من الطول
        if len(phone_clean) < 8 or len(phone_clean) > 15:
            return False, "طول رقم الهاتف غير صحيح"
        
        # يمكن إضافة تحقق حسب رمز الدولة
        if country_code:
            if not phone_clean.startswith(country_code):
                phone_clean = country_code + phone_clean.lstrip('0')
        
        if not re.match(Validators.PATTERNS['phone'], phone_clean):
            return False, "تنسيق رقم الهاتف غير صحيح"
        
        return True, phone_clean
    
    @staticmethod
    def validate_license_key_format(license_key: str) -> Tuple[bool, str]:
        """التحقق من تنسيق مفتاح الترخيص"""
        if not license_key or not isinstance(license_key, str):
            return False, "مفتاح الترخيص غير صالح"
        
        license_key = license_key.strip().upper()
        
        # التحقق من النمط الأساسي
        if not re.match(Validators.PATTERNS['license_key'], license_key):
            return False, "تنسيق مفتاح الترخيص غير صحيح"
        
        # التحقق من مجموعات الأرقام
        groups = license_key.split('-')
        if len(groups) != 5:
            return False, "مفتاح الترخيص يجب أن يحتوي على 5 مجموعات"
        
        # يمكن إضافة المزيد من التحقق حسب الحاجة
        return True, license_key
    
    @staticmethod
    def validate_hwid(hwid: str) -> Tuple[bool, str]:
        """التحقق من معرف الجهاز"""
        if not hwid or not isinstance(hwid, str):
            return False, "معرف الجهاز غير صالح"
        
        hwid = hwid.strip().upper()
        
        if not re.match(Validators.PATTERNS['hwid'], hwid):
            return False, "تنسيق معرف الجهاز غير صحيح"
        
        return True, hwid
    
    @staticmethod
    def validate_date(date_str: str, date_format: str = 'iso') -> Tuple[bool, Optional[datetime]]:
        """التحقق من صحة التاريخ"""
        if not date_str or not isinstance(date_str, str):
            return False, None
        
        try:
            if date_format == 'iso':
                if not re.match(Validators.PATTERNS['date_iso'], date_str):
                    return False, None
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_str, date_format)
            
            return True, date_obj
            
        except ValueError:
            return False, None
    
    @staticmethod
    def validate_json(data: str) -> Tuple[bool, Optional[Dict]]:
        """التحقق من صحة JSON"""
        try:
            parsed = json.loads(data)
            return True, parsed
        except json.JSONDecodeError as e:
            logger.error(f"خطأ في تحليل JSON: {e}")
            return False, None
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """التحقق من امتداد الملف"""
        if not filename:
            return False
        
        ext = filename.lower().split('.')[-1]
        return ext in [ext.lower() for ext in allowed_extensions]
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: float) -> Tuple[bool, float]:
        """التحقق من حجم الملف"""
        try:
            import os
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            
            if size_mb > max_size_mb:
                return False, size_mb
            
            return True, size_mb
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من حجم الملف: {e}")
            return False, 0
    
    @staticmethod
    def validate_image_file(file_path: str) -> Tuple[bool, str]:
        """التحقق من صحة ملف الصورة"""
        try:
            from PIL import Image
            
            # التحقق من الامتداد
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
            if not Validators.validate_file_extension(file_path, allowed_extensions):
                return False, "امتداد الملف غير مدعوم"
            
            # التحقق من أن الملف صورة صالحة
            try:
                with Image.open(file_path) as img:
                    img.verify()  # التحقق من سلامة الصورة
                
                # التحقق من الأبعاد
                with Image.open(file_path) as img:
                    width, height = img.size
                    if width == 0 or height == 0:
                        return False, "أبعاد الصورة غير صالحة"
                    
                    if width > 10000 or height > 10000:
                        return False, "الصورة كبيرة جداً"
                
                return True, "الصورة صالحة"
                
            except Exception as e:
                return False, f"ملف الصورة تالف: {str(e)}"
                
        except ImportError:
            logger.warning("لم يتم العثور على Pillow، تخطي التحقق المتقدم للصورة")
            return True, "تم تخطي التحقق المتقدم"
        except Exception as e:
            logger.error(f"خطأ في التحقق من ملف الصورة: {e}")
            return False, f"خطأ في التحقق: {str(e)}"
    
    @staticmethod
    def validate_contact_data(contact: Dict) -> Tuple[bool, List[str]]:
        """التحقق من بيانات جهة الاتصال"""
        errors = []
        
        # التحقق من الهاتف
        phone = contact.get('phone') or contact.get('Phone') or contact.get('PHONE')
        if not phone:
            errors.append("رقم الهاتف مطلوب")
        else:
            phone_valid, phone_msg = Validators.validate_phone(str(phone))
            if not phone_valid:
                errors.append(f"رقم الهاتف غير صالح: {phone_msg}")
        
        # التحقق من الاسم (اختياري ولكن مستحسن)
        name = contact.get('name') or contact.get('Name') or contact.get('NAME')
        if not name:
            errors.append("الاسم مستحسن")
        elif len(str(name)) > 100:
            errors.append("الاسم طويل جداً")
        
        # التحقق من البيانات الإضافية
        if 'data' in contact and contact['data']:
            try:
                json.dumps(contact['data'])  # التحقق من إمكانية التسلسل
            except:
                errors.append("البيانات الإضافية غير صالحة")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_message_content(message: str, max_length: int = 1000) -> Tuple[bool, str]:
        """التحقق من محتوى الرسالة"""
        if not message or not isinstance(message, str):
            return False, "الرسالة فارغة"
        
        message = message.strip()
        
        if len(message) == 0:
            return False, "الرسالة فارغة"
        
        if len(message) > max_length:
            return False, f"الرسالة طويلة جداً (الحد الأقصى: {max_length} حرف)"
        
        # التحقق من المحتوى غير المرغوب فيه
        spam_indicators = [
            'http://', 'https://', '.com', '.net', '.org',
            'FREE', 'WINNER', 'PRIZE', 'URGENT', 'IMPORTANT'
        ]
        
        message_upper = message.upper()
        for indicator in spam_indicators:
            if indicator in message_upper:
                return False, "قد تحتوي الرسالة على محتوى غير مرغوب فيه"
        
        return True, "الرسالة صالحة"
    
    @staticmethod
    def validate_license_data(license_data: Dict) -> Tuple[bool, List[str]]:
        """التحقق من بيانات الترخيص"""
        errors = []
        
        required_fields = ['license_key', 'license_type', 'client_name', 'client_email']
        
        for field in required_fields:
            if field not in license_data or not license_data[field]:
                errors.append(f"الحقل '{field}' مطلوب")
        
        if 'license_key' in license_data and license_data['license_key']:
            key_valid, key_msg = Validators.validate_license_key_format(license_data['license_key'])
            if not key_valid:
                errors.append(key_msg)
        
        if 'client_email' in license_data and license_data['client_email']:
            email_valid, email_msg = Validators.validate_email(license_data['client_email'])
            if not email_valid:
                errors.append(email_msg)
        
        if 'hwid' in license_data and license_data['hwid']:
            hwid_valid, hwid_msg = Validators.validate_hwid(license_data['hwid'])
            if not hwid_valid:
                errors.append(hwid_msg)
        
        if 'expiry_date' in license_data and license_data['expiry_date']:
            date_valid, date_obj = Validators.validate_date(license_data['expiry_date'])
            if not date_valid:
                errors.append("تاريخ الانتهاء غير صالح")
            elif date_obj and date_obj < datetime.now():
                errors.append("تاريخ الانتهاء منقضي")
        
        return len(errors) == 0, errors