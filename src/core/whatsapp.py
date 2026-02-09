"""
WhatsApp Web Automation Core
"""

import time
import random
import threading
from typing import Optional, Dict, Any, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    WebDriverException, ElementNotInteractableException
)

class WhatsAppDriver:
    """مدير متصفح واتساب"""
    
    def __init__(self, settings: Optional[Dict] = None):
        self.settings = settings or {}
        self.driver: Optional[webdriver.Chrome] = None
        self.is_connected = False
        self.is_authenticated = False
        self.wait_timeout = 60
        self.chat_opened = False
        
    def initialize_driver(self) -> bool:
        """تهيئة متصفح Chrome"""
        try:
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            # خيارات Chrome
            options = Options()
            
            # إعدادات المستخدم
            user_data_dir = self.settings.get("user_data_dir", "chrome_profile")
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument("--profile-directory=Default")
            
            # إعدادات الأداء
            if self.settings.get("headless", False):
                options.add_argument("--headless=new")
            
            if self.settings.get("disable_gpu", False):
                options.add_argument("--disable-gpu")
            
            if self.settings.get("no_sandbox", False):
                options.add_argument("--no-sandbox")
            
            if self.settings.get("disable_dev_shm", True):
                options.add_argument("--disable-dev-shm-usage")
            
            # إعدادات واجهة المستخدم
            if self.settings.get("disable_notifications", True):
                options.add_argument("--disable-notifications")
            
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # إخفاء WebDriver
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # محاولة استخدام webdriver-manager
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except:
                # استخدام chromedriver-autoinstaller
                import chromedriver_autoinstaller
                chromedriver_autoinstaller.install()
                self.driver = webdriver.Chrome(options=options)
            
            # إخفاء WebDriver من الاكتشاف
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تهيئة Chrome: {e}")
            return False
    
    def connect(self) -> bool:
        """الاتصال بواتساب ويب"""
        if not self.driver:
            if not self.initialize_driver():
                return False
        
        try:
            # فتح واتساب ويب
            self.driver.get("https://web.whatsapp.com")
            
            # الانتظار للتحميل
            time.sleep(5)
            
            # التحقق من حالة الاتصال
            self.is_connected = self.check_connection()
            
            if self.is_connected:
                print("✅ متصل بواتساب ويب")
            else:
                print("⏳ انتظار مسح رمز QR...")
                self.wait_for_qr_scan()
            
            return self.is_connected
            
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {e}")
            self.is_connected = False
            return False
    
    def check_connection(self) -> bool:
        """التحقق من حالة الاتصال"""
        if not self.driver:
            return False
        
        try:
            # التحقق من وجود عناصر تدل على الاتصال
            indicators = [
                'div[data-testid="chat-list"]',
                'div[aria-label="قائمة الدردشات"]',
                'div[aria-label="Chat list"]',
                'div[title="بحث"]',
                'div[title="Search"]',
            ]
            
            for indicator in indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        self.is_authenticated = True
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def wait_for_qr_scan(self, timeout: int = 120) -> bool:
        """انتظار مسح رمز QR"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            # انتظار ظهور رمز QR
            qr_element = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 'canvas[aria-label="Scan me!"]'
                ))
            )
            
            print("📱 يرجى مسح رمز QR من تطبيق واتساب على الهاتف")
            
            # انتظار اختفاء رمز QR (تم المسح)
            wait.until(
                EC.invisibility_of_element_located((
                    By.CSS_SELECTOR, 'canvas[aria-label="Scan me!"]'
                ))
            )
            
            self.is_connected = True
            self.is_authenticated = True
            print("✅ تم مسح رمز QR بنجاح!")
            
            # انتظار تحميل الواجهة
            time.sleep(3)
            
            return True
            
        except TimeoutException:
            print("⏰ انتهى وقت انتظار مسح رمز QR")
            return False
        except Exception as e:
            print(f"❌ خطأ في انتظار رمز QR: {e}")
            return False
    
    def open_chat(self, phone_number: str) -> bool:
        """فتح دردشة مع رقم هاتف"""
        try:
            # تنظيف رقم الهاتف
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            # فتح رابط الدردشة
            chat_url = f"https://web.whatsapp.com/send?phone={clean_phone}"
            self.driver.get(chat_url)
            
            # انتظار تحميل الدردشة
            time.sleep(5)
            
            # التحقق من فتح الدردشة
            if self.is_chat_opened():
                self.chat_opened = True
                print(f"✅ تم فتح الدردشة مع {clean_phone}")
                return True
            else:
                print(f"❌ تعذر فتح الدردشة مع {clean_phone}")
                return False
            
        except Exception as e:
            print(f"❌ خطأ في فتح الدردشة: {e}")
            return False
    
    def is_chat_opened(self) -> bool:
        """التحقق من فتح الدردشة"""
        try:
            # البحث عن عنصر إدخال الرسالة
            input_selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][data-tab="9"]',
                'footer div[contenteditable="true"]',
                'div[data-testid="conversation-compose-box-input"]',
            ]
            
            for selector in input_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed() and element.is_enabled():
                        return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def send_message(self, message: str) -> bool:
        """إرسال رسالة نصية"""
        try:
            # البحث عن مربع الرسائل
            input_box = None
            selectors = [
                'div[contenteditable="true"][data-tab="10"]',
                'div[contenteditable="true"][data-tab="9"]',
                'footer div[contenteditable="true"]',
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            input_box = element
                            break
                    if input_box:
                        break
                except:
                    continue
            
            if not input_box:
                print("❌ تعذر العثور على مربع الرسائل")
                return False
            
            # إدخال الرسالة
            input_box.click()
            input_box.clear()
            
            # تقسيم الرسالة الطويلة
            max_length = 1000
            if len(message) > max_length:
                parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
                for part in parts:
                    input_box.send_keys(part)
                    time.sleep(0.1)
            else:
                input_box.send_keys(message)
            
            time.sleep(0.5)
            
            # إرسال الرسالة
            input_box.send_keys(Keys.ENTER)
            time.sleep(1)
            
            print(f"✅ تم إرسال الرسالة ({len(message)} حرف)")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إرسال الرسالة: {e}")
            return False
    
    def send_image(self, image_path: str, caption: str = "") -> bool:
        """إرسال صورة"""
        try:
            import os
            import pyperclip
            import win32clipboard
            from io import BytesIO
            from PIL import Image
            
            # التحقق من وجود الصورة
            if not os.path.exists(image_path):
                print(f"❌ ملف الصورة غير موجود: {image_path}")
                return False
            
            # فتح مربع إرفاق الملفات
            try:
                attach_button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'div[data-testid="conversation-clip"]'
                )
                attach_button.click()
                time.sleep(1)
            except:
                # محاولة طريقة بديلة
                try:
                    attach_button = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'span[data-icon="clip"]'
                    )
                    attach_button.click()
                    time.sleep(1)
                except:
                    print("❌ تعذر العثور على زر الإرفاق")
                    return False
            
            # اختيار صورة
            try:
                image_input = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'input[accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
                )
                image_input.send_keys(image_path)
                time.sleep(2)
            except:
                print("❌ تعذر اختيار الصورة")
                return False
            
            # إضافة تعليق إذا كان موجوداً
            if caption:
                try:
                    caption_box = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'div[contenteditable="true"][data-tab="10"]'
                    )
                    caption_box.click()
                    caption_box.send_keys(caption)
                    time.sleep(0.5)
                except:
                    print("⚠️ تعذر إضافة تعليق للصورة")
            
            # إرسال الصورة
            try:
                send_button = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'span[data-icon="send"]'
                )
                send_button.click()
                time.sleep(2)
            except:
                # محاولة طريقة بديلة
                try:
                    send_button = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'div[aria-label="Send"]'
                    )
                    send_button.click()
                    time.sleep(2)
                except:
                    print("❌ تعذر إرسال الصورة")
                    return False
            
            print(f"✅ تم إرسال الصورة: {os.path.basename(image_path)}")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إرسال الصورة: {e}")
            return False
    
    def close(self):
        """إغلاق المتصفح"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.is_connected = False
                self.is_authenticated = False
                print("✅ تم إغلاق المتصفح")
        except Exception as e:
            print(f"⚠️ خطأ في إغلاق المتصفح: {e}")
    
    def restart(self) -> bool:
        """إعادة تشغيل المتصفح"""
        self.close()
        time.sleep(2)
        return self.initialize_driver() and self.connect()
    
    def take_screenshot(self, save_path: str = "screenshot.png") -> bool:
        """أخذ لقطة شاشة"""
        try:
            if self.driver:
                self.driver.save_screenshot(save_path)
                print(f"✅ تم حفظ لقطة الشاشة: {save_path}")
                return True
        except Exception as e:
            print(f"❌ خطأ في أخذ لقطة شاشة: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """الحصول على حالة الاتصال"""
        return {
            "connected": self.is_connected,
            "authenticated": self.is_authenticated,
            "chat_opened": self.chat_opened,
            "driver_active": self.driver is not None,
        }