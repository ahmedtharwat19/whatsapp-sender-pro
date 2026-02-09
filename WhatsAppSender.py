import sys, os, subprocess, time, json, random, shutil, logging, threading, atexit
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps

# ================= AUTO INSTALL =================
REQUIRED = [
    "selenium","webdriver-manager","pyperclip",
    "pillow","psutil","PyQt6","pandas","openpyxl",
    "arabic-reshaper", "python-bidi",
    "requests","googletrans",
]

def ensure():
    for p in REQUIRED:
        try:
            # معالجة خاصة لكل مكتبة
            if p == "PyQt6":
                __import__("PyQt6.QtWidgets")
            elif p == "python-bidi":
                __import__("bidi")
            else:
                __import__(p)
        except:
            print(f"📦 جاري تثبيت {p}...")
            subprocess.check_call([sys.executable,"-m","pip","install",p])

ensure()

# ================= AUTO UPDATE =================
def check_and_update_packages():
    """فحص وتحديث المكتبات المطلوبة إذا كانت قديمة"""
    try:
        import logging as log_module
        logger = log_module.getLogger()
        logger.info("🔍 فحص تحديثات المكتبات...")
        
        packages_to_check = REQUIRED
        
        for package in packages_to_check:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "show", package],
                    capture_output=True, text=True, encoding='utf-8',
                    timeout=5
                )
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    installed_version = None
                    for line in lines:
                        if line.startswith('Version:'):
                            installed_version = line.split(':')[1].strip()
                            break
                    
                    if installed_version:
                        logger.info(f"📦 {package}: الإصدار {installed_version}")
                    else:
                        logger.info(f"📦 {package}: مثبت")
                else:
                    logger.info(f"📦 {package}: غير مثبت")
                    
            except Exception as e:
                logger.warning(f"⚠️ خطأ في فحص {package}: {e}")
        
        return True
            
    except Exception as e:
        print(f"❌ خطأ في فحص التحديثات: {e}")
        return False

check_and_update_packages()

# ================= IMPORTS =================
import psutil, pyperclip, pandas as pd
import urllib.request
from PIL import Image as PILImage

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QFont

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= PATHS =================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

CHROME_USER_DATA = os.path.join(HOME, "AppData", "Local", "Google", "Chrome", "User Data")
DEFAULT_PROFILE = os.path.join(CHROME_USER_DATA, "Default")
PROFILE_COPY_DIR = os.path.join(APP_DIR, "ChromeProfile")

LOG_DIR = os.path.join(APP_DIR, "WhatsAppSenderLogs")
FONTS_DIR = os.path.join(APP_DIR, "Fonts")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# ================= VERSION =================
VERSION = "4.2.2"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger()


# ================= ARABIC SUPPORT =================
ARABIC_SUPPORT = False

def setup_arabic_support():
    global ARABIC_SUPPORT, arabic_reshaper, get_display
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        ARABIC_SUPPORT = True
        log.info("✅ Arabic support enabled")
    except:
        ARABIC_SUPPORT = False
        log.warning("⚠️ Arabic reshaping not available")

setup_arabic_support()


# ================= TEXT PROCESSING FUNCTIONS =================
def is_arabic_text(text):
    """فحص إذا كان النص عربي"""
    if not text:
        return False
    return any('\u0600' <= char <= '\u06FF' for char in text)

def ensure_arabic_font():
    """تأكد من وجود خط عربي"""
    arabic_font_path = os.path.join(FONTS_DIR, "arabic.ttf")
    
    if not os.path.exists(arabic_font_path):
        log.info("📝 جاري تنزيل خط عربي افتراضي...")
        
        # محاولة تنزيل خط Vazir (خط عربي مجاني وشائع)
        try:
            font_url = "https://github.com/rastikerdar/vazir-font/releases/download/v33.0.3/Vazir.ttf"
            urllib.request.urlretrieve(font_url, arabic_font_path)
            log.info(f"✅ تم تنزيل خط عربي: Vazir")
        except Exception as e:
            log.warning(f"⚠️ تعذر تنزيل الخط العربي: {e}")
            
            # محاولة استخدام خطوط النظام
            system_fonts = [
                "C:\\Windows\\Fonts\\tahoma.ttf",
                "C:\\Windows\\Fonts\\arial.ttf",
                "C:\\Windows\\Fonts\\segoeui.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf"
            ]
            
            for font_path in system_fonts:
                if os.path.exists(font_path):
                    try:
                        shutil.copy(font_path, arabic_font_path)
                        log.info(f"✅ تم نسخ خط النظام: {os.path.basename(font_path)}")
                        break
                    except:
                        continue
    
    return arabic_font_path if os.path.exists(arabic_font_path) else None

def prepare_text_for_display(text, prefix="إلى:"):
    """تحضير النص للعرض مع البادئة المناسبة - الإصدار الجديد"""
    if not text:
        return prefix
    
    # تحديد ما إذا كان النص عربي
    text_is_arabic = is_arabic_text(text)
    
    if text_is_arabic:
        # للغة العربية: دمج البادئة والنص بشكل صحيح
        # لا تعكس الكلمات! هذه هي المشكلة
        full_text = f"{prefix} {text}"
        
        # تشكيل النص العربي بشكل صحيح
        if ARABIC_SUPPORT:
            try:
                reshaped_text = arabic_reshaper.reshape(full_text)
                return get_display(reshaped_text)
            except Exception as e:
                log.warning(f"⚠️ تعذر تشكيل النص العربي: {e}")
                return full_text
        return full_text
    else:
        # للإنجليزية: بادئة إنجليزية
        return f"To: {text}"

def prepare_message_for_sending(message, contact_name, phone, idx, is_arabic=False):
    """تحضير الرسالة النصية للإرسال - الإصدار الجديد"""
    if not message:
        return ""
    
    # # إذا لم يتم تحديد اللغة، نكتشفها تلقائياً
    # if not is_arabic:
    #     is_arabic = is_arabic_text(contact_name or message)
    
    # # استبدال المتغيرات
    message = message.replace('{phone}', str(phone))
    message = message.replace('{date}', datetime.now().strftime("%Y-%m-%d"))
    message = message.replace('{number}', str(idx + 1))
    
    # # استبدال الاسم
    name_replacement = contact_name if contact_name else ("عزيزي/عزيزتي" if is_arabic else "Dear")
    message = message.replace('{name}', name_replacement)
    
    # # إضافة تحية مناسبة إذا كان النص عربي
    # if is_arabic:
    #     # تحقق إذا كانت الرسالة تبدأ بتحية
    #     greetings = ["مرحباً", "أهلاً", "سلام", "تحية", "السلام عليكم"]
    #     if not any(message.strip().startswith(g) for g in greetings):
    #         if contact_name:
    #             message = f"مرحباً {contact_name}\n{message}"
    #         else:
    #             message = f"مرحباً\n{message}"
    
    # # تشكيل النص العربي إذا كان مدعوماً
    # if is_arabic and ARABIC_SUPPORT:
    #     try:
    #         reshaped = arabic_reshaper.reshape(message)
    #         return get_display(reshaped)
    #     except Exception as e:
    #         log.warning(f"⚠️ تعذر تشكيل النص العربي: {e}")
    #         return message
    
    return message

# ================= IMAGE TEXT SETTINGS =================
TEXT_COLOR = (255, 215, 0)  # ذهبي افتراضي
TEXT_SIZE = 50

