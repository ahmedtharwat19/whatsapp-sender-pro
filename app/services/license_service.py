# app/services/license_service.py
"""
خدمة الترخيص - لإدارة عمليات الترخيص
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.core.encryption_service import EncryptionService

class LicenseService:
    def __init__(self, api_url=None):
        """تهيئة خدمة الترخيص"""
        self.logger = logging.getLogger(__name__)
        self.api_url = api_url or "https://your-license-api.com"
        self.encryption_service = EncryptionService()
        
    def verify_license_online(self, license_key: str, hwid: str) -> Dict:
        """التحقق من الترخيص عبر الإنترنت"""
        try:
            payload = {
                'license_key': license_key,
                'hwid': hwid,
                'timestamp': datetime.now().isoformat()
            }
            
            # تشفير البيانات قبل الإرسال
            encrypted_payload = self.encryption_service.encrypt(payload)
            
            response = requests.post(
                f"{self.api_url}/verify",
                json={'data': encrypted_payload},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    return {
                        'valid': True,
                        'type': result.get('type'),
                        'expiry_date': result.get('expiry_date'),
                        'uses': result.get('uses'),
                        'max_uses': result.get('max_uses'),
                        'plan': result.get('plan')
                    }
            
            return {'valid': False, 'message': 'Invalid license'}
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق عبر الإنترنت: {e}")
            return {'valid': False, 'message': 'Connection error'}
    
    def activate_license(self, license_key: str, hwid: str, user_info: Dict) -> Dict:
        """تفعيل ترخيص جديد"""
        try:
            payload = {
                'license_key': license_key,
                'hwid': hwid,
                'user_info': user_info,
                'timestamp': datetime.now().isoformat()
            }
            
            encrypted_payload = self.encryption_service.encrypt(payload)
            
            response = requests.post(
                f"{self.api_url}/activate",
                json={'data': encrypted_payload},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            
            return {'success': False, 'message': 'Activation failed'}
            
        except Exception as e:
            self.logger.error(f"خطأ في تفعيل الترخيص: {e}")
            return {'success': False, 'message': 'Connection error'}
    
    def check_updates(self, current_version: str) -> Dict:
        """التحقق من التحديثات"""
        try:
            payload = {
                'version': current_version,
                'hwid': 'check-update',
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_url}/check-update",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {'update_available': False}
            
        except Exception as e:
            self.logger.error(f"خطأ في التحقق من التحديثات: {e}")
            return {'update_available': False}
    
    def send_usage_statistics(self, license_key: str, stats: Dict) -> bool:
        """إرسال إحصائيات الاستخدام"""
        try:
            payload = {
                'license_key': license_key,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
            encrypted_payload = self.encryption_service.encrypt(payload)
            
            response = requests.post(
                f"{self.api_url}/stats",
                json={'data': encrypted_payload},
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الإحصائيات: {e}")
            return False
    
    def get_pricing_plans(self) -> Dict:
        """الحصول على خطط الأسعار"""
        try:
            response = requests.get(f"{self.api_url}/pricing", timeout=5)
            
            if response.status_code == 200:
                return response.json()
            
            # خطط افتراضية في حالة فشل الاتصال
            return {
                'plans': [
                    {'name': 'trial', 'price': 0, 'duration_days': 7, 'max_uses': 50},
                    {'name': '1_month', 'price': 500, 'duration_days': 30, 'max_uses': 1000},
                    {'name': '3_months', 'price': 1200, 'duration_days': 90, 'max_uses': 3000},
                    {'name': '6_months', 'price': 2000, 'duration_days': 180, 'max_uses': 6000},
                    {'name': '9_months', 'price': 2800, 'duration_days': 270, 'max_uses': 9000},
                    {'name': '1_year', 'price': 3800, 'duration_days': 365, 'max_uses': 12000}
                ],
                'currency': 'EGP'
            }
            
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على خطط الأسعار: {e}")
            # إرجاع الخطط الافتراضية
            return {
                'plans': [
                    {'name': 'trial', 'price': 0, 'duration_days': 7, 'max_uses': 50},
                    {'name': '1_month', 'price': 500, 'duration_days': 30, 'max_uses': 1000},
                    {'name': '3_months', 'price': 1200, 'duration_days': 90, 'max_uses': 3000},
                    {'name': '6_months', 'price': 2000, 'duration_days': 180, 'max_uses': 6000},
                    {'name': '9_months', 'price': 2800, 'duration_days': 270, 'max_uses': 9000},
                    {'name': '1_year', 'price': 3800, 'duration_days': 365, 'max_uses': 12000}
                ],
                'currency': 'EGP'
            }