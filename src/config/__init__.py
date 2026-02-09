"""
حزمة إعدادات التطبيق
"""

from .settings import AppSettings, app_settings
from .license_manager import LicenseManager, license_manager

__all__ = ['AppSettings', 'app_settings', 'LicenseManager', 'license_manager']