def add_text_to_image(image_path, text, output_path=None, text_color=None, text_size=None, add_background=False, add_frame=False):
    """إضافة نص إلى الصورة مع دعم اللغة العربية وإطار دائري للاسم"""
    try:
        if not output_path:
            output_path = os.path.join(APP_DIR, f"temp_image_with_text_{int(time.time())}.jpg")
        
        color = text_color if text_color else TEXT_COLOR
        size = text_size if text_size else TEXT_SIZE
        
        # فتح الصورة
        img = PILImage.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        
        # تحضير النص للعرض (سيتم معالجة "إلى:" مع النص)
        display_text = prepare_text_for_display(text)
        
        # تحديد الخط المناسب
        font = None
        arabic_font_path = ensure_arabic_font()
        
        if is_arabic_text(display_text) and arabic_font_path:
            try:
                font = ImageFont.truetype(arabic_font_path, size)
                log.info("✅ استخدام الخط العربي للنص")
            except Exception as e:
                log.warning(f"⚠️ تعذر تحميل الخط العربي: {e}")
                # محاولة خطوط النظام
                system_fonts = [
                    "C:\\Windows\\Fonts\\tahoma.ttf",
                    "C:\\Windows\\Fonts\\arial.ttf",
                    "C:\\Windows\\Fonts\\segoeui.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/System/Library/Fonts/Supplemental/Arial.ttf"
                ]
                
                for font_path in system_fonts:
                    if os.path.exists(font_path):
                        try:
                            font = ImageFont.truetype(font_path, size)
                            log.info(f"✅ استخدام خط النظام: {os.path.basename(font_path)}")
                            break
                        except:
                            continue
                
                if not font:
                    font = ImageFont.load_default()
        else:
            # استخدام خط عادي للنص الإنجليزي
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", size)
                except:
                    font = ImageFont.load_default()
        
        # حساب حجم النص
        text_bbox = draw.textbbox((0, 0), display_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        img_width, img_height = img.size
        
        # ضبط حجم الخط ليناسب الصورة
        max_width = img_width * 0.8
        while text_width > max_width and size > 20:
            size = int(size * 0.9)
            try:
                if hasattr(font, 'path'):
                    font = ImageFont.truetype(font.path, size)
                else:
                    font = ImageFont.load_default()
                text_bbox = draw.textbbox((0, 0), display_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            except:
                break
        
        # حساب موضع النص - أعلى الوسط
        x = (img_width - text_width) // 2
        y = 30
        
        # إضافة إطار دائري للنص إذا طلب
        if add_frame:
            frame_padding = 20
            frame_radius = 15
            
            # إنشاء طبقة شفافية مؤقتة
            temp_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            frame_draw = ImageDraw.Draw(temp_layer)
            
            # حساب موضع الإطار
            frame_box = [
                x - frame_padding,
                y - frame_padding,
                x + text_width + frame_padding,
                y + text_height + frame_padding
            ]
            
            # رسم إطار فقط (بدون تعبئة) بنفس لون النص
            frame_draw.rounded_rectangle(
                frame_box,
                radius=frame_radius,
                outline=color + (255,),  # نفس لون النص مع شفافية كاملة
                width=3  # سمك الإطار
            )
            
            # دمج الإطار مع الصورة الأصلية
            img = Image.alpha_composite(img, temp_layer)
            draw = ImageDraw.Draw(img)
        
        # إضافة ظل للنص
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), display_text, 
                 font=font, fill=(0, 0, 0, 100))
        
        # إضافة النص الرئيسي
        draw.text((x, y), display_text, font=font, fill=color)
        
        # حفظ الصورة
        img = img.convert("RGB")
        img.save(output_path, quality=95)
        
        log.info(f"📝 تم إضافة النص '{display_text[:30]}...' إلى الصورة")
        return output_path
        
    except Exception as e:
        log.error(f"❌ فشل إضافة النص إلى الصورة: {e}")
        return image_path

# ================= CHROME PROFILE MANAGEMENT =================
def copy_chrome_profile():
    """نسخ ملف Chrome الشخصي الحالي"""
    try:
        log.info(f"📂 جاري نسخ ملف Chrome الشخصي من: {DEFAULT_PROFILE}")
        
        if os.path.exists(PROFILE_COPY_DIR):
            log.info("🗑️ حذف النسخة القديمة من ملف الشخصي...")
            shutil.rmtree(PROFILE_COPY_DIR, ignore_errors=True)
        
        os.makedirs(PROFILE_COPY_DIR, exist_ok=True)
        
        files_copied = 0
        skip_files = [
            "Cache", "Cache_Data", "Code Cache", "GPUCache",
            "JumpListIcons", "JumpListIconsOld", "Local Storage",
            "Session Storage", "TransportSecurity", "History",
            "Visited Links", "Top Sites", "Shortcuts", "Favicons"
        ]
        
        if not os.path.exists(DEFAULT_PROFILE):
            log.warning(f"⚠️ لم يتم العثور على ملف الشخصي الأصلي: {DEFAULT_PROFILE}")
            return False
        
        for item in os.listdir(DEFAULT_PROFILE):
            src_path = os.path.join(DEFAULT_PROFILE, item)
            dst_path = os.path.join(PROFILE_COPY_DIR, item)
            
            if any(skip in item for skip in skip_files):
                continue
                
            try:
                if os.path.isdir(src_path):
                    if item in ["Cookies", "Extensions", "Local Extension Settings", 
                               "Sync Data", "Web Applications", "Local State"]:
                        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                        files_copied += 1
                else:
                    if item.endswith((".db", ".dat", ".json", ".txt", "Local State")):
                        shutil.copy2(src_path, dst_path)
                        files_copied += 1
                        
            except Exception as e:
                log.warning(f"⚠️ تعذر نسخ {item}: {e}")
        
        log.info(f"✅ تم نسخ {files_copied} ملف/مجلد من ملف الشخصي")
        return True
        
    except Exception as e:
        log.error(f"❌ فشل نسخ ملف الشخصي: {e}")
        return False

def get_chrome_debug_port():
    """الحصول على منفذ تصحيح Chrome المفتوح"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline:
                        for arg in cmdline:
                            if '--remote-debugging-port' in arg:
                                port = arg.split('=')[1]
                                log.info(f"🔌 وجد Chrome مع منفذ تصحيح: {port}")
                                return int(port)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        log.warning(f"⚠️ خطأ في البحث عن منفذ تصحيح: {e}")
    
    return None

def check_chrome_for_whatsapp():
    """فحص ما إذا كان Chrome مفتوحًا وفيه WhatsApp"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def wait_for_whatsapp_login(driver, timeout=120):
    """الانتظار حتى دخول واتساب"""
    log.info("⏳ جاري الانتظار للدخول إلى واتساب...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < timeout:
        try:
            # فحص عناصر واتساب المسجل دخول
            logged_in_selectors = [
                "//div[@id='side']",
                "//div[@id='pane-side']",
                "//div[contains(@class, 'chat-list')]",
                "//div[@contenteditable='true'][@data-tab='10']",
                "//div[contains(@class, 'app-wrapper')]",
                "//div[contains(@class, '_1qB8f')]",
            ]
            
            for selector in logged_in_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        for element in elements:
                            if element.is_displayed():
                                if last_status != "green":
                                    log.info("🟢 تم العثور على عناصر واتساب - تم الدخول بنجاح!")
                                    last_status = "green"
                                time.sleep(3)
                                return True
                except:
                    continue
            
            # فحص صفحة QR Code
            try:
                current_url = driver.current_url
                if "web.whatsapp.com" in current_url:
                    page_source = driver.page_source.lower()
                    if any(keyword in page_source for keyword in ['qr', 'code', 'مسح', 'تسجيل الدخول', 'دخول']):
                        if last_status != "red":
                            log.info("🔴 في صفحة QR Code - انتظر مسح الرمز")
                            last_status = "red"
                    else:
                        if last_status != "green":
                            log.info("🟢 يبدو أنك مسجل الدخول بالفعل")
                            last_status = "green"
                        return True
            except:
                pass
            
            # تحديث حالة الانتظار
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                log.info(f"⏳ لا يزال في انتظار الدخول... ({elapsed} ثانية)")
            
            time.sleep(2)
            
        except Exception as e:
            log.warning(f"⚠️ خطأ في فحص حالة الدخول: {e}")
            time.sleep(2)
    
    log.warning("⚠️ انتهى وقت الانتظار ولم يتم تأكيد الدخول")
    return False

def connect_to_existing_chrome():
    """الاتصال بـ Chrome مفتوح بالفعل"""
    try:
        log.info("🔗 محاولة الاتصال بـ Chrome المفتوح بالفعل...")
        
        debug_port = get_chrome_debug_port()
        
        if debug_port:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                log.info(f"✅ تم الاتصال بـ Chrome المفتوح على منفذ {debug_port}!")
                
                # التحقق من وجود واتساب
                current_url = driver.current_url
                if "web.whatsapp.com" not in current_url:
                    log.info("🌐 جاري فتح واتساب ويب...")
                    driver.get("https://web.whatsapp.com")
                    time.sleep(5)
                
                return driver
            except Exception as e:
                log.warning(f"⚠️ لم أتمكن من الاتصال بـ Chrome المفتوح: {e}")
        
        return None
        
    except Exception as e:
        log.error(f"❌ فشل الاتصال بـ Chrome: {e}")
        return None

def start_chrome_with_profile_copy():
    """فتح Chrome جديد مع نسخة من الملف الشخصي الحالي"""
    log.info("🚀 فتح Chrome مع نسخة من الملف الشخصي الحالي...")
    
    # استخدام مجلد ثابت للملف الشخصي بدلاً من نسخه في كل مرة
    profile_dir = os.path.join(APP_DIR, "WhatsAppProfile")
    
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir, exist_ok=True)
        log.info(f"📁 تم إنشاء مجلد الملف الشخصي في: {profile_dir}")
    
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={profile_dir}")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--remote-debugging-port=9223")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        log.info("✅ تم فتح Chrome بنجاح مع الملف الشخصي الدائم!")
        return driver
        
    except Exception as e:
        log.error(f"❌ فشل فتح Chrome: {e}")
        raise

def validate_phone_number(phone):
    """التحقق من صحة رقم الهاتف"""
    if not phone or not isinstance(phone, str):
        return False
    
    cleaned = ''.join(filter(str.isdigit, phone))
    
    if len(cleaned) < 8 or len(cleaned) > 15:
        return False
    
    return cleaned

