"""
خدمة المصادقة - لإدارة عمليات تسجيل الدخول والمستخدمين
"""

import hashlib
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.core.encryption_service import EncryptionService

class AuthService:
    def __init__(self, secret_key=None):
        """تهيئة خدمة المصادقة"""
        self.logger = logging.getLogger(__name__)
        self.secret_key = secret_key or "your-jwt-secret-key-change-in-production"
        self.encryption_service = EncryptionService()
        self.users = {}  # تخزين مؤقت للمستخدمين
        
    def hash_password(self, password: str) -> str:
        """تجزئة كلمة المرور"""
        salt = "whatsapp-sender-pro-salt"
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def register_user(self, username: str, password: str, email: str, role: str = "user") -> Dict:
        """تسجيل مستخدم جديد"""
        try:
            if username in self.users:
                return {"success": False, "message": "اسم المستخدم موجود بالفعل"}
            
            hashed_password = self.hash_password(password)
            
            user_data = {
                "username": username,
                "password": hashed_password,
                "email": email,
                "role": role,
                "created_at": datetime.now().isoformat(),
                "is_active": True,
                "failed_attempts": 0,
                "last_login": None
            }
            
            self.users[username] = user_data
            
            # إنشاء token
            token = self.create_token(username, role)
            
            return {
                "success": True,
                "message": "تم تسجيل المستخدم بنجاح",
                "token": token,
                "user": {
                    "username": username,
                    "email": email,
                    "role": role
                }
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل المستخدم: {e}")
            return {"success": False, "message": "خطأ في تسجيل المستخدم"}
    
    def login(self, username: str, password: str) -> Dict:
        """تسجيل الدخول"""
        try:
            if username not in self.users:
                return {"success": False, "message": "اسم المستخدم أو كلمة المرور غير صحيحة"}
            
            user = self.users[username]
            
            # التحقق من الحظر
            if not user["is_active"]:
                return {"success": False, "message": "الحساب معطل"}
            
            # التحقق من كلمة المرور
            hashed_password = self.hash_password(password)
            if user["password"] != hashed_password:
                user["failed_attempts"] = user.get("failed_attempts", 0) + 1
                
                if user["failed_attempts"] >= 5:
                    user["is_active"] = False
                    return {"success": False, "message": "تم تعطيل الحساب بعد محاولات فاشلة كثيرة"}
                
                return {"success": False, "message": "اسم المستخدم أو كلمة المرور غير صحيحة"}
            
            # إعادة تعيين محاولات الفشل
            user["failed_attempts"] = 0
            user["last_login"] = datetime.now().isoformat()
            
            # إنشاء token
            token = self.create_token(username, user["role"])
            
            return {
                "success": True,
                "message": "تم تسجيل الدخول بنجاح",
                "token": token,
                "user": {
                    "username": username,
                    "email": user["email"],
                    "role": user["role"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل الدخول: {e}")
            return {"success": False, "message": "خطأ في تسجيل الدخول"}
    
    def create_token(self, username: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
        """إنشاء JWT token"""
        try:
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(hours=24)
            
            payload = {
                "sub": username,
                "role": role,
                "exp": expire,
                "iat": datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            return token
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء token: {e}")
            return ""
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """التحقق من صحة token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            username = payload.get("sub")
            
            if username in self.users:
                return {
                    "username": username,
                    "role": payload.get("role"),
                    "expires": payload.get("exp")
                }
            
            return None
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token منتهي الصلاحية")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Token غير صالح")
            return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Dict:
        """تغيير كلمة المرور"""
        try:
            if username not in self.users:
                return {"success": False, "message": "المستخدم غير موجود"}
            
            user = self.users[username]
            
            # التحقق من كلمة المرور القديمة
            old_hashed = self.hash_password(old_password)
            if user["password"] != old_hashed:
                return {"success": False, "message": "كلمة المرور القديمة غير صحيحة"}
            
            # تحديث كلمة المرور
            new_hashed = self.hash_password(new_password)
            user["password"] = new_hashed
            
            return {"success": True, "message": "تم تغيير كلمة المرور بنجاح"}
            
        except Exception as e:
            self.logger.error(f"خطأ في تغيير كلمة المرور: {e}")
            return {"success": False, "message": "خطأ في تغيير كلمة المرور"}
    
    def reset_password(self, email: str) -> Dict:
        """إعادة تعيين كلمة المرور"""
        try:
            # البحث عن المستخدم بالبريد الإلكتروني
            user = None
            for username, user_data in self.users.items():
                if user_data.get("email") == email:
                    user = user_data
                    break
            
            if not user:
                return {"success": False, "message": "البريد الإلكتروني غير مسجل"}
            
            # إنشاء كلمة مرور مؤقتة
            import random
            import string
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # تحديث كلمة المرور
            user["password"] = self.hash_password(temp_password)
            
            # في الواقع، هنا سنرسل البريد الإلكتروني
            # self.send_reset_email(email, temp_password)
            
            self.logger.info(f"كلمة المرور المؤقتة لـ {email}: {temp_password}")
            
            return {
                "success": True,
                "message": "تم إنشاء كلمة مرور مؤقتة",
                "temp_password": temp_password  # في الإنتاج، لا ترسل هذا!
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في إعادة تعيين كلمة المرور: {e}")
            return {"success": False, "message": "خطأ في إعادة تعيين كلمة المرور"}
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """الحصول على معلومات المستخدم"""
        if username in self.users:
            user = self.users[username].copy()
            user.pop("password", None)  # إزالة كلمة المرور
            return user
        return None
    
    def update_user_profile(self, username: str, update_data: Dict) -> Dict:
        """تحديث ملف المستخدم"""
        try:
            if username not in self.users:
                return {"success": False, "message": "المستخدم غير موجود"}
            
            user = self.users[username]
            
            # تحديث البيانات المسموح بها
            allowed_fields = ["email", "phone", "name", "company"]
            for field in allowed_fields:
                if field in update_data:
                    user[field] = update_data[field]
            
            return {"success": True, "message": "تم تحديث الملف بنجاح"}
            
        except Exception as e:
            self.logger.error(f"خطأ في تحديث ملف المستخدم: {e}")
            return {"success": False, "message": "خطأ في تحديث الملف"}
    
    def logout(self, username: str) -> Dict:
        """تسجيل الخروج"""
        try:
            if username in self.users:
                user = self.users[username]
                user["last_logout"] = datetime.now().isoformat()
                
                # إلغاء Token (في تطبيق حقيقي، سنضيفه إلى القائمة السوداء)
                return {"success": True, "message": "تم تسجيل الخروج بنجاح"}
            
            return {"success": False, "message": "المستخدم غير موجود"}
            
        except Exception as e:
            self.logger.error(f"خطأ في تسجيل الخروج: {e}")
            return {"success": False, "message": "خطأ في تسجيل الخروج"}
    
    def check_permission(self, username: str, required_role: str) -> bool:
        """التحقق من صلاحيات المستخدم"""
        if username not in self.users:
            return False
        
        user_role = self.users[username].get("role", "user")
        
        # هرمية الصلاحيات
        role_hierarchy = {
            "admin": ["admin", "moderator", "user"],
            "moderator": ["moderator", "user"],
            "user": ["user"]
        }
        
        return required_role in role_hierarchy.get(user_role, [])