#!/usr/bin/env python3
"""
ملف تشغيل WhatsApp Sender Pro
"""

import sys
import os
from pathlib import Path

# الحصول على مسار المجلد الحالي
current_dir = Path(__file__).parent

# إضافة مجلد src إلى مسار بايثون
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

print(f"📁 تشغيل من: {current_dir}")
print(f"📁 مجلد src: {src_dir}")

# التحقق من وجود المجلدات المطلوبة
required_dirs = ["data/config", "data/logs", "data/fonts", "data/temp"]
for dir_path in required_dirs:
    dir_full = current_dir / dir_path
    dir_full.mkdir(parents=True, exist_ok=True)
    print(f"📁 تأكد من وجود: {dir_full}")

try:
    # تشغيل التطبيق
    from src.main import main
    main()
except Exception as e:
    print(f"❌ خطأ في التشغيل: {e}")
    import traceback
    traceback.print_exc()
    input("\nاضغط Enter للخروج...")