# app/ui/__init__.py
"""
حزمة واجهة المستخدم
"""

from .user_interface import WhatsAppSenderApp
from .admin_interface import AdminInterface
from .styles import Styles

__all__ = [
    'WhatsAppSenderApp',
    'AdminInterface',
    'Styles'
]