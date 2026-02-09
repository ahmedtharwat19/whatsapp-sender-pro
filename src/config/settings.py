"""
نظام إعدادات التطبيق
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

class Theme(Enum):
    """المواضيع المتاحة"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class Language(Enum):
    """اللغات المتاحة"""
    ARABIC = "ar"
    ENGLISH = "en"
    FRENCH = "fr"
    SPANISH = "es"

@dataclass
class ImageSettings:
    """إعدادات الصورة"""
    add_text: bool = True
    text_color: tuple = (255, 215, 0)  # لون ذهبي
    text_size: int = 50
    add_frame: bool = True
    frame_color: tuple = (255, 255, 255)
    frame_width: int = 3

@dataclass
class SendingSettings:
    """إعدادات الإرسال"""
    delay_minutes: int = 0
    delay_seconds: int = 20
    random_delay: bool = True
    extract_names: bool = True
    send_image: bool = True
    send_message: bool = True
    max_errors: int = 5
    retry_count: int = 3

@dataclass
class WhatsAppSettings:
    """إعدادات واتساب"""
    user_data_dir: str = "chrome_profile"
    headless: bool = False
    disable_notifications: bool = True
    disable_gpu: bool = False
    no_sandbox: bool = False

@dataclass
class AppSettings:
    """إعدادات التطبيق الرئيسية"""
    # المظهر
    theme: Theme = Theme.AUTO
    language: Language = Language.ARABIC
    font_size: str = "medium"
    show_sidebar: bool = True
    
    # الإعدادات الفنية
    image_settings: ImageSettings = field(default_factory=ImageSettings)
    sending_settings: SendingSettings = field(default_factory=SendingSettings)
    whatsapp_settings: WhatsAppSettings = field(default_factory=WhatsAppSettings)
    
    # مسارات
    last_contacts_path: Optional[str] = None
    last_image_path: Optional[str] = None
    last_export_path: Optional[str] = None
    
    # إعدادات أخرى
    auto_update: bool = True
    auto_backup: bool = True
    backup_interval: int = 7  # أيام
    max_log_files: int = 10
    
    def __post_init__(self):
        """تهيئة بعد الإنشاء"""
        self.config_dir = Path(__file__).parent.parent.parent / "data" / "config"
        self.config_file = self.config_dir / "settings.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self):
        """حفظ الإعدادات"""
        try:
            # تحويل البيانات إلى قاموس
            data = {
                "theme": self.theme.value,
                "language": self.language.value,
                "font_size": self.font_size,
                "show_sidebar": self.show_sidebar,
                "image_settings": asdict(self.image_settings),
                "sending_settings": asdict(self.sending_settings),
                "whatsapp_settings": asdict(self.whatsapp_settings),
                "last_contacts_path": self.last_contacts_path,
                "last_image_path": self.last_image_path,
                "last_export_path": self.last_export_path,
                "auto_update": self.auto_update,
                "auto_backup": self.auto_backup,
                "backup_interval": self.backup_interval,
                "max_log_files": self.max_log_files,
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في حفظ الإعدادات: {e}")
            return False
    
    def load(self):
        """تحميل الإعدادات"""
        try:
            if not self.config_file.exists():
                return False
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # تحميل البيانات
            self.theme = Theme(data.get("theme", "auto"))
            self.language = Language(data.get("language", "ar"))
            self.font_size = data.get("font_size", "medium")
            self.show_sidebar = data.get("show_sidebar", True)
            
            # تحميل الإعدادات المتداخلة
            img_data = data.get("image_settings", {})
            self.image_settings = ImageSettings(
                add_text=img_data.get("add_text", True),
                text_color=tuple(img_data.get("text_color", (255, 215, 0))),
                text_size=img_data.get("text_size", 50),
                add_frame=img_data.get("add_frame", True),
                frame_color=tuple(img_data.get("frame_color", (255, 255, 255))),
                frame_width=img_data.get("frame_width", 3)
            )
            
            send_data = data.get("sending_settings", {})
            self.sending_settings = SendingSettings(
                delay_minutes=send_data.get("delay_minutes", 0),
                delay_seconds=send_data.get("delay_seconds", 20),
                random_delay=send_data.get("random_delay", True),
                extract_names=send_data.get("extract_names", True),
                send_image=send_data.get("send_image", True),
                send_message=send_data.get("send_message", True),
                max_errors=send_data.get("max_errors", 5),
                retry_count=send_data.get("retry_count", 3)
            )
            
            whatsapp_data = data.get("whatsapp_settings", {})
            self.whatsapp_settings = WhatsAppSettings(
                user_data_dir=whatsapp_data.get("user_data_dir", "chrome_profile"),
                headless=whatsapp_data.get("headless", False),
                disable_notifications=whatsapp_data.get("disable_notifications", True),
                disable_gpu=whatsapp_data.get("disable_gpu", False),
                no_sandbox=whatsapp_data.get("no_sandbox", False)
            )
            
            # تحميل المسارات
            self.last_contacts_path = data.get("last_contacts_path")
            self.last_image_path = data.get("last_image_path")
            self.last_export_path = data.get("last_export_path")
            
            # إعدادات أخرى
            self.auto_update = data.get("auto_update", True)
            self.auto_backup = data.get("auto_backup", True)
            self.backup_interval = data.get("backup_interval", 7)
            self.max_log_files = data.get("max_log_files", 10)
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في تحميل الإعدادات: {e}")
            return False
    
    def reset_to_default(self):
        """إعادة التعيين إلى الإعدادات الافتراضية"""
        self.__init__()
        return self.save()
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل الإعدادات إلى قاموس"""
        return {
            "theme": self.theme.value,
            "language": self.language.value,
            "font_size": self.font_size,
            "show_sidebar": self.show_sidebar,
            "image_settings": asdict(self.image_settings),
            "sending_settings": asdict(self.sending_settings),
            "whatsapp_settings": asdict(self.whatsapp_settings),
            "last_contacts_path": self.last_contacts_path,
            "last_image_path": self.last_image_path,
            "last_export_path": self.last_export_path,
            "auto_update": self.auto_update,
            "auto_backup": self.auto_backup,
            "backup_interval": self.backup_interval,
            "max_log_files": self.max_log_files,
        }

# إنشاء نسخة عامة للإعدادات
app_settings = AppSettings()
app_settings.load()