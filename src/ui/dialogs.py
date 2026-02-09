"""
النوافذ والحوارات المخصصة
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import json
import base64
from datetime import datetime, timedelta
import sys
import os

# إضافة المسار للاستيرادات
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from config.license_manager import license_manager
    from utils.translator import translator
except ImportError:
    # استيرادات بديلة في حالة الفشل
    license_manager = None
    translator = None

from .components import ModernButton, CardWidget

class LicenseDialog(QDialog):
    """حوار الترخيص"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 الترخيص")
        self.setMinimumSize(700, 600)
        self.setup_ui()
        self.load_license_info()
    
    def setup_ui(self):
        """إعداد الواجهة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # العنوان
        title = QLabel("🔐 نظام الترخيص")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        self.info_group = QGroupBox("حالة الترخيص")
        self.info_group.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout = QVBoxLayout(self.info_group)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 8px;")
        info_layout.addWidget(self.status_label)
        
        # الحصول على HWID من license_manager إذا كان متاحاً
        hwid = license_manager.get_hardware_id() if license_manager else "غير متاح"
        self.hardware_label = QLabel(f"معرف الجهاز: {hwid}")
        self.hardware_label.setStyleSheet("""
            font-family: monospace; 
            background: #f8f9fa; 
            padding: 10px; 
            border-radius: 6px;
        """)
        self.hardware_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addWidget(self.hardware_label)
        
        layout.addWidget(self.info_group)
        
        tabs = QTabWidget()
        
        # تبويب التفعيل
        activation_tab = QWidget()
        activation_layout = QVBoxLayout(activation_tab)
        
        # معلومات النسخة التجريبية
        if license_manager:
            status = license_manager.check_status()
            if status["type"] == "trial" and status["is_valid"]:
                trial_info = QLabel(f"🎁 نسخة تجريبية: {status['days_remaining']} يوم متبقي")
                trial_info.setStyleSheet("""
                    background: #d4edda;
                    color: #155724;
                    padding: 15px;
                    border-radius: 8px;
                    font-size: 14px;
                """)
                activation_layout.addWidget(trial_info)
            elif not status["is_valid"]:
                expired_info = QLabel("⛔ الترخيص منتهي الصلاحية")
                expired_info.setStyleSheet("""
                    background: #f8d7da;
                    color: #721c24;
                    padding: 15px;
                    border-radius: 8px;
                    font-size: 14px;
                """)
                activation_layout.addWidget(expired_info)
        else:
            error_info = QLabel("⚠️ نظام الترخيص غير متوفر")
            error_info.setStyleSheet("""
                background: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            """)
            activation_layout.addWidget(error_info)
        
        # حقل إدخال مفتاح الترخيص
        key_layout = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("أدخل مفتاح الترخيص...")
        self.key_input.setStyleSheet("""
            padding: 12px; 
            font-size: 14px; 
            border: 2px solid #dee2e6; 
            border-radius: 8px;
        """)
        
        activate_btn = ModernButton("تفعيل")
        activate_btn.clicked.connect(self.activate_license)
        
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(activate_btn)
        activation_layout.addLayout(key_layout)
        
        # تعليمات الحصول على الترخيص
        instructions = QLabel("""
        <h3>كيفية الحصول على مفتاح ترخيص:</h3>
        <ol>
            <li>انسخ معرف الجهاز أعلاه</li>
            <li>تواصل مع المطور عبر:</li>
            <ul>
                <li>📱 واتساب: +201061007999</li>
                <li>📧 البريد: ahmed.tharwat19@gmail.com</li>
            </ul>
            <li>أرسل معرف الجهاز واختر الباقة المناسبة</li>
            <li>ستستلم مفتاح الترخيص خلال 24 ساعة</li>
        </ol>
        """)
        instructions.setStyleSheet("font-size: 13px; color: #555;")
        instructions.setWordWrap(True)
        activation_layout.addWidget(instructions)
        
        activation_layout.addStretch()
        tabs.addTab(activation_tab, "تفعيل الترخيص")
        
        # تبويب الأسعار
        pricing_tab = QWidget()
        pricing_layout = QVBoxLayout(pricing_tab)
        
        pricing_title = QLabel("💼 باقات الاشتراك")
        pricing_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        pricing_layout.addWidget(pricing_title)
        
        plans_grid = QGridLayout()
        plans_grid.setSpacing(15)
        
        plans = [
            ("شهري", "500 ج.م", "30 يوم", "#17a2b8"),
            ("ربع سنوي", "1200 ج.م", "90 يوم", "#28a745"),
            ("نصف سنوي", "2000 ج.م", "180 يوم", "#ffc107"),
            ("سنوي", "3800 ج.م", "365 يوم", "#dc3545"),
        ]
        
        for i, (plan, price, duration, color) in enumerate(plans):
            card = CardWidget()
            card.setStyleSheet(f"""
                CardWidget {{
                    background-color: white;
                    border-radius: 12px;
                    border: 2px solid {color};
                }}
            """)
            
            plan_name = QLabel(plan)
            plan_name.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
            plan_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            plan_price = QLabel(price)
            plan_price.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
            plan_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            plan_duration = QLabel(duration)
            plan_duration.setStyleSheet("font-size: 14px; color: #666;")
            plan_duration.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            card.layout.addWidget(plan_name)
            card.layout.addWidget(plan_price)
            card.layout.addWidget(plan_duration)
            
            plans_grid.addWidget(card, i // 2, i % 2)
        
        pricing_layout.addLayout(plans_grid)
        
        contact_btn = ModernButton("📞 التواصل مع الدعم")
        contact_btn.clicked.connect(self.contact_support)
        pricing_layout.addWidget(contact_btn)
        
        pricing_layout.addStretch()
        tabs.addTab(pricing_tab, "الباقات والأسعار")
        
        layout.addWidget(tabs)
        
        close_btn = ModernButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def load_license_info(self):
        """تحميل معلومات الترخيص"""
        if not license_manager:
            status_text = "⚠️ نظام الترخيص غير متوفر"
            self.status_label.setStyleSheet("""
                font-size: 16px; 
                padding: 10px; 
                border-radius: 8px;
                background: #fff3cd;
                color: #856404;
            """)
            self.status_label.setText(status_text)
            return
        
        status = license_manager.check_status()
        
        if status["is_valid"]:
            if status["type"] == "trial":
                status_text = f"🎁 تجريبي - {status['days_remaining']} يوم متبقي"
                self.status_label.setStyleSheet("""
                    font-size: 16px; 
                    padding: 10px; 
                    border-radius: 8px;
                    background: #fff3cd;
                    color: #856404;
                """)
            else:
                status_text = f"✅ مفعل - {status['days_remaining']} يوم متبقي"
                self.status_label.setStyleSheet("""
                    font-size: 16px; 
                    padding: 10px; 
                    border-radius: 8px;
                    background: #d4edda;
                    color: #155724;
                """)
        else:
            status_text = "⛔ منتهي الصلاحية"
            self.status_label.setStyleSheet("""
                font-size: 16px; 
                padding: 10px; 
                border-radius: 8px;
                background: #f8d7da;
                color: #721c24;
            """)
        
        self.status_label.setText(status_text)
    
    def activate_license(self):
        """تفعيل الترخيص"""
        if not license_manager:
            QMessageBox.critical(self, "خطأ", "نظام الترخيص غير متوفر")
            return
        
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مفتاح الترخيص")
            return
        
        success, message = license_manager.activate_license(key)
        if success:
            QMessageBox.information(self, "نجاح", "تم تفعيل الترخيص بنجاح!")
            self.load_license_info()
        else:
            QMessageBox.critical(self, "خطأ", f"فشل التفعيل: {message}")
    
    def contact_support(self):
        """التواصل مع الدعم"""
        import webbrowser
        webbrowser.open(f"https://wa.me/201061007999")

class DeveloperDialog(QDialog):
    """حوار المطور"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👨‍💻 أدوات المطور")
        self.setMinimumSize(900, 700)
        self.current_license_key = None
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد الواجهة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("👨‍💻 لوحة تحكم المطور")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            padding: 20px;
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            border-radius: 15px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # معلومات المطور
        info_card = CardWidget("معلومات المطور")
        info_text = QLabel("""
        <div style='font-size: 14px; line-height: 1.6;'>
        <b>👨‍💻 المطور:</b> أحمد ثروت<br>
        <b>📱 الهاتف:</b> +201061007999<br>
        <b>📧 البريد:</b> ahmed.tharwat19@gmail.com<br>
        <b>🚀 الإصدار:</b> 4.4.0<br>
        <b>🏷️ النوع:</b> PROFESSIONAL
        </div>
        """)
        info_text.setStyleSheet("padding: 15px;")
        info_card.layout.addWidget(info_text)
        layout.addWidget(info_card)
        
        # إنشاء ترخيص
        license_card = CardWidget("إنشاء ترخيص جديد")
        license_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.buyer_name = QLineEdit()
        self.buyer_name.setPlaceholderText("اسم المشتري")
        form_layout.addRow("👤 اسم المشتري:", self.buyer_name)
        
        self.buyer_phone = QLineEdit()
        self.buyer_phone.setPlaceholderText("رقم الهاتف")
        form_layout.addRow("📱 الهاتف:", self.buyer_phone)
        
        self.buyer_email = QLineEdit()
        self.buyer_email.setPlaceholderText("البريد الإلكتروني")
        form_layout.addRow("📧 البريد:", self.buyer_email)
        
        license_layout.addLayout(form_layout)
        
        # نوع الاشتراك
        plan_layout = QHBoxLayout()
        plan_label = QLabel("📅 نوع الاشتراك:")
        self.plan_combo = QComboBox()
        self.plan_combo.addItems(["شهري", "ربع سنوي", "نصف سنوي", "سنوي"])
        plan_layout.addWidget(plan_label)
        plan_layout.addWidget(self.plan_combo)
        plan_layout.addStretch()
        license_layout.addLayout(plan_layout)
        
        create_btn = ModernButton("🚀 إنشاء ترخيص")
        create_btn.setMinimumHeight(50)
        create_btn.clicked.connect(self.generate_license)
        license_layout.addWidget(create_btn)
        
        license_card.layout.addLayout(license_layout)
        layout.addWidget(license_card)
        
        # عرض الترخيص المنشأ
        self.license_display = QTextEdit()
        self.license_display.setReadOnly(True)
        self.license_display.setPlaceholderText("سيعرض هنا مفتاح الترخيص بعد إنشائه...")
        self.license_display.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.license_display)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        copy_btn = ModernButton("📋 نسخ الترخيص")
        copy_btn.clicked.connect(self.copy_license)
        
        save_btn = ModernButton("💾 حفظ في ملف")
        save_btn.clicked.connect(self.save_license)
        
        close_btn = ModernButton("❌ إغلاق")
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def generate_license(self):
        """إنشاء ترخيص جديد"""
        if not license_manager:
            QMessageBox.critical(self, "خطأ", "نظام الترخيص غير متوفر")
            return
        
        buyer_name = self.buyer_name.text().strip()
        buyer_phone = self.buyer_phone.text().strip()
        buyer_email = self.buyer_email.text().strip()
        
        if not buyer_name:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال اسم المشتري")
            return
        
        plan_map = {
            "شهري": "monthly",
            "ربع سنوي": "quarterly", 
            "نصف سنوي": "half_yearly",
            "سنوي": "yearly"
        }
        plan = plan_map.get(self.plan_combo.currentText(), "monthly")
        
        # إنشاء بيانات المشتري
        buyer_info = {
            "name": buyer_name,
            "phone": buyer_phone,
            "email": buyer_email
        }
        
        # إنشاء مفتاح الترخيص
        license_key = license_manager.generate_license_key(buyer_info, plan)
        
        if license_key:
            # عرض الترخيص
            display_text = f"""
╔{'═' * 60}╗
║{'معلومات الترخيص'.center(58)}║
╠{'═' * 60}╣
║ 🔑 مفتاح الترخيص: {license_key[:50]}...║
╠{'─' * 60}╣
║ 👤 المشتري: {buyer_name:<44}║
║ 📱 الهاتف: {buyer_phone if buyer_phone else 'N/A':<44}║
║ 📧 البريد: {buyer_email if buyer_email else 'N/A':<44}║
╠{'─' * 60}╣
║ 📅 نوع الاشتراك: {plan:<44}║
║ ⏰ تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d'):<44}║
╚{'═' * 60}╝
            """
            
            self.license_display.setText(display_text)
            self.current_license_key = license_key
            
            QMessageBox.information(self, "نجاح", "تم إنشاء الترخيص بنجاح!")
        else:
            QMessageBox.critical(self, "خطأ", "فشل إنشاء الترخيص")
    
    def copy_license(self):
        """نسخ الترخيص"""
        if self.current_license_key:
            import pyperclip
            pyperclip.copy(self.current_license_key)
            QMessageBox.information(self, "نجاح", "تم نسخ الترخيص إلى الحافظة")
        else:
            QMessageBox.warning(self, "تحذير", "لا يوجد ترخيص لنسخه")
    
    def save_license(self):
        """حفظ الترخيص في ملف"""
        if self.current_license_key:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ ملف الترخيص",
                f"license_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dat",
                "ملفات الترخيص (*.dat);;جميع الملفات (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(self.current_license_key)
                    QMessageBox.information(self, "نجاح", f"تم حفظ الملف في: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "خطأ", f"فشل حفظ الملف: {e}")

class SettingsDialog(QDialog):
    """حوار الإعدادات"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ الإعدادات")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """إعداد الواجهة"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("⚙️ إعدادات التطبيق")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        tabs = QTabWidget()
        
        # تبويب المظهر
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        # اللغة
        lang_layout = QHBoxLayout()
        lang_label = QLabel("🌍 اللغة:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["العربية", "English", "Français", "Español"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        appearance_layout.addLayout(lang_layout)
        
        # السمة
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 السمة:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["فاتح", "داكن", "تلقائي"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        
        # حجم الخط
        font_layout = QHBoxLayout()
        font_label = QLabel("🔤 حجم الخط:")
        self.font_combo = QComboBox()
        self.font_combo.addItems(["صغير", "متوسط", "كبير"])
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)
        font_layout.addStretch()
        appearance_layout.addLayout(font_layout)
        
        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "المظهر")
        
        # تبويب الإرسال
        sending_tab = QWidget()
        sending_layout = QVBoxLayout(sending_tab)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(5, 300)
        self.delay_spin.setSuffix(" ثانية")
        form_layout.addRow("⏱️ تأخير بين الرسائل:", self.delay_spin)
        
        self.start_delay_spin = QSpinBox()
        self.start_delay_spin.setRange(0, 60)
        self.start_delay_spin.setSuffix(" دقيقة")
        form_layout.addRow("⏰ تأخير البدء:", self.start_delay_spin)
        
        self.random_check = QCheckBox("تأخير عشوائي")
        form_layout.addRow("", self.random_check)
        
        self.extract_check = QCheckBox("استخراج الأسماء من واتساب")
        form_layout.addRow("", self.extract_check)
        
        sending_layout.addLayout(form_layout)
        sending_layout.addStretch()
        tabs.addTab(sending_tab, "الإرسال")
        
        # تبويب الصور
        images_tab = QWidget()
        images_layout = QVBoxLayout(images_tab)
        
        image_form = QFormLayout()
        
        self.text_size_spin = QSpinBox()
        self.text_size_spin.setRange(20, 100)
        image_form.addRow("🔤 حجم نص الصورة:", self.text_size_spin)
        
        self.add_frame_check = QCheckBox("إضافة إطار للنص")
        image_form.addRow("", self.add_frame_check)
        
        self.auto_resize_check = QCheckBox("تغيير حجم الصور تلقائياً")
        image_form.addRow("", self.auto_resize_check)
        
        images_layout.addLayout(image_form)
        images_layout.addStretch()
        tabs.addTab(images_tab, "الصور")
        
        layout.addWidget(tabs)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        save_btn = ModernButton("💾 حفظ")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = ModernButton("❌ إلغاء")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_settings(self):
        """تحميل الإعدادات"""
        try:
            # هنا يمكنك تحميل الإعدادات من ملف
            # للإعدادات الافتراضية الآن
            self.delay_spin.setValue(20)
            self.start_delay_spin.setValue(0)
            self.random_check.setChecked(True)
            self.extract_check.setChecked(True)
            self.text_size_spin.setValue(50)
            self.add_frame_check.setChecked(True)
            self.auto_resize_check.setChecked(True)
            self.lang_combo.setCurrentText("العربية")
            self.theme_combo.setCurrentText("تلقائي")
            self.font_combo.setCurrentText("متوسط")
        except:
            pass
    
    def save_settings(self):
        """حفظ الإعدادات"""
        try:
            # هنا يمكنك حفظ الإعدادات في ملف
            settings = {
                "language": self.lang_combo.currentText(),
                "theme": self.theme_combo.currentText(),
                "font_size": self.font_combo.currentText(),
                "delay": self.delay_spin.value(),
                "start_delay": self.start_delay_spin.value(),
                "random_delay": self.random_check.isChecked(),
                "extract_names": self.extract_check.isChecked(),
                "text_size": self.text_size_spin.value(),
                "add_frame": self.add_frame_check.isChecked(),
                "auto_resize": self.auto_resize_check.isChecked()
            }
            
            # حفظ في ملف (مثال)
            import json
            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=2)
            
            QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل حفظ الإعدادات: {e}")

# تصدير الكلاسات
__all__ = ['LicenseDialog', 'DeveloperDialog', 'SettingsDialog']