def start_whatsapp_driver(existing_driver=None):
    """تشغيل أو الاتصال بـ Chrome - الإصدار المعدل"""
    try:
        # إذا كان هناك driver مفتوح بالفعل، استخدمه
        if existing_driver:
            log.info("🔗 استخدام المتصفح المفتوح بالفعل...")
            
            # التحقق من أن Driver لا يزال نشطًا
            try:
                # محاولة الوصول إلى صفحة بسيطة للتحقق
                existing_driver.current_url
                log.info("✅ المتصفح المفتوح لا يزال نشطًا")
                return existing_driver, True
            except:
                log.warning("⚠️ المتصفح المفتوح لم يعد نشطًا")
                existing_driver = None
        
        # محاولة الاتصال بـ Chrome مفتوح
        if not existing_driver:
            driver = connect_to_existing_chrome()
            if driver:
                log.info("🌐 جاري التحقق من حالة واتساب...")
                logged_in = wait_for_whatsapp_login(driver, timeout=30)
                if logged_in:
                    log.info("✅ تم الدخول إلى واتساب بنجاح!")
                    return driver, True
                else:
                    log.info("⚠️ لم يتم تأكيد الدخول، استمرار مع هذا المتصفح")
                    return driver, False
        
        # إذا لم نتمكن من الاتصال بـ Chrome مفتوح، افتح جديد
        log.info("🔄 فتح Chrome جديد مع الملف الشخصي الدائم...")
        driver = start_chrome_with_profile_copy()
        
        log.info("🌐 جاري فتح واتساب ويب...")
        driver.get("https://web.whatsapp.com")
        
        time.sleep(5)
        
        logged_in = wait_for_whatsapp_login(driver)
        if logged_in:
            log.info("✅ تم الدخول إلى واتساب بنجاح!")
            return driver, True
        else:
            log.warning("⚠️ قد لا يكون المستخدم مسجل الدخول بعد")
            return driver, False
        
    except Exception as e:
        log.error(f"❌ فشل تشغيل Chrome: {e}")
        raise

def open_whatsapp_only():
    """فتح واتساب فقط - باستخدام الملف الشخصي الدائم"""
    try:
        log.info("🌐 جاري فتح واتساب ويب...")
        
        # استخدام الملف الشخصي الدائم
        profile_dir = os.path.join(APP_DIR, "WhatsAppProfile")
        
        if os.path.exists(profile_dir):
            log.info(f"📁 استخدام الملف الشخصي الدائم: {profile_dir}")
        else:
            os.makedirs(profile_dir, exist_ok=True)
            log.info(f"📁 تم إنشاء مجلد الملف الشخصي الجديد")
        
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--log-level=3")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # فتح واتساب
        driver.get("https://web.whatsapp.com")
        log.info("✅ تم فتح واتساب ويب بنجاح!")
        
        return driver
        
    except Exception as e:
        log.error(f"❌ فشل فتح واتساب: {e}")
        return None

def send_image(driver, path, recipient_name="", text_color=None, text_size=None, add_background=False, add_frame=False):
    """إرسال صورة عبر WhatsApp مع إمكانية إضافة النص"""
    try:
        import win32clipboard
        
        image_to_send = path
        if recipient_name and os.path.exists(path):
            temp_image = os.path.join(APP_DIR, f"temp_{int(time.time())}_{os.path.basename(path)}")
            image_to_send = add_text_to_image(path, recipient_name, temp_image, text_color, text_size, add_background, add_frame)
        
        log.info(f"🖼️ جاري إرسال الصورة: {os.path.basename(image_to_send)}")
        
        img = PILImage.open(image_to_send)
        output = BytesIO()
        img.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

        input_box = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )
        
        input_box.click()
        input_box.send_keys(Keys.CONTROL, "v")
        time.sleep(3)
        
        log.info("🔍 البحث عن زر إرسال الصورة...")
        
        send_selectors = [
            "//*[@id='app']/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/span/div/div/span",
            "//span[@data-icon='send']",
            "//span[@data-icon='send']",
            "//span[@data-testid='send']",
            "//button[@aria-label='Send']",
            "//div[@role='button'][@title='Send']"
        ]
        
        send_button = None
        for selector in send_selectors:
            try:
                send_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if send_button and send_button.is_displayed():
                    break
            except:
                continue
        
        if send_button:
            send_button.click()
            time.sleep(2)
            log.info("✅ تم إرسال الصورة بنجاح!")
            
            # تنظيف الصورة المؤقتة
            if image_to_send != path and os.path.exists(image_to_send):
                try:
                    os.remove(image_to_send)
                except:
                    pass
            
            return True
        else:
            log.error("❌ لم يتم العثور على زر إرسال الصورة")
            return False
        
    except Exception as e:
        log.error(f"❌ فشل إرسال الصورة: {e}")
        return False

def extract_contact_name_from_whatsapp(driver, phone):
    """استخراج اسم الجهة من WhatsApp"""
    try:
        driver.get(f"https://web.whatsapp.com/send?phone={phone}")
        time.sleep(3)
        
        name_selectors = [
            "//header//span[@dir='auto']",
            "//span[@data-testid='conversation-info-header-chat-title']",
            "//header//span[contains(@class, 'chat-title')]",
            "//header//div[contains(@class, 'chat-title')]",
        ]
        
        for selector in name_selectors:
            try:
                name_element = driver.find_elements(By.XPATH, selector)
                if name_element:
                    name = name_element[0].text.strip()
                    if name and name != phone:
                        log.info(f"👤 تم العثور على الاسم في WhatsApp: {name}")
                        return name
            except:
                continue
        
        log.info(f"⚠️ لم يتم العثور على اسم للرقم {phone} في WhatsApp")
        return None
        
    except Exception as e:
        log.error(f"❌ خطأ في استخراج الاسم: {e}")
        return None

# ================= WHATSAPP STATUS MONITOR =================
class WhatsAppStatusMonitor(QThread):
    """مراقبة حالة واتساب"""
    status_changed = pyqtSignal(str, str)  # حالة, لون
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.driver = None
        
    def stop(self):
        """إيقاف المراقبة"""
        self.running = False
        
    def check_whatsapp_status(self):
        """فحص حالة واتساب"""
        try:
            if self.driver:
                try:
                    current_url = self.driver.current_url
                    if "web.whatsapp.com" in current_url:
                        try:
                            # فحص عناصر واتساب النشطة
                            active_selectors = [
                                "//div[@contenteditable='true'][@data-tab='10']",
                                "//div[@id='side']",
                                "//div[@id='pane-side']"
                            ]
                            
                            for selector in active_selectors:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                if elements and any(e.is_displayed() for e in elements):
                                    return "✅ واتساب نشط وجاهز", "green"
                            
                            # فحص صفحة QR Code
                            page_source = self.driver.page_source.lower()
                            if any(keyword in page_source for keyword in ['qr', 'code', 'مسح']):
                                return "🔴 امسح رمز QR", "red"
                            
                            return "🟡 جاري التحميل...", "yellow"
                        except:
                            return "🟡 جاري الاتصال...", "yellow"
                except:
                    # المتصفح مغلق
                    self.driver = None
                    return "⚪ غير متصل", "gray"
            return "⚪ غير متصل", "gray"
        except:
            return "⚪ غير متصل", "gray"
    
    def run(self):
        """تشغيل المراقبة"""
        while self.running:
            status, color = self.check_whatsapp_status()
            self.status_changed.emit(status, color)
            time.sleep(2)

