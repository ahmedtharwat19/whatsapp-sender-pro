"""
نماذج قاعدة البيانات
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class License:
    """نموذج الترخيص"""
    
    def __init__(self, 
                 license_key: str,
                 license_type: str,
                 client_name: str,
                 client_email: str,
                 hwid: Optional[str] = None,
                 created_date: Optional[str] = None,
                 expiry_date: Optional[str] = None,
                 status: str = "active",
                 uses: int = 0,
                 max_uses: int = 1000,
                 client_phone: Optional[str] = None,
                 company: Optional[str] = None):
        
        self.license_key = license_key
        self.license_type = license_type
        self.client_name = client_name
        self.client_email = client_email
        self.hwid = hwid
        self.created_date = created_date or datetime.now().isoformat()
        self.expiry_date = expiry_date
        self.status = status
        self.uses = uses
        self.max_uses = max_uses
        self.client_phone = client_phone
        self.company = company
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "license_key": self.license_key,
            "license_type": self.license_type,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "hwid": self.hwid,
            "created_date": self.created_date,
            "expiry_date": self.expiry_date,
            "status": self.status,
            "uses": self.uses,
            "max_uses": self.max_uses,
            "client_phone": self.client_phone,
            "company": self.company,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'License':
        """إنشاء من قاموس"""
        return cls(
            license_key=data.get("license_key", ""),
            license_type=data.get("license_type", "trial"),
            client_name=data.get("client_name", ""),
            client_email=data.get("client_email", ""),
            hwid=data.get("hwid"),
            created_date=data.get("created_date"),
            expiry_date=data.get("expiry_date"),
            status=data.get("status", "active"),
            uses=data.get("uses", 0),
            max_uses=data.get("max_uses", 1000),
            client_phone=data.get("client_phone"),
            company=data.get("company")
        )
    
    def is_valid(self) -> bool:
        """التحقق من صلاحية الترخيص"""
        from datetime import datetime
        
        # التحقق من الحالة
        if self.status != "active":
            return False
        
        # التحقق من الاستخدامات
        if self.uses >= self.max_uses:
            return False
        
        # التحقق من تاريخ الانتهاء
        if self.expiry_date:
            expiry = datetime.fromisoformat(self.expiry_date)
            if datetime.now() > expiry:
                self.status = "expired"
                return False
        
        return True
    
    def increment_uses(self) -> None:
        """زيادة عدد الاستخدامات"""
        self.uses += 1
        self.updated_at = datetime.now().isoformat()


class User:
    """نموذج المستخدم"""
    
    def __init__(self,
                 username: str,
                 email: str,
                 password_hash: str,
                 role: str = "user",
                 is_active: bool = True,
                 created_at: Optional[str] = None,
                 last_login: Optional[str] = None,
                 failed_attempts: int = 0,
                 phone: Optional[str] = None,
                 name: Optional[str] = None,
                 company: Optional[str] = None):
        
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.created_at = created_at or datetime.now().isoformat()
        self.last_login = last_login
        self.failed_attempts = failed_attempts
        self.phone = phone
        self.name = name
        self.company = company
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "failed_attempts": self.failed_attempts,
            "phone": self.phone,
            "name": self.name,
            "company": self.company,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """إنشاء من قاموس"""
        return cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            password_hash=data.get("password_hash", ""),
            role=data.get("role", "user"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            last_login=data.get("last_login"),
            failed_attempts=data.get("failed_attempts", 0),
            phone=data.get("phone"),
            name=data.get("name"),
            company=data.get("company")
        )


class MessageLog:
    """نموذج سجل الرسائل"""
    
    def __init__(self,
                 message_id: str,
                 phone_number: str,
                 message: str,
                 status: str,
                 sent_at: Optional[str] = None,
                 image_path: Optional[str] = None,
                 license_key: Optional[str] = None,
                 error_message: Optional[str] = None):
        
        self.message_id = message_id
        self.phone_number = phone_number
        self.message = message
        self.status = status  # success, failed, pending
        self.sent_at = sent_at or datetime.now().isoformat()
        self.image_path = image_path
        self.license_key = license_key
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "message_id": self.message_id,
            "phone_number": self.phone_number,
            "message": self.message[:500],  # تقصير الرسالة
            "status": self.status,
            "sent_at": self.sent_at,
            "image_path": self.image_path,
            "license_key": self.license_key,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageLog':
        """إنشاء من قاموس"""
        return cls(
            message_id=data.get("message_id", ""),
            phone_number=data.get("phone_number", ""),
            message=data.get("message", ""),
            status=data.get("status", "pending"),
            sent_at=data.get("sent_at"),
            image_path=data.get("image_path"),
            license_key=data.get("license_key"),
            error_message=data.get("error_message")
        )


class ActivityLog:
    """نموذج سجل النشاط"""
    
    def __init__(self,
                 log_id: str,
                 activity_type: str,
                 description: str,
                 user: Optional[str] = None,
                 ip_address: Optional[str] = None,
                 timestamp: Optional[str] = None,
                 details: Optional[Dict] = None):
        
        self.log_id = log_id
        self.activity_type = activity_type  # login, logout, send_message, etc.
        self.description = description
        self.user = user
        self.ip_address = ip_address
        self.timestamp = timestamp or datetime.now().isoformat()
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "log_id": self.log_id,
            "activity_type": self.activity_type,
            "description": self.description,
            "user": self.user,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp,
            "details": json.dumps(self.details) if self.details else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActivityLog':
        """إنشاء من قاموس"""
        details = data.get("details")
        if details and isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                details = {}
        
        return cls(
            log_id=data.get("log_id", ""),
            activity_type=data.get("activity_type", ""),
            description=data.get("description", ""),
            user=data.get("user"),
            ip_address=data.get("ip_address"),
            timestamp=data.get("timestamp"),
            details=details
        )


class SystemSettings:
    """نموذج إعدادات النظام"""
    
    def __init__(self,
                 setting_id: str,
                 setting_key: str,
                 setting_value: str,
                 setting_type: str = "string",
                 description: Optional[str] = None,
                 updated_at: Optional[str] = None):
        
        self.setting_id = setting_id
        self.setting_key = setting_key
        self.setting_value = setting_value
        self.setting_type = setting_type
        self.description = description
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "setting_id": self.setting_id,
            "setting_key": self.setting_key,
            "setting_value": self.setting_value,
            "setting_type": self.setting_type,
            "description": self.description,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemSettings':
        """إنشاء من قاموس"""
        return cls(
            setting_id=data.get("setting_id", ""),
            setting_key=data.get("setting_key", ""),
            setting_value=data.get("setting_value", ""),
            setting_type=data.get("setting_type", "string"),
            description=data.get("description"),
            updated_at=data.get("updated_at")
        )
    
    def get_value(self):
        """الحصول على القيمة بالأنواع المناسبة"""
        if self.setting_type == "integer":
            return int(self.setting_value)
        elif self.setting_type == "float":
            return float(self.setting_value)
        elif self.setting_type == "boolean":
            return self.setting_value.lower() == "true"
        elif self.setting_type == "json":
            try:
                return json.loads(self.setting_value)
            except:
                return {}
        else:
            return self.setting_value