# app/core/encryption_service.py
"""
خدمة التشفير - لتشفير البيانات الحساسة
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
import json
import logging

class EncryptionService:
    def __init__(self, key_file="config/encryption_keys.json"):
        """تهيئة خدمة التشفير"""
        self.logger = logging.getLogger(__name__)
        self.key_file = key_file
        self.keys = self._load_or_generate_keys()
    
    def _load_or_generate_keys(self):
        """تحميل أو إنشاء مفاتيح التشفير"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'r') as f:
                    keys = json.load(f)
                
                # تحويل المفاتيح من base64
                keys['fernet_key'] = base64.urlsafe_b64decode(keys['fernet_key'].encode())
                keys['pbkdf_salt'] = base64.urlsafe_b64decode(keys['pbkdf_salt'].encode())
                
                return keys
            else:
                # إنشاء مفاتيح جديدة
                keys = {
                    'fernet_key': Fernet.generate_key(),
                    'pbkdf_salt': os.urandom(16)
                }
                
                # حفظ المفاتيح
                self._save_keys(keys)
                
                return keys
                
        except Exception as e:
            self.logger.error(f"خطأ في تحميل/إنشاء المفاتيح: {e}")
            
            # إنشاء مفاتيح طارئة
            return {
                'fernet_key': Fernet.generate_key(),
                'pbkdf_salt': os.urandom(16)
            }
    
    def _save_keys(self, keys):
        """حفظ المفاتيح"""
        try:
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            
            keys_to_save = {
                'fernet_key': base64.urlsafe_b64encode(keys['fernet_key']).decode(),
                'pbkdf_salt': base64.urlsafe_b64encode(keys['pbkdf_salt']).decode()
            }
            
            with open(self.key_file, 'w') as f:
                json.dump(keys_to_save, f)
                
        except Exception as e:
            self.logger.error(f"خطأ في حفظ المفاتيح: {e}")
    
    def encrypt(self, data):
        """تشفير البيانات"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            
            fernet = Fernet(self.keys['fernet_key'])
            encrypted = fernet.encrypt(data.encode())
            
            return base64.urlsafe_b64encode(encrypted).decode()
            
        except Exception as e:
            self.logger.error(f"خطأ في التشفير: {e}")
            return None
    
    def decrypt(self, encrypted_data):
        """فك تشفير البيانات"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            fernet = Fernet(self.keys['fernet_key'])
            decrypted = fernet.decrypt(encrypted_bytes)
            
            # محاولة تحويل JSON
            try:
                return json.loads(decrypted.decode())
            except:
                return decrypted.decode()
                
        except Exception as e:
            self.logger.error(f"خطأ في فك التشفير: {e}")
            return None
    
    def derive_key_from_password(self, password, salt=None):
        """اشتقاق مفتاح من كلمة المرور"""
        try:
            if salt is None:
                salt = self.keys['pbkdf_salt']
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
            
        except Exception as e:
            self.logger.error(f"خطأ في اشتقاق المفتاح: {e}")
            return None
    
    def encrypt_file(self, file_path, output_path=None):
        """تشفير ملف"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"الملف غير موجود: {file_path}")
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            fernet = Fernet(self.keys['fernet_key'])
            encrypted_data = fernet.encrypt(data)
            
            if output_path is None:
                output_path = file_path + '.enc'
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"خطأ في تشفير الملف: {e}")
            return None
    
    def decrypt_file(self, file_path, output_path=None):
        """فك تشفير ملف"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"الملف غير موجود: {file_path}")
            
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            fernet = Fernet(self.keys['fernet_key'])
            decrypted_data = fernet.decrypt(encrypted_data)
            
            if output_path is None:
                if file_path.endswith('.enc'):
                    output_path = file_path[:-4]
                else:
                    output_path = file_path + '.dec'
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"خطأ في فك تشفير الملف: {e}")
            return None