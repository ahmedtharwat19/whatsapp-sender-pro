import time
import random
import threading
import datetime
from queue import Queue
from selenium.common.exceptions import WebDriverException
from .whatsapp import WhatsAppDriver

class AdvancedSender:
    """نظام إرسال متقدم مع إدارة أخطاء محسنة"""
    
    def __init__(self, driver: WhatsAppDriver):
        self.driver = driver
        self.is_sending = False
        self.message_queue = Queue()
        self.error_count = 0
        self.max_retries = 3
        self.callbacks = {
            'on_progress': None,
            'on_complete': None,
            'on_error': None
        }
    
    def send_bulk(self, contacts, message_template, image_path=None, options=None):
        """إرسال جماعي مع معالجة الأخطاء"""
        options = options or {}
        
        # إعداد الخيارات
        delay_min = options.get('delay_min', 15)
        delay_max = options.get('delay_max', 30)
        max_errors = options.get('max_errors', 5)
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': [],
            'start_time': time.time()
        }
        
        self.is_sending = True
        
        for i, contact in enumerate(contacts):
            if not self.is_sending:
                break
            
            try:
                # إرسال الرسالة
                success = self.send_single(
                    contact=contact,
                    message=message_template,
                    image_path=image_path,
                    retry_count=0
                )
                
                if success:
                    results['success'] += 1
                    self._trigger_callback('on_progress', {
                        'current': i + 1,
                        'total': len(contacts),
                        'success': results['success'],
                        'failed': results['failed']
                    })
                else:
                    results['failed'] += 1
                
                # تأخير ذكي
                if i < len(contacts) - 1:
                    delay = self.calculate_smart_delay(i, len(contacts))
                    time.sleep(delay)
                
                # التحقق من عدد الأخطاء
                if self.error_count >= max_errors:
                    self._trigger_callback('on_error', {
                        'message': 'تم تجاوز الحد الأقصى للأخطاء',
                        'error_count': self.error_count
                    })
                    break
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                self.error_count += 1
        
        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        
        self._trigger_callback('on_complete', results)
        self.is_sending = False
        
        return results
    
    def calculate_smart_delay(self, current, total):
        """حساب تأخير ذكي بناءً على التقدم"""
        # تقليل التأخير في النصف الأول، زيادته في النصف الثاني
        progress = current / total
        
        if progress < 0.5:
            # تأخير أقل في البداية
            return random.randint(10, 20)
        else:
            # تأخير أكبر مع التقدم
            base_delay = 20
            extra_delay = int((progress - 0.5) * 40)  # زيادة تدريجية
            return random.randint(base_delay, base_delay + extra_delay)
    
    def send_single(self, contact, message, image_path=None, retry_count=0):
        """إرسال رسالة واحدة مع إعادة المحاولة"""
        try:
            # فتح الدردشة
            if not self.driver.open_chat(contact['phone']):
                return False
            
            # إرسال الرسالة النصية
            if message:
                formatted_message = self.format_message(message, contact)
                self.driver.send_message(formatted_message)
            
            # إرسال الصورة
            if image_path:
                self.driver.send_image(image_path, contact.get('name', ''))
            
            return True
            
        except WebDriverException as e:
            if retry_count < self.max_retries:
                # إعادة المحاولة
                time.sleep(2 ** retry_count)  # تأخير أسي
                return self.send_single(contact, message, image_path, retry_count + 1)
            else:
                self._trigger_callback('on_error', {
                    'contact': contact,
                    'error': str(e),
                    'retries': retry_count
                })
                return False
    
    def format_message(self, template, contact):
        """تنسيق الرسالة مع المتغيرات"""
        variables = {
            '{name}': contact.get('name', 'عزيزي/عزيزتي'),
            '{phone}': contact.get('phone', ''),
            '{date}': datetime.now().strftime('%Y-%m-%d'),
            '{time}': datetime.now().strftime('%H:%M'),
            '{number}': str(contact.get('index', '')),
        }
        
        message = template
        for key, value in variables.items():
            message = message.replace(key, value)
        
        return message