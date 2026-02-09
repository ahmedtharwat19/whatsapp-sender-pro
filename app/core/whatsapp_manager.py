# app/core/whatsapp_manager.py
"""
مدير WhatsApp - للتحكم في فتح وإدارة WhatsApp Web
"""

import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import logging
import os
from pathlib import Path

class WhatsAppManager:
    def __init__(self, profile_path=None):
        """تهيئة مدير WhatsApp"""
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.profile_path = profile_path or str(Path.home() / "whatsapp_sender_profile")
        self.is_running = False
        
    def start_driver(self, headless=False):
        """بدء تشغيل المتصفح"""
        try:
            chrome_options = Options()
            
            # تجنب المشاكل الشائعة
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # إعدادات الملف الشخصي
            chrome_options.add_argument(f'--user-data-dir={self.profile_path}')
            chrome_options.add_argument('--profile-directory=Default')
            
            # إعدادات أخرى
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-notifications')
            
            if headless:
                chrome_options.add_argument('--headless')
            
            # استخدام undetected_chromedriver لتجنب الكشف
            self.driver = uc.Chrome(
                options=chrome_options,
                driver_executable_path=ChromeDriverManager().install()
            )
            
            # إخفاء علامات التشغيل الآلي
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.is_running = True
            self.logger.info("تم بدء تشغيل المتصفح بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في بدء تشغيل المتصفح: {e}")
            self.is_running = False
            return False
    
    def open_whatsapp_web(self):
        """فتح WhatsApp Web"""
        if not self.is_running or not self.driver:
            if not self.start_driver():
                return False
        
        try:
            self.driver.get("https://web.whatsapp.com")
            
            # الانتظار حتى يتم تحميل الصفحة
            wait = WebDriverWait(self.driver, 30)
            
            # محاولة اكتشاف حالة QR Code أو الدخول المباشر
            try:
                # التحقق إذا كان المستخدم مسجل الدخول بالفعل
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list']")))
                self.logger.info("تم تسجيل الدخول تلقائياً")
                return True
                
            except TimeoutException:
                # الانتظار لمسح QR Code
                qr_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[aria-label='Scan me!']")))
                self.logger.info("يرجى مسح رمز QR")
                
                # انتظار المستخدم لمسح QR Code
                for _ in range(180):  # انتظار لمدة 3 دقائق
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, "[data-testid='chat-list']")
                        self.logger.info("تم تسجيل الدخول بنجاح")
                        return True
                    except:
                        time.sleep(1)
                
                return False
                
        except Exception as e:
            self.logger.error(f"خطأ في فتح WhatsApp Web: {e}")
            return False
    
    def check_existing_session(self):
        """التحقق من وجود جلسة نشطة"""
        try:
            if self.driver:
                current_url = self.driver.current_url
                if "web.whatsapp.com" in current_url:
                    # التحقق من عناصر واجهة WhatsApp
                    elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='chat-list']")
                    return len(elements) > 0
            return False
        except:
            return False
    
    def send_message(self, phone_number, message, image_path=None):
        """إرسال رسالة إلى رقم هاتف"""
        try:
            if not self.check_existing_session():
                if not self.open_whatsapp_web():
                    return False
            
            # فتح دردشة جديدة
            chat_url = f"https://web.whatsapp.com/send?phone={phone_number}"
            self.driver.get(chat_url)
            
            # الانتظار حتى يتم فتح المحادثة
            wait = WebDriverWait(self.driver, 30)
            message_box = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[contenteditable='true']"))
            )
            
            time.sleep(2)  # تأخير قصير
            
            if image_path and os.path.exists(image_path):
                # رفع صورة
                attachment_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='attach-menu-plus']")
                attachment_button.click()
                
                time.sleep(1)
                
                # اختيار إرفاق صورة
                image_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept='image/*,video/mp4,video/3gpp,video/quicktime']")
                image_input.send_keys(image_path)
                
                # الانتظار حتى يتم تحميل الصورة
                time.sleep(3)
                
                # إضافة نص إلى الصورة (إذا كان هناك رسالة نصية)
                if message:
                    caption_box = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[contenteditable='true'][data-testid='media-caption-input-text']"))
                    )
                    caption_box.click()
                    caption_box.send_keys(message)
                
                # إرسال
                send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
                send_button.click()
                
            else:
                # إرسال رسالة نصية فقط
                message_box.click()
                message_box.send_keys(message)
                message_box.send_keys(Keys.ENTER)
            
            self.logger.info(f"تم إرسال الرسالة إلى {phone_number}")
            time.sleep(2)  # تأخير بين الرسائل
            return True
            
        except Exception as e:
            self.logger.error(f"خطأ في إرسال الرسالة: {e}")
            return False
    
    def close(self):
        """إغلاق المتصفح"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
        self.is_running = False