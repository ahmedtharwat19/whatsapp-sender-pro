# app/__init__.py
"""
حزمة WhatsApp Sender Pro
"""

__version__ = "1.0.0"
__author__ = "Your Company"
__email__ = "support@yourcompany.com"

from .core.whatsapp_manager import WhatsAppManager
from .core.message_sender import MessageSender
from .core.license_validator import LicenseValidator
from .core.hwid_generator import HWIDGenerator
from .core.encryption_service import EncryptionService
from .core.update_checker import UpdateChecker

from .ui.user_interface import WhatsAppSenderApp
from .ui.admin_interface import AdminInterface
from .ui.styles import Styles

from .services.firestore_service import FirestoreService
from .services.license_service import LicenseService
from .services.auth_service import AuthService

__all__ = [
    'WhatsAppManager',
    'MessageSender',
    'LicenseValidator',
    'HWIDGenerator',
    'EncryptionService',
    'UpdateChecker',
    'WhatsAppSenderApp',
    'AdminInterface',
    'Styles',
    'FirestoreService',
    'LicenseService',
    'AuthService'
]