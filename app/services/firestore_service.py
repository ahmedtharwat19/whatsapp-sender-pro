# app/services/firestore_service.py
"""
خدمة Firebase Firestore - للتواصل مع قاعدة البيانات
"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client
from google.cloud.exceptions import GoogleCloudError
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List

class FirestoreService:
    def __init__(self, config_file="config/firebase_config.json"):
        """تهيئة خدمة Firebase"""
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.cred = None
        self.app = None
        self.db: Optional[Client] = None

        self.initialize()
        
    def initialize(self) -> bool:
        """تهيئة اتصال Firebase"""
        try:
            if not firebase_admin._apps:
                self.cred = credentials.Certificate(self.config_file)
                self.app = firebase_admin.initialize_app(self.cred)
            
            self.db = firestore.client()
            self.logger.info("تم تهيئة اتصال Firebase بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في تهيئة Firebase: {e}")
            return False
    
    def save_license(self, license_data: Dict) -> bool:
        """حفظ ترخيص في قاعدة البيانات"""
        try:
            if not self.db:
                self.initialize()
            
            license_ref = self.db.collection('licenses').document()
            license_data['id'] = license_ref.id
            license_data['updated_at'] = datetime.now().isoformat()
            
            license_ref.set(license_data)
            self.logger.info(f"تم حفظ الترخيص: {license_data.get('license_key', '')[:20]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في حفظ الترخيص: {e}")
            return False
    
    def validate_license(self, license_key: str, hwid: str) -> bool:
        """التحقق من صلاحية الترخيص"""
        try:
            if not self.db:
                self.initialize()
            
            # البحث عن الترخيص
            licenses_ref = self.db.collection('licenses')
            query = licenses_ref.where('license_key', '==', license_key).limit(1)
            docs = query.stream()
            
            for doc in docs:
                license_data = doc.to_dict()
                
                # التحقق من HWID
                if license_data.get('hwid') and license_data['hwid'] != hwid:
                    self.logger.warning(f"HWID غير مطابق للترخيص: {license_key[:20]}...")
                    return False
                
                # التحقق من تاريخ الانتهاء
                expiry_date_str = license_data.get('expiry_date')
                if expiry_date_str:
                    expiry_date = datetime.fromisoformat(expiry_date_str)
                    if datetime.now() > expiry_date:
                        self.logger.warning(f"الترخيص منتهي: {license_key[:20]}...")
                        # تحديث الحالة
                        doc.reference.update({'status': 'expired'})
                        return False
                
                # التحقق من الحالة
                if license_data.get('status') != 'active':
                    self.logger.warning(f"الترخيص غير نشط: {license_key[:20]}...")
                    return False
                
                # تحديث عدد الاستخدامات
                current_uses = license_data.get('uses', 0)
                doc.reference.update({
                    'uses': current_uses + 1,
                    'last_used': datetime.now().isoformat()
                })
                
                self.logger.info(f"تم التحقق من الترخيص بنجاح: {license_key[:20]}...")
                return True
            
            self.logger.warning(f"الترخيص غير موجود: {license_key[:20]}...")
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من الترخيص: {e}")
            return False
    
    def get_license_info(self, license_key: str) -> Optional[Dict]:
        """الحصول على معلومات الترخيص"""
        try:
            if not self.db:
                self.initialize()
            
            licenses_ref = self.db.collection('licenses')
            query = licenses_ref.where('license_key', '==', license_key).limit(1)
            docs = query.stream()
            
            for doc in docs:
                return doc.to_dict()
            
            return None
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على معلومات الترخيص: {e}")
            return None
    
    def update_license(self, license_key: str, update_data: Dict) -> bool:
        """تحديث بيانات الترخيص"""
        try:
            if not self.db:
                self.initialize()
            
            licenses_ref = self.db.collection('licenses')
            query = licenses_ref.where('license_key', '==', license_key).limit(1)
            docs = query.stream()
            
            for doc in docs:
                update_data['updated_at'] = datetime.now().isoformat()
                doc.reference.update(update_data)
                self.logger.info(f"تم تحديث الترخيص: {license_key[:20]}...")
                return True
            
            self.logger.warning(f"الترخيص غير موجود للتحديث: {license_key[:20]}...")
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في تحديث الترخيص: {e}")
            return False
    
    def delete_license(self, license_key: str) -> bool:
        """حذف ترخيص"""
        try:
            if not self.db:
                self.initialize()
            
            licenses_ref = self.db.collection('licenses')
            query = licenses_ref.where('license_key', '==', license_key).limit(1)
            docs = query.stream()
            
            for doc in docs:
                doc.reference.delete()
                self.logger.info(f"تم حذف الترخيص: {license_key[:20]}...")
                return True
            
            self.logger.warning(f"الترخيص غير موجود للحذف: {license_key[:20]}...")
            return False
            
        except Exception as e:
            self.logger.error(f"خطأ في حذف الترخيص: {e}")
            return False
    
    def get_all_licenses(self, limit: int = 100) -> List[Dict]:
        """الحصول على جميع التراخيص"""
        try:
            if not self.db:
                self.initialize()
            
            licenses_ref = self.db.collection('licenses')
            docs = licenses_ref.order_by('created_date', direction='DESCENDING').limit(limit).stream()
            
            licenses = []
            for doc in docs:
                license_data = doc.to_dict()
                license_data['doc_id'] = doc.id
                licenses.append(license_data)
            
            return licenses
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على التراخيص: {e}")
            return []
    
    def search_licenses(self, search_term: str, search_field: str = 'client_name') -> List[Dict]:
        """بحث في التراخيص"""
        try:
            if not self.db:
                self.initialize()
            
            licenses_ref = self.db.collection('licenses')
            
            # Note: Firestore لا يدعم البحث الجزئي، لذلك نحتاج لطريقة بديلة
            # يمكن استخدام Cloud Functions أو Algolia للبحث المتقدم
            query = licenses_ref.where(search_field, '>=', search_term).where(
                search_field, '<=', search_term + '\uf8ff'
            ).limit(50)
            
            docs = query.stream()
            
            licenses = []
            for doc in docs:
                license_data = doc.to_dict()
                license_data['doc_id'] = doc.id
                licenses.append(license_data)
            
            return licenses
            
        except Exception as e:
            self.logger.error(f"خطأ في البحث: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات النظام"""
        try:
            if not self.db:
                self.initialize()
            
            stats = {
                'total_licenses': 0,
                'active_licenses': 0,
                'expired_licenses': 0,
                'total_revenue': 0,
                'monthly_revenue': 0,
                'active_users': 0
            }
            
            # هذه إحصائيات تجميعية - في الإنتاج الحقيقي، 
            # يجب استخدام Cloud Functions لحساب الإحصائيات
            licenses_ref = self.db.collection('licenses')
            docs = licenses_ref.stream()
            
            for doc in docs:
                license_data = doc.to_dict()
                stats['total_licenses'] += 1
                
                if license_data.get('status') == 'active':
                    stats['active_licenses'] += 1
                    stats['active_users'] += 1
                
                if license_data.get('status') == 'expired':
                    stats['expired_licenses'] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على الإحصائيات: {e}")
            return {}