# ================= SENDING THREAD CLASS =================
class SendingThread(QThread):
    """Thread منفصل للإرسال"""
    progress_update = pyqtSignal(int, int, int, int, int)  # إرسال, ناجح, فاشل, غير صالح, مؤشر
    log_message = pyqtSignal(str)
    status_update = pyqtSignal(str, str)  # حالة, لون
    finished_sending = pyqtSignal()
    error_occurred = pyqtSignal(str)
    require_login_confirmation = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_running = True
        
    def stop(self):
        """إوقف thread الإرسال"""
        self.is_running = False
        
    def run(self):
        """تنفيذ عملية الإرسال"""
        try:
            self.status_update.emit("🔧 جاري الإعداد...", "yellow")
            
            if self.parent.delay_seconds > 0:
                self.log_message.emit(f"⏳ انتظار {self.parent.delay_seconds//60} دقيقة...")
                for i in range(self.parent.delay_seconds, 0, -1):
                    if not self.is_running:
                        return
                    if i % 30 == 0:
                        self.log_message.emit(f"⏳ متبقي {i//60} دقيقة...")
                    time.sleep(1)
            
            self.log_message.emit(f"🚀 جاري تشغيل المتصفح...")
            self.status_update.emit("🌐 جاري تشغيل المتصفح...", "yellow")
            
            try:
                # استخدام المتصفح المفتوح إذا كان موجودًا
                existing_driver = self.parent.driver
                self.parent.driver, logged_in = start_whatsapp_driver(existing_driver)
                
                if not logged_in:
                    self.log_message.emit("⚠️ يبدو أنك لست مسجل الدخول إلى واتساب")
                    self.status_update.emit("🔴 انتظر الدخول إلى واتساب", "red")
                    
                    # انتظار المستخدم لمسح QR Code
                    self.require_login_confirmation.emit()
                    
                    if not self.is_running:
                        return
                    
                    # إعادة الانتظار للدخول
                    logged_in = wait_for_whatsapp_login(self.parent.driver, timeout=60)
                    if not logged_in:
                        self.log_message.emit("❌ لم يتم الدخول إلى واتساب")
                        return
                    
                self.log_message.emit("✅ تم الدخول إلى واتساب بنجاح!")
                self.status_update.emit("✅ واتساب نشط وجاهز", "green")
                
            except Exception as e:
                self.log_message.emit(f"❌ فشل تشغيل المتصفح: {e}")
                self.status_update.emit("❌ خطأ في المتصفح", "red")
                self.error_occurred.emit(str(e))
                return
            
            # حلقة الإرسال الرئيسية
            total_contacts = len(self.parent.contacts)
            successful_contacts = []
            failed_contacts = []
            
            for idx, contact in enumerate(self.parent.contacts):
                if not self.is_running:
                    break
                
                try:
                    phone = contact.get('validated_phone', '')
                    if not phone:
                        failed_contacts.append({'phone': 'غير معروف', 'error': 'رقم غير صالح'})
                        self.update_progress(idx + 1, successful_contacts, failed_contacts)
                        continue
                    
                    self.log_message.emit(f"📱 جاري الإرسال إلى {phone} ({idx+1}/{total_contacts})")
                    self.status_update.emit(f"📤 جاري الإرسال ({idx+1}/{total_contacts})", "yellow")
                    
                    # فتح الدردشة
                    self.parent.driver.get(f"https://web.whatsapp.com/send?phone={phone}")
                    time.sleep(5)
                    
                    try:
                        input_box = WebDriverWait(self.parent.driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, 
                                "//div[@contenteditable='true'][@data-tab='10']"))
                        )
                    except:
                        try:
                            time.sleep(3)
                            input_box = self.parent.driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                        except:
                            self.log_message.emit(f"❌ الرقم {phone} قد يكون غير موجود في WhatsApp")
                            failed_contacts.append({'phone': phone, 'error': 'الرقم غير موجود أو مشكلة في الاتصال'})
                            self.update_progress(idx + 1, successful_contacts, failed_contacts)
                            continue
                    
                    # استخراج أو تحديد اسم الجهة
                    contact_name = contact.get('contact_name', '')
                    
                    if self.parent.extract_names_from_whatsapp and not contact_name:
                        try:
                            whatsapp_name = extract_contact_name_from_whatsapp(self.parent.driver, phone)
                            if whatsapp_name:
                                contact_name = whatsapp_name
                                self.log_message.emit(f"👤 تم استخراج الاسم من WhatsApp: {contact_name}")
                        except:
                            pass
                    
                    # تحديد إذا كان الاسم عربي
                    is_arabic_name = is_arabic_text(contact_name) if contact_name else False
                    
                    # إرسال الرسالة النصية
                    try:
                        # استخدام الرسالة الواحدة مع اللغة المناسبة
                        message = self.parent.message_input.toPlainText()
                        
                        if message.strip():
                            # تحضير الرسالة
                            final_message = prepare_message_for_sending(
                                message, contact_name, phone, idx, is_arabic_name
                            )
                            
                            pyperclip.copy(final_message)
                            input_box.click()
                            input_box.send_keys(Keys.CONTROL, "v")
                            time.sleep(1)
                            input_box.send_keys(Keys.ENTER)
                            self.log_message.emit(f"📨 تم إرسال الرسالة")
                        
                    except Exception as e:
                        self.log_message.emit(f"⚠️ تعذر إرسال الرسالة: {str(e)[:50]}")
                    
                    # إرسال الصورة
                    if self.parent.image_path and os.path.exists(self.parent.image_path):
                        time.sleep(2)
                        if self.parent.add_name_to_image and contact_name:
                            self.log_message.emit(f"📝 جاري كتابة الاسم '{contact_name}' على الصورة...")
                        
                        if send_image(self.parent.driver, self.parent.image_path, 
                                    contact_name if self.parent.add_name_to_image else "",
                                    self.parent.text_color, self.parent.text_size, 
                                    self.parent.add_background, self.parent.add_frame):
                            self.log_message.emit(f"🖼️ تم إرسال الصورة")
                        else:
                            self.log_message.emit(f"⚠️ فشل إرسال الصورة")
                    
                    successful_contacts.append({'phone': phone, 'name': contact_name})
                    self.log_message.emit(f"✅ تم الإرسال بنجاح")
                    
                except Exception as e:
                    self.log_message.emit(f"❌ خطأ في الإرسال: {str(e)[:100]}")
                    failed_contacts.append({'phone': phone if 'phone' in locals() else 'غير معروف', 'error': str(e)[:100]})
                
                # تحديث التقدم
                self.update_progress(idx + 1, successful_contacts, failed_contacts)
                
                # تأخير بين الرسائل
                if idx < total_contacts - 1 and self.is_running:
                    delay = random.randint(15, 30)
                    self.log_message.emit(f"⏳ انتظار {delay} ثانية...")
                    
                    for sec in range(delay):
                        if not self.is_running:
                            break
                        time.sleep(1)
            
            # إنهاء العملية - لا نغلق المتصفح!
            self.update_progress(total_contacts, successful_contacts, failed_contacts)
            
            # حفظ النتائج
            self.parent.successful_contacts = successful_contacts
            self.parent.failed_contacts = failed_contacts
            self.parent.current_index = total_contacts
            
            result = f"🎉 اكتمل الإرسال! ناجح: {len(successful_contacts)}, فاشل: {len(failed_contacts)}"
            self.log_message.emit(result)
            self.status_update.emit("🎉 اكتمل الإرسال", "green")
            self.progress_update.emit(total_contacts, len(successful_contacts), len(failed_contacts), 
                                    len(self.parent.invalid_contacts), 100)
            
            self.finished_sending.emit()
            
        except Exception as e:
            self.log_message.emit(f"❌ خطأ غير متوقع: {str(e)[:200]}")
            self.status_update.emit("❌ خطأ في الإرسال", "red")
            self.error_occurred.emit(str(e))
    
    def update_progress(self, processed, successful, failed):
        """تحديث التقدم"""
        self.progress_update.emit(
            processed,
            len(successful),
            len(failed),
            len(self.parent.invalid_contacts),
            int((processed / len(self.parent.contacts)) * 100) if self.parent.contacts else 0
        )

# ================= MAIN GUI APPLICATION =================
class WhatsAppSenderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"WhatsApp Bulk Sender - النسخة الذكية v{VERSION}")
        self.setMinimumSize(1000, 700)
        
        # تهيئة المتغيرات
        self.is_running = False
        self.contacts = []
        self.image_path = None
        self.driver = None
        self.delay_seconds = 0
        self.current_index = 0
        
        self.extract_names_from_whatsapp = True
        self.add_name_to_image = False
        
        self.text_color = (255, 215, 0)  # ذهبي
        self.text_size = 50
        self.add_background = False
        self.add_frame = True  # إضافة إطار دائري افتراضي
        
        self.successful_contacts = []
        self.failed_contacts = []
        self.invalid_contacts = []
        
        self.log_queue = []
        self.log_timer = None
        
        self.sending_worker = None
        self.status_monitor = None
        
        self.setup_ui()
        self.log(f"🚀 تطبيق WhatsApp Sender v{VERSION} جاهز للاستخدام")
        
        # بدء مراقبة الحالة
        self.start_status_monitor()
        
    def setup_ui(self):
        """تهيئة واجهة المستخدم مع Scroll Area"""
        # إنشاء الـ Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout رئيسي
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ====== الجزء العلوي (ثابت لا يتحرك) ======
        top_widget = QWidget()
        top_widget.setMaximumHeight(180)
        top_layout = QVBoxLayout(top_widget)
        
        # العنوان
        title = QLabel(f"📱 WhatsApp Bulk Sender - النسخة الذكية v{VERSION}")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #25D366;
            padding: 15px;
            background: white;
            border-radius: 10px;
            qproperty-alignment: AlignCenter;
            border: 2px solid #25D366;
        """)
        top_layout.addWidget(title)
        
        # شريط الحالة مع زر فتح واتساب
        status_bar = QWidget()
        status_layout = QHBoxLayout(status_bar)
        
        self.whatsapp_status = QLabel("⚪ غير متصل")
        self.whatsapp_status.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 2px solid #6c757d;
            min-width: 200px;
            color: black;
        """)
        
        # زر فتح واتساب
        self.open_whatsapp_btn = QPushButton("🌐 فتح واتساب")
        self.open_whatsapp_btn.clicked.connect(self.open_whatsapp)
        self.open_whatsapp_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 10px 25px;
                background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
                color: black;
                border-radius: 8px;
                border: 2px solid #25D366;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #128C7E 0%, #075E54 100%);
            }
            QPushButton:pressed {
                background: #075E54;
            }
        """)
        
        status_layout.addWidget(self.whatsapp_status)
        status_layout.addWidget(self.open_whatsapp_btn)
        status_layout.addStretch()
        
        top_layout.addWidget(status_bar)
        
        main_layout.addWidget(top_widget)
        
        # ====== الجزء الرئيسي (قابل للتمرير) ======
        # إنشاء Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # إنشاء Widget للـ Scroll Area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        
        self.tab_widget = QTabWidget()
        
        # تبويب الإعدادات الأساسية
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setSpacing(10)
        
        # رسالة واحدة بدلاً من رسالتين
        messages_group = QGroupBox("✉️ الرسالة")
        messages_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                color: black;
            }
            QGroupBox::title {
                color: black;
            }
        """)
        messages_layout = QVBoxLayout(messages_group)
        
        # رسالة واحدة فقط
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("اكتب الرسالة هنا...\nاستخدم {name} لاسم الجهة\nمثال: عيد ميلاد سعيد {name}!")
        self.message_input.setMaximumHeight(150)
        self.message_input.setStyleSheet("""
            color: black;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        """)
        messages_layout.addWidget(self.message_input)
        
        # ملاحظة
        note_label = QLabel("💡 ملاحظة: اكتب الرسالة بلغتك المفضلة. سيتم استخدامها كما هي.")
        note_label.setStyleSheet("""
            color: #6c757d;
            font-size: 12px;
            padding: 5px;
            font-style: italic;
        """)
        messages_layout.addWidget(note_label)
        
        settings_layout.addWidget(messages_group)
        
        # إعدادات الأسماء
        name_group = QGroupBox("👤 إعدادات الأسماء")
        name_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                color: black;
            }
            QGroupBox::title {
                color: black;
            }
        """)
        name_layout = QVBoxLayout(name_group)
        
        self.extract_names_check = QCheckBox("استخراج الأسماء من WhatsApp تلقائيًا")
        self.extract_names_check.setChecked(True)
        self.extract_names_check.setStyleSheet("color: black;")
        name_layout.addWidget(self.extract_names_check)
        
        self.add_name_to_image_check = QCheckBox("كتابة اسم المرسل إليه على الصورة")
        self.add_name_to_image_check.setChecked(False)
        self.add_name_to_image_check.setStyleSheet("color: black;")
        name_layout.addWidget(self.add_name_to_image_check)
        
        settings_layout.addWidget(name_group)
        
        # إعدادات الخط على الصورة
        font_group = QGroupBox("🎨 إعدادات الخط على الصورة")
        font_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                color: black;
            }
            QGroupBox::title {
                color: black;
            }
        """)
        font_layout = QVBoxLayout(font_group)
        
        # حجم الخط
        font_size_widget = QWidget()
        font_size_layout = QHBoxLayout(font_size_widget)
        size_label = QLabel("حجم الخط:")
        size_label.setStyleSheet("color: black;")
        font_size_layout.addWidget(size_label)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(20, 100)
        self.font_size_spin.setValue(50)
        self.font_size_spin.setSuffix(" بكسل")
        self.font_size_spin.valueChanged.connect(self.update_font_size)
        self.font_size_spin.setStyleSheet("color: black;")
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        
        font_layout.addWidget(font_size_widget)
        
        # ألوان الخط
        color_label = QLabel("لون الخط:")
        color_label.setStyleSheet("color: black;")
        font_layout.addWidget(color_label)
        
        color_buttons_widget = QWidget()
        color_buttons_layout = QHBoxLayout(color_buttons_widget)
        
        colors = [
            ("ذهبي", (255, 215, 0), "#ffd700"),
            ("أبيض", (255, 255, 255), "#ffffff"),
            ("أحمر", (255, 0, 0), "#ff0000"),
            ("أزرق", (0, 0, 255), "#0000ff"),
            ("أخضر", (0, 255, 0), "#00ff00"),
            ("أسود", (0, 0, 0), "#000000"),
            ("فضي", (192, 192, 192), "#c0c0c0")
        ]
        
        for color_name, color_rgb, hex_code in colors:
            btn = QPushButton(color_name)
            btn.setFixedHeight(35)
            # تحديد لون النص بناءً على لون الخلفية
            text_color = "black" if sum(color_rgb) > 400 else "white"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_code};
                    color: {text_color};
                    border-radius: 5px;
                    font-weight: bold;
                    border: 2px solid #ddd;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    border: 2px solid #007bff;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color_rgb: self.update_text_color(c))
            color_buttons_layout.addWidget(btn)
        
        font_layout.addWidget(color_buttons_widget)
        
        # لون مخصص
        self.custom_color_btn = QPushButton("🎨 اختيار لون مخصص")
        self.custom_color_btn.clicked.connect(self.choose_custom_color)
        self.custom_color_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                border: none;
                margin-top: 5px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }
        """)
        font_layout.addWidget(self.custom_color_btn)
        
        # عرض اللون الحالي
        self.current_color_label = QLabel("اللون الحالي: ذهبي")
        self.current_color_label.setStyleSheet("""
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
            font-weight: bold;
            border: 1px solid #dee2e6;
            margin-top: 5px;
            color: black;
        """)
        font_layout.addWidget(self.current_color_label)
        
        # خيارات إضافية للنص على الصورة
        text_options_widget = QWidget()
        text_options_layout = QVBoxLayout(text_options_widget)
        
        # خيار الإطار الدائري
        self.add_frame_check = QCheckBox("📦 إضافة برواز دائري للاسم (مستدير الحواف)")
        self.add_frame_check.setChecked(True)
        self.add_frame_check.stateChanged.connect(self.toggle_text_frame)
        self.add_frame_check.setStyleSheet("color: black;")
        text_options_layout.addWidget(self.add_frame_check)
        
        font_layout.addWidget(text_options_widget)
        
        settings_layout.addWidget(font_group)
        
        # الصورة
        img_group = QGroupBox("🖼️ الصورة (اختياري)")
        img_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                color: black;
            }
            QGroupBox::title {
                color: black;
            }
        """)
        img_layout = QVBoxLayout(img_group)
        
        self.img_info = QLabel("لم يتم اختيار صورة")
        self.img_info.setStyleSheet("""
            padding: 15px;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            color: #6c757d;
            font-size: 14px;
        """)
        self.img_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        img_btn_widget = QWidget()
        img_btn_layout = QHBoxLayout(img_btn_widget)
        
        self.select_img_btn = QPushButton("📁 اختيار صورة")
        self.select_img_btn.clicked.connect(self.select_image)
        self.select_img_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        
        self.clear_img_btn = QPushButton("🗑️ حذف الصورة")
        self.clear_img_btn.clicked.connect(self.clear_image)
        self.clear_img_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        img_btn_layout.addWidget(self.select_img_btn)
        img_btn_layout.addWidget(self.clear_img_btn)
        
        img_layout.addWidget(self.img_info)
        img_layout.addWidget(img_btn_widget)
        settings_layout.addWidget(img_group)
        
        settings_layout.addStretch()
        self.tab_widget.addTab(settings_tab, "⚙️ الإعدادات")
        
        # تبويب جهات الاتصال
        contacts_tab = QWidget()
        contacts_layout = QVBoxLayout(contacts_tab)
        
        contacts_group = QGroupBox("📇 جهات الاتصال")
        contacts_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                color: black;
            }
            QGroupBox::title {
                color: black;
            }
        """)
        group_layout = QVBoxLayout(contacts_group)
        
        # معلومات العد
        contacts_info_widget = QWidget()
        contacts_info_layout = QHBoxLayout(contacts_info_widget)
        
        self.contacts_count = QLabel("0 جهة اتصال")
        self.contacts_count.setStyleSheet("""
            color: #25D366;
            font-weight: bold;
            font-size: 16px;
            padding: 10px;
        """)
        
        contacts_info_layout.addWidget(self.contacts_count)
        contacts_info_layout.addStretch()
        
        # أزرار التحكم
        contacts_btn_widget = QWidget()
        contacts_btn_layout = QHBoxLayout(contacts_btn_widget)
        
        self.load_contacts_btn = QPushButton("📂 تحميل جهات")
        self.load_contacts_btn.clicked.connect(self.load_contacts)
        self.load_contacts_btn.setStyleSheet("""
            QPushButton {
                background: #007bff;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        
        self.view_contacts_btn = QPushButton("👁️ عرض الجهات")
        self.view_contacts_btn.clicked.connect(self.view_contacts)
        self.view_contacts_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        contacts_btn_layout.addWidget(self.load_contacts_btn)
        contacts_btn_layout.addWidget(self.view_contacts_btn)
        contacts_btn_layout.addStretch()
        
        group_layout.addWidget(contacts_info_widget)
        group_layout.addWidget(contacts_btn_widget)
        
        contacts_layout.addWidget(contacts_group)
        contacts_layout.addStretch()
        self.tab_widget.addTab(contacts_tab, "📇 الجهات")
        
        # تبويب التحكم
        control_tab = QWidget()
        control_layout = QVBoxLayout(control_tab)
        
        control_group = QGroupBox("🎮 التحكم في العملية")
        control_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                color: black;
            }
            QGroupBox::title {
                color: black;
            }
        """)
        group_layout = QVBoxLayout(control_group)
        
        # تأخير البدء
        delay_widget = QWidget()
        delay_layout = QHBoxLayout(delay_widget)
        delay_label = QLabel("⏱️ تأخير البدء:")
        delay_label.setStyleSheet("color: black;")
        delay_layout.addWidget(delay_label)
        
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 120)
        self.delay_spin.setValue(0)
        self.delay_spin.setSuffix(" دقيقة")
        self.delay_spin.setStyleSheet("padding: 8px; font-size: 14px; color: black;")
        self.delay_spin.valueChanged.connect(self.update_delay)
        delay_layout.addWidget(self.delay_spin)
        delay_layout.addStretch()
        
        group_layout.addWidget(delay_widget)
        
        # أزرار التحكم الرئيسية
        control_btn_widget = QWidget()
        control_btn_layout = QHBoxLayout(control_btn_widget)
        
        self.start_btn = QPushButton("🚀 بدء الإرسال")
        self.start_btn.clicked.connect(self.start_sending)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: black;
                font-weight: bold;
                padding: 15px 30px;
                font-size: 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #20c997 0%, #28a745 100%);
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """)
        
        self.stop_btn = QPushButton("⛔ إيقاف")
        self.stop_btn.clicked.connect(self.stop_sending)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                color: black;
                font-weight: bold;
                padding: 15px 30px;
                font-size: 16px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #c82333 0%, #dc3545 100%);
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """)
        self.stop_btn.setEnabled(False)
        
        control_btn_layout.addWidget(self.start_btn)
        control_btn_layout.addWidget(self.stop_btn)
        group_layout.addWidget(control_btn_widget)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                text-align: center;
                height: 25px;
                font-size: 12px;
                color: black;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 4px;
            }
        """)
        group_layout.addWidget(self.progress_bar)
        
        # معلومات الإحصائيات
        stats_widget = QWidget()
        stats_layout = QGridLayout(stats_widget)
        stats_layout.setSpacing(10)
        
        stats_labels = [
            ("الحالة:", "status_label", "🟢 جاهز"),
            ("تم الإرسال:", "processed_label", "0"),
            ("ناجح:", "success_label", "0"),
            ("فاشل:", "failed_label", "0"),
            ("غير صالح:", "invalid_label", "0"),
            ("المتبقي:", "remaining_label", "0")
        ]
        
        row, col = 0, 0
        for label_text, attr_name, default_value in stats_labels:
            # تسمية
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold; color: black; font-size: 12px;")
            stats_layout.addWidget(label, row, col * 2)
            
            # القيمة
            label_widget = QLabel(default_value)
            label_widget.setStyleSheet("""
                padding: 6px 12px;
                background: #e9ecef;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
                font-size: 12px;
                color: black;
            """)
            setattr(self, attr_name, label_widget)
            stats_layout.addWidget(label_widget, row, col * 2 + 1)
            
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        group_layout.addWidget(stats_widget)
        control_layout.addWidget(control_group)
        self.tab_widget.addTab(control_tab, "🎮 التحكم")
        
        # تبويب السجلات
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        logs_group = QGroupBox("📋 سجلات النظام")
        logs_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                font-size: 14px; 
                color: black;
            }
            QGroupBox::title {
                color: black;
            }
        """)
        group_layout = QVBoxLayout(logs_group)
        
        # أزرار السجلات
        logs_btn_widget = QWidget()
        logs_btn_layout = QHBoxLayout(logs_btn_widget)
        
        self.clear_logs_btn = QPushButton("🗑️ مسح السجلات")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.clear_logs_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        self.save_logs_btn = QPushButton("💾 حفظ السجلات")
        self.save_logs_btn.clicked.connect(self.save_logs)
        self.save_logs_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        
        logs_btn_layout.addWidget(self.clear_logs_btn)
        logs_btn_layout.addWidget(self.save_logs_btn)
        logs_btn_layout.addStretch()
        
        group_layout.addWidget(logs_btn_widget)
        
        # عرض السجلات
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 11px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 8px;
            color: black;
        """)
        group_layout.addWidget(self.log_display)
        
        logs_layout.addWidget(logs_group)
        self.tab_widget.addTab(logs_tab, "📋 السجلات")
        
        scroll_layout.addWidget(self.tab_widget)
        
        # إضافة الـ Scroll Widget إلى الـ Scroll Area
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        
        main_layout.addWidget(scroll_area)
        
        # ====== الجزء السفلي (ثابت لا يتحرك) ======
        bottom_widget = QWidget()
        bottom_widget.setMaximumHeight(60)
        bottom_layout = QHBoxLayout(bottom_widget)
        
        self.bottom_status = QLabel(f"✨ WhatsApp Bulk Sender v{VERSION} - جاهز للاستخدام")
        self.bottom_status.setStyleSheet("""
            padding: 10px;
            background: linear-gradient(135deg, #e8f5e9 0%, #d4edda 100%);
            border-radius: 8px;
            font-weight: bold;
            color: #155724;
            border: 2px solid #c3e6cb;
            font-size: 14px;
        """)
        
        bottom_layout.addWidget(self.bottom_status)
        bottom_layout.addStretch()
        
        # إضافة زر إغلاق
        close_btn = QPushButton("❌ إغلاق")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        bottom_layout.addWidget(close_btn)
        
        main_layout.addWidget(bottom_widget)
        
        # ====== ربط الإشارات ======
        self.extract_names_check.stateChanged.connect(self.update_name_options)
        self.add_name_to_image_check.stateChanged.connect(self.update_name_options)
        
        # مؤشر تحديث السجلات
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_log_display)
        self.log_timer.start(500)
        
        # إضافة زر لتوسيط النافذة
        QTimer.singleShot(100, self.center_window)
        
        # تحميل الألوان بناءً على النظام
        self.apply_system_theme()
        
    def apply_system_theme(self):
        """تطبيق ألوان النظام"""
        palette = self.palette()
        if palette.window().color().lightness() > 127:
            # وضع النهار - خلفية فاتحة
            self.setStyleSheet("""
                QWidget {
                    color: black;
                }
                QLabel {
                    color: black;
                }
                QCheckBox {
                    color: black;
                }
                QGroupBox::title {
                    color: black;
                }
                QTextEdit {
                    color: black;
                }
            """)
        else:
            # وضع الليل - خلفية داكنة
            self.setStyleSheet("""
                QWidget {
                    color: white;
                    background-color: #2b2b2b;
                }
                QLabel {
                    color: white;
                }
                QCheckBox {
                    color: white;
                }
                QGroupBox {
                    color: white;
                    border: 1px solid #555;
                }
                QGroupBox::title {
                    color: white;
                }
                QTextEdit {
                    color: white;
                    background-color: #3c3c3c;
                }
                QSpinBox {
                    color: white;
                    background-color: #3c3c3c;
                }
            """)
        
    def center_window(self):
        """توسيط النافذة على الشاشة"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def start_status_monitor(self):
        """بدء مراقبة حالة واتساب"""
        self.status_monitor = WhatsAppStatusMonitor()
        self.status_monitor.status_changed.connect(self.update_whatsapp_status)
        self.status_monitor.log_message.connect(self.log)
        self.status_monitor.start()
        
    def update_whatsapp_status(self, status, color):
        """تحديث حالة واتساب"""
        color_map = {
            "green": "#28a745",
            "red": "#dc3545",
            "yellow": "#ffc107",
            "gray": "#6c757d"
        }
        
        self.whatsapp_status.setText(status)
        self.whatsapp_status.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
            background: {color_map.get(color, "#f8f9fa")};
            color: {'white' if color in ['green', 'red', 'gray'] else 'black'};
            border-radius: 8px;
            border: 2px solid {color_map.get(color, "#6c757d")};
            min-width: 200px;
        """)
        
    def open_whatsapp(self):
        """فتح واتساب فقط"""
        self.log("🌐 جاري فتح واتساب ويب...")
        self.whatsapp_status.setText("🟡 جاري فتح واتساب...")
        self.whatsapp_status.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
            background: #ffc107;
            color: black;
            border-radius: 8px;
            border: 2px solid #ffc107;
        """)
        
        # تشغيل في thread منفصل
        threading.Thread(target=self._open_whatsapp_thread, daemon=True).start()
        
    def _open_whatsapp_thread(self):
        """Thread لفتح واتساب"""
        try:
            self.driver = open_whatsapp_only()
            if self.driver:
                self.log("✅ تم فتح واتساب بنجاح!")
                # إعطاء السائق لمراقب الحالة
                if self.status_monitor:
                    self.status_monitor.driver = self.driver
            else:
                self.log("❌ فشل فتح واتساب")
        except Exception as e:
            self.log(f"❌ خطأ في فتح واتساب: {e}")
            
    def copy_chrome_profile(self):
        """نسخ ملف Chrome الشخصي"""
        self.log("📂 جاري نسخ ملف Chrome الشخصي...")
        threading.Thread(target=self._copy_chrome_profile_thread, daemon=True).start()
        
    def _copy_chrome_profile_thread(self):
        """Thread لنسخ ملف Chrome الشخصي"""
        try:
            success = copy_chrome_profile()
            if success:
                self.log("✅ تم نسخ ملف Chrome الشخصي بنجاح!")
            else:
                self.log("❌ فشل نسخ ملف Chrome الشخصي")
        except Exception as e:
            self.log(f"❌ خطأ في نسخ ملف Chrome: {e}")
    
    def update_log_display(self):
        """تحديث عرض السجلات"""
        try:
            if self.log_queue:
                messages = []
                while self.log_queue:
                    messages.append(self.log_queue.pop(0))
                
                if messages:
                    self.log_display.append('\n'.join(messages))
                    scrollbar = self.log_display.verticalScrollBar()
                    scrollbar.setValue(scrollbar.maximum())
        except:
            pass
    
    def log(self, message):
        """إضافة رسالة إلى السجلات"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        
        self.log_queue.append(full_message)
        log.info(message)
    
    def update_font_size(self, size):
        """تحديث حجم الخط"""
        self.text_size = size
        self.log(f"🔠 تم تغيير حجم الخط إلى: {size} بكسل")
    
    def update_text_color(self, color):
        """تحديث لون الخط"""
        self.text_color = color
        color_name = self.get_color_name(color)
        self.current_color_label.setText(f"اللون الحالي: {color_name}")
        self.log(f"🎨 تم تغيير لون الخط إلى: {color_name}")
    
    def get_color_name(self, color_rgb):
        """الحصول على اسم اللون"""
        colors = {
            (255, 215, 0): "ذهبي",
            (255, 255, 255): "أبيض",
            (255, 0, 0): "أحمر",
            (0, 0, 255): "أزرق",
            (0, 255, 0): "أخضر",
            (0, 0, 0): "أسود",
            (192, 192, 192): "فضي"
        }
        return colors.get(tuple(color_rgb), "مخصص")
    
    def choose_custom_color(self):
        """اختيار لون مخصص"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = (color.red(), color.green(), color.blue())
            self.current_color_label.setText(f"اللون الحالي: مخصص (RGB: {color.red()}, {color.green()}, {color.blue()})")
            self.log(f"🎨 تم اختيار لون مخصص: RGB({color.red()}, {color.green()}, {color.blue()})")
    
    def toggle_text_frame(self):
        """تبديل خيار إضافة إطار دائري"""
        self.add_frame = self.add_frame_check.isChecked()
        self.log("📦 " + ("تم تفعيل إضافة برواز دائري للاسم" if self.add_frame else "تم إلغاء برواز الاسم"))
    
    def update_name_options(self):
        """تحديث خيارات الأسماء"""
        self.extract_names_from_whatsapp = self.extract_names_check.isChecked()
        self.add_name_to_image = self.add_name_to_image_check.isChecked()
        self.log("👤 " + ("تم تفعيل استخراج الأسماء" if self.extract_names_from_whatsapp else "تم تعطيل استخراج الأسماء"))
    
    def load_contacts(self):
        """تحميل جهات الاتصال"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر ملف جهات الاتصال", APP_DIR,
            "ملفات Excel (*.xlsx);;ملفات CSV (*.csv);;ملفات JSON (*.json);;جميع الملفات (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.xlsx':
                df = pd.read_excel(file_path)
            elif ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                self.log("❌ نوع الملف غير مدعوم")
                QMessageBox.warning(self, "خطأ", "نوع الملف غير مدعوم. يرجى استخدام ملف Excel أو CSV أو JSON.")
                return
            
            # تحويل إلى قواميس
            self.contacts = df.to_dict('records')
            
            # تصفية الأرقام الصالحة
            valid_contacts = []
            invalid_contacts = []
            
            for contact in self.contacts:
                # البحث عن عمود الهاتف
                phone_keys = [k for k in contact.keys() if any(word in str(k).lower() for word in ['phone', 'mobile', 'رقم', 'هاتف'])]
                
                if phone_keys:
                    phone = str(contact[phone_keys[0]])
                    validated = validate_phone_number(phone)
                    
                    if validated:
                        contact['validated_phone'] = validated
                        
                        # البحث عن عمود الاسم
                        name_keys = [k for k in contact.keys() if any(word in str(k).lower() for word in ['name', 'اسم', 'contact'])]
                        if name_keys:
                            contact['contact_name'] = str(contact[name_keys[0]])
                        else:
                            contact['contact_name'] = ""
                        
                        valid_contacts.append(contact)
                    else:
                        invalid_contacts.append({'phone': phone, 'reason': 'رقم غير صالح'})
                else:
                    invalid_contacts.append({'phone': 'غير معروف', 'reason': 'لا يوجد عمود هاتف'})
            
            self.contacts = valid_contacts
            self.invalid_contacts = invalid_contacts
            
            # تحديث العد
            self.contacts_count.setText(f"{len(self.contacts)} جهة اتصال")
            self.remaining_label.setText(str(len(self.contacts)))
            
            if self.contacts:
                self.log(f"✅ تم تحميل {len(self.contacts)} جهة اتصال صالحة")
                if invalid_contacts:
                    self.log(f"⚠️ تم تجاهل {len(invalid_contacts)} رقم غير صالح")
                
                self.bottom_status.setText(f"📊 {len(self.contacts)} جهة صالحة | ❌ {len(invalid_contacts)} غير صالحة")
                
                # عرض عينة من البيانات
                sample = min(3, len(self.contacts))
                self.log("📋 عينة من الجهات المحملة:")
                for i in range(sample):
                    contact = self.contacts[i]
                    name = contact.get('contact_name', 'بدون اسم')
                    phone = contact.get('validated_phone', '')
                    self.log(f"   {i+1}. {name} ({phone})")
                
            else:
                self.log("❌ لم يتم العثور على أرقام صالحة في الملف")
                self.bottom_status.setText("❌ لا توجد أرقام صالحة")
            
        except Exception as e:
            self.log(f"❌ خطأ في تحميل الملف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل تحميل الملف: {str(e)}")
            self.contacts = []
            self.invalid_contacts = []
            self.contacts_count.setText("0 جهة")
    
    def view_contacts(self):
        """عرض جهات الاتصال"""
        if not self.contacts and not self.invalid_contacts:
            QMessageBox.information(self, "معلومات", "لا توجد جهات اتصال للعرض.")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle(f"جهات الاتصال ({len(self.contacts)} صالحة, {len(self.invalid_contacts)} غير صالحة)")
        dialog.resize(800, 500)
        
        layout = QVBoxLayout(dialog)
        
        tab_widget = QTabWidget()
        
        if self.contacts:
            valid_tab = QWidget()
            valid_layout = QVBoxLayout(valid_tab)
            
            valid_label = QLabel(f"الأرقام الصالحة ({len(self.contacts)} جهة):")
            valid_label.setStyleSheet("color: #28a745; font-weight: bold; padding: 15px; font-size: 16px;")
            valid_layout.addWidget(valid_label)
            
            valid_table = QTableWidget()
            valid_table.setColumnCount(4)
            valid_table.setHorizontalHeaderLabels(["#", "رقم الهاتف", "الاسم", "اللغة"])
            valid_table.setRowCount(len(self.contacts))
            
            for i, contact in enumerate(self.contacts):
                valid_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                valid_table.setItem(i, 1, QTableWidgetItem(contact.get('validated_phone', '')))
                valid_table.setItem(i, 2, QTableWidgetItem(contact.get('contact_name', '')))
                
                # تحديد اللغة
                name = contact.get('contact_name', '')
                language = "عربي" if is_arabic_text(name) else "إنجليزي/أخرى"
                valid_table.setItem(i, 3, QTableWidgetItem(language))
            
            valid_table.resizeColumnsToContents()
            valid_table.setAlternatingRowColors(True)
            valid_layout.addWidget(valid_table)
            tab_widget.addTab(valid_tab, f"✅ صالحة ({len(self.contacts)})")
        
        if self.invalid_contacts:
            invalid_tab = QWidget()
            invalid_layout = QVBoxLayout(invalid_tab)
            
            invalid_label = QLabel(f"الأرقام غير الصالحة ({len(self.invalid_contacts)} جهة):")
            invalid_label.setStyleSheet("color: #dc3545; font-weight: bold; padding: 15px; font-size: 16px;")
            invalid_layout.addWidget(invalid_label)
            
            invalid_table = QTableWidget()
            invalid_table.setColumnCount(3)
            invalid_table.setHorizontalHeaderLabels(["#", "رقم الهاتف", "السبب"])
            invalid_table.setRowCount(len(self.invalid_contacts))
            
            for i, contact in enumerate(self.invalid_contacts):
                invalid_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                invalid_table.setItem(i, 1, QTableWidgetItem(contact.get('phone', '')))
                invalid_table.setItem(i, 2, QTableWidgetItem(contact.get('reason', '')))
            
            invalid_table.resizeColumnsToContents()
            invalid_table.setAlternatingRowColors(True)
            invalid_layout.addWidget(invalid_table)
            tab_widget.addTab(invalid_tab, f"❌ غير صالحة ({len(self.invalid_contacts)})")
        
        layout.addWidget(tab_widget)
        
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            background: #6c757d;
            color: white;
            padding: 10px 30px;
            border-radius: 8px;
            font-weight: bold;
        """)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def select_image(self):
        """اختيار صورة"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر صورة", APP_DIR,
            "الصور (*.png *.jpg *.jpeg *.bmp *.gif);;جميع الملفات (*.*)"
        )
        
        if file_path:
            self.image_path = file_path
            name = os.path.basename(file_path)
            size_kb = os.path.getsize(file_path) / 1024
            size_mb = size_kb / 1024
            
            if size_mb > 1:
                size_text = f"{size_mb:.1f} MB"
            else:
                size_text = f"{size_kb:.0f} KB"
            
            self.img_info.setText(f"📷 {name}\n📊 الحجم: {size_text}")
            self.img_info.setStyleSheet("""
                padding: 15px;
                background: #e8f5e9;
                border: 2px solid #28a745;
                border-radius: 10px;
                color: #155724;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            """)
            self.log(f"✅ تم اختيار الصورة: {name} ({size_text})")
    
    def clear_image(self):
        """حذف الصورة"""
        self.image_path = None
        self.img_info.setText("لم يتم اختيار صورة")
        self.img_info.setStyleSheet("""
            padding: 15px;
            background: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            color: #6c757d;
            font-size: 14px;
            qproperty-alignment: AlignCenter;
        """)
        self.log("🗑️ تم حذف الصورة")
    
    def update_delay(self, minutes):
        """تحديث التأخير"""
        self.delay_seconds = minutes * 60
        if minutes > 0:
            self.log(f"⏱ تم تعيين تأخير {minutes} دقيقة")
        else:
            self.log("⏱ بدون تأخير")
    
    def start_sending(self):
        """بدء الإرسال"""
        if not self.contacts:
            self.log("❌ يرجى تحميل جهات الاتصال أولاً")
            QMessageBox.warning(self, "تحذير", "يرجى تحميل جهات الاتصال أولاً")
            return
        
        # حفظ الرسالة
        self.message = self.message_input.toPlainText()
        
        if not self.message.strip():
            reply = QMessageBox.question(
                self, "تأكيد",
                "لم تقم بكتابة أي رسالة.\nهل تريد المتابعة بدون رسالة نصية؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # تحديث الإعدادات
        self.extract_names_from_whatsapp = self.extract_names_check.isChecked()
        self.add_name_to_image = self.add_name_to_image_check.isChecked()
        self.add_frame = self.add_frame_check.isChecked()
        
        # إعادة تعيين المتغيرات
        self.is_running = True
        self.current_index = 0
        self.successful_contacts = []
        self.failed_contacts = []
        
        # تحديث واجهة المستخدم
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("جاري الإعداد...")
        
        self.log("=" * 50)
        self.log("🚀 بدء عملية الإرسال...")
        self.log(f"🎯 عدد الجهات: {len(self.contacts)}")
        self.log(f"🎨 إعدادات الخط: حجم {self.text_size} بكسل، لون {self.get_color_name(self.text_color)}")
        self.log(f"📦 برواز الاسم: {'مفعل' if self.add_frame else 'معطل'}")
        self.log("=" * 50)
        
        # إنشاء وتشغيل thread الإرسال
        self.sending_worker = SendingThread(self)
        self.sending_worker.progress_update.connect(self.on_progress_update)
        self.sending_worker.log_message.connect(self.log)
        self.sending_worker.status_update.connect(self.on_status_update)
        self.sending_worker.finished_sending.connect(self.on_sending_finished)
        self.sending_worker.error_occurred.connect(self.on_sending_error)
        self.sending_worker.require_login_confirmation.connect(self.ask_login_confirmation)
        
        self.sending_worker.start()
    
    def ask_login_confirmation(self):
        """طلب تأكيد الدخول"""
        reply = QMessageBox.question(
            self, "تأكيد الدخول",
            "يبدو أنك لست مسجل الدخول إلى واتساب.\n\n"
            "1. تأكد من فتح واتساب ويب على Chrome\n"
            "2. امسح رمز QR Code إذا طلب منك\n"
            "3. اضغط على موافق عندما تكون مستعداً\n\n"
            "هل تريد المتابعة؟",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        
        if reply == QMessageBox.StandardButton.Cancel:
            self.log("❌ تم إلغاء العملية من قبل المستخدم")
            self.stop_sending()
    
    def on_progress_update(self, processed, successful, failed, invalid, progress):
        """تحديث التقدم"""
        self.current_index = processed
        remaining = max(0, len(self.contacts) - processed)
        
        self.processed_label.setText(str(processed))
        self.success_label.setText(str(successful))
        self.failed_label.setText(str(failed))
        self.invalid_label.setText(str(invalid))
        self.remaining_label.setText(str(remaining))
        
        self.progress_bar.setValue(progress)
        
        # تحديث حالة التقدم
        if progress < 30:
            status_text = "🔧 جاري الإعداد..."
        elif progress < 70:
            status_text = f"📤 جاري الإرسال ({processed}/{len(self.contacts)})"
        elif progress < 100:
            status_text = f"🎉 جاري الانتهاء..."
        else:
            status_text = "✅ اكتمل"
        
        self.status_label.setText(status_text)
    
    def on_status_update(self, status, color):
        """تحديث الحالة"""
        color_map = {
            "green": "#28a745",
            "red": "#dc3545",
            "yellow": "#ffc107"
        }
        
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color_map.get(color, '#000000')}; font-weight: bold;")
    
    def on_sending_finished(self):
        """عند اكتمال الإرسال"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.is_running = False
        
        # عرض النتائج النهائية
        self.show_final_results()
        
        # تنظيف - لا نغلق المتصفح!
        if self.sending_worker:
            self.sending_worker = None
        
        # تحديث حالة المراقب
        if self.status_monitor and self.driver:
            self.status_monitor.driver = self.driver
    
    def on_sending_error(self, error_message):
        """عند حدوث خطأ"""
        self.log(f"❌ خطأ في الإرسال: {error_message}")
        self.status_label.setText("❌ خطأ")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        self.stop_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        self.is_running = False
        self.sending_worker = None
        
        QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الإرسال:\n{error_message}")
    
    def stop_sending(self):
        """إيقاف الإرسال"""
        self.is_running = False
        
        if self.sending_worker:
            self.sending_worker.stop()
            self.sending_worker = None
        
        self.log("⛔ تم إيقاف الإرسال يدوياً")
        self.status_label.setText("⏹️ متوقف")
        self.status_label.setStyleSheet("color: #6c757d; font-weight: bold;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def show_final_results(self):
        """عرض النتائج النهائية"""
        try:
            total = len(self.contacts) + len(self.invalid_contacts)
            valid = len(self.contacts)
            invalid = len(self.invalid_contacts)
            success = len(self.successful_contacts)
            failed = len(self.failed_contacts)
            
            message = f"""
            📊 تقرير النتائج النهائية:
            
            📁 إجمالي الجهات في الملف: {total}
            ✅ صالحة للإرسال: {valid}
            ❌ غير صالحة (تم تجاهلها): {invalid}
            
            🎯 نتائج الإرسال:
            ✅ نجحت: {success}
            ⚠️ فشلت: {failed}
            
            📈 نسبة النجاح: {(success/valid*100 if valid > 0 else 0):.1f}%
            """
            
            QMessageBox.information(self, "اكتمل الإرسال", message.strip())
            
            # عرض تفاصيل الفاشلة إذا وجدت
            if failed > 0:
                self.log("📋 تفاصيل الجهات الفاشلة:")
                for contact in self.failed_contacts[:5]:  # عرض أول 5 فقط
                    self.log(f"   ❌ {contact.get('phone', 'غير معروف')}: {contact.get('error', 'سبب غير معروف')}")
                if failed > 5:
                    self.log(f"   ... و {failed-5} جهة أخرى")
            
        except Exception as e:
            self.log(f"⚠️ خطأ في عرض النتائج: {e}")
    
    def clear_logs(self):
        """مسح السجلات"""
        self.log_display.clear()
        self.log("🗑️ تم مسح السجلات")
    
    def save_logs(self):
        """حفظ السجلات"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ السجلات", 
            os.path.join(LOG_DIR, f"whatsapp_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"),
            "ملفات النص (*.txt);;جميع الملفات (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                self.log(f"💾 تم حفظ السجلات في: {file_path}")
                QMessageBox.information(self, "تم الحفظ", f"تم حفظ السجلات بنجاح في:\n{file_path}")
            except Exception as e:
                self.log(f"❌ فشل حفظ السجلات: {e}")
                QMessageBox.critical(self, "خطأ", f"فشل حفظ السجلات:\n{str(e)}")
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        if self.is_running:
            reply = QMessageBox.question(
                self, 'تأكيد الإغلاق',
                'جاري عملية إرسال.\n\n'
                'هل تريد إغلاق التطبيق؟\n'
                'سيتم إيقاف عملية الإرسال الحالية.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_sending()
                time.sleep(2)
                
                # إيقاف مراقبة الحالة
                if self.status_monitor:
                    self.status_monitor.stop()
                    self.status_monitor.wait(2000)
                
                self.cleanup_temp_files()
                event.accept()
            else:
                event.ignore()
        else:
            # إيقاف مراقبة الحالة
            if self.status_monitor:
                self.status_monitor.stop()
                self.status_monitor.wait(2000)
            
            self.cleanup_temp_files()
            event.accept()
    
    def cleanup_temp_files(self):
        """تنظيف الملفات المؤقتة"""
        try:
            temp_files_deleted = 0
            for file in os.listdir(APP_DIR):
                if file.startswith("temp_") and file.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    try:
                        os.remove(os.path.join(APP_DIR, file))
                        temp_files_deleted += 1
                    except:
                        pass
            
            if temp_files_deleted > 0:
                log.info(f"🧹 تم حذف {temp_files_deleted} ملف مؤقت")
        except:
            pass

# ================= MAIN =================
def cleanup_on_exit():
    """تنظيف الموارد عند الخروج"""
    log.info("🧹 جاري التنظيف...")
    
    try:
        # حذف الملفات المؤقتة
        for file in os.listdir(APP_DIR):
            if file.startswith("temp_") and file.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                try:
                    os.remove(os.path.join(APP_DIR, file))
                except:
                    pass
            
    except Exception as e:
        log.error(f"⚠️ خطأ في التنظيف: {e}")

if __name__ == "__main__":
    atexit.register(cleanup_on_exit)
    
    app = QApplication(sys.argv)
    app.setApplicationName(f"WhatsApp Bulk Sender v{VERSION}")
    app.setStyle('Fusion')  # استخدام نمط حديث
    
    window = WhatsAppSenderApp()
    window.show()
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        log.error(f"❌ خطأ غير متوقع: {e}")
        cleanup_on_exit()