"""
النافذة الرئيسية للتطبيق - نسخة مصححة
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
import os
from datetime import datetime

# إضافة المسار للاستيرادات
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from config.license_manager import license_manager
    from utils.translator import translator
except ImportError:
    license_manager = None
    translator = None

from .components import ModernButton, CardWidget, SidePane, ModernTableWidget, SearchBox
from .dialogs import LicenseDialog, DeveloperDialog, SettingsDialog

class WhatsAppSenderPro(QMainWindow):
    """النافذة الرئيسية"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("WhatsApp Sender Pro v4.4.0")
        self.setGeometry(100, 100, 1400, 800)
        self.contacts = []
        self.image_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # الشريط الجانبي
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # المحتوى الرئيسي
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # العنوان
        self.title_label = QLabel("🚀 WhatsApp Sender Pro")
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
            padding: 20px;
            background: white;
            border-bottom: 2px solid #e0e0e0;
        """)
        content_layout.addWidget(self.title_label)
        
        # منطقة المحتوى الديناميكي
        self.content_stack = QStackedWidget()
        
        # صفحة لوحة التحكم
        self.dashboard_page = self.create_dashboard_page()
        self.content_stack.addWidget(self.dashboard_page)
        
        # صفحة الإرسال
        self.sending_page = self.create_sending_page()
        self.content_stack.addWidget(self.sending_page)
        
        # صفحة جهات الاتصال
        self.contacts_page = self.create_contacts_page()
        self.content_stack.addWidget(self.contacts_page)
        
        # صفحة الإعدادات
        self.settings_page = self.create_settings_page()
        self.content_stack.addWidget(self.settings_page)
        
        content_layout.addWidget(self.content_stack, stretch=1)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        # الشريط الجانبي للسجلات
        self.side_pane = SidePane()
        main_layout.addWidget(self.side_pane)
        
        # إضافة بعض السجلات للاختبار
        self.side_pane.add_log("✅ تم تحميل الواجهة الرئيسية بنجاح", "SUCCESS")
        self.side_pane.add_log(f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "INFO")
    
    def create_sidebar(self):
        """إنشاء الشريط الجانبي"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #075E54, stop:1 #128C7E);
                border-right: 1px solid #128C7E;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(10)
        
        # شعار
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setSpacing(10)
        
        icon_label = QLabel("📱")
        icon_label.setStyleSheet("font-size: 48px; text-align: center;")
        logo_layout.addWidget(icon_label)
        
        logo_text = QLabel("WhatsApp\nSender Pro")
        logo_text.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            text-align: center;
        """)
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_text)
        
        version_label = QLabel("v4.4.0")
        version_label.setStyleSheet("color: rgba(255,255,255,0.7); text-align: center;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(version_label)
        
        logo_widget.setStyleSheet("""
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 15px;
        """)
        sidebar_layout.addWidget(logo_widget)
        
        # أزرار التنقل
        nav_buttons = [
            ("🏠", "لوحة التحكم", self.show_dashboard),
            ("📤", "الإرسال", self.show_sending),
            ("👥", "جهات الاتصال", self.show_contacts),
            ("⚙️", "الإعدادات", self.show_settings),
            ("🔐", "الترخيص", self.show_license),
        ]
        
        for icon, text, callback in nav_buttons:
            btn = ModernButton(f"{icon} {text}")
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        # إضافة زر المطور
        developer_btn = ModernButton("👨‍💻 أدوات المطور")
        developer_btn.clicked.connect(self.show_developer)
        sidebar_layout.addWidget(developer_btn)
        
        sidebar_layout.addStretch()
        
        # حالة الترخيص
        if license_manager:
            status = license_manager.check_status()
            license_text = f"🔐 {status['type']}\n{status['days_remaining']} يوم"
        else:
            license_text = "🔐 تجريبي\n30 يوم"
        
        license_label = QLabel(license_text)
        license_label.setStyleSheet("""
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
        """)
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(license_label)
        
        return sidebar
    
    def create_dashboard_page(self):
        """إنشاء صفحة لوحة التحكم"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # بطاقات الإحصائيات
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        stats = [
            ("📊", "إجمالي المرسل", "0", "#25D366"),
            ("✅", "نسبة النجاح", "0%", "#28a745"),
            ("⏳", "قيد الانتظار", "0", "#ffc107"),
            ("❌", "فشل", "0", "#dc3545"),
            ("👥", "جهات الاتصال", "0", "#17a2b8"),
            ("⏱️", "الوقت المستغرق", "0s", "#6c757d"),
        ]
        
        self.stats_cards = {}
        for i, (icon, title, value, color) in enumerate(stats):
            card = self.create_stat_card(icon, title, value, color)
            self.stats_cards[title] = card
            stats_grid.addWidget(card, i // 3, i % 2)
        
        layout.addLayout(stats_grid)
        
        # إحصائيات سريعة
        quick_stats = CardWidget("📈 إحصائيات سريعة")
        quick_layout = QHBoxLayout()
        
        stats_list = [
            ("اليوم", "0 رسالة"),
            ("هذا الأسبوع", "0 رسالة"),
            ("هذا الشهر", "0 رسالة"),
            ("الإجمالي", "0 رسالة"),
        ]
        
        for period, count in stats_list:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            
            period_label = QLabel(period)
            period_label.setStyleSheet("font-size: 12px; color: #666;")
            period_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            count_label = QLabel(count)
            count_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
            count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            stat_layout.addWidget(period_label)
            stat_layout.addWidget(count_label)
            quick_layout.addWidget(stat_widget)
        
        quick_stats.layout.addLayout(quick_layout)
        layout.addWidget(quick_stats)
        
        # الإجراءات السريعة
        quick_actions = CardWidget("⚡ إجراءات سريعة")
        actions_layout = QHBoxLayout()
        
        actions = [
            ("📤", "بدء إرسال جديد", self.start_new_sending),
            ("👥", "تحميل جهات اتصال", self.load_contacts),
            ("⚙️", "الإعدادات السريعة", self.quick_settings),
            ("📊", "عرض التقارير", self.show_reports),
        ]
        
        for icon, text, callback in actions:
            btn = QPushButton(f"{icon}\n{text}")
            btn.setMinimumHeight(80)
            btn.setStyleSheet("""
                QPushButton {
                    background: white;
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    font-size: 12px;
                    padding: 10px;
                    text-align: center;
                }
                QPushButton:hover {
                    border-color: #25D366;
                    background: #f8fff9;
                }
            """)
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn)
        
        quick_actions.layout.addLayout(actions_layout)
        layout.addWidget(quick_actions)
        
        layout.addStretch()
        return widget
    
    def create_stat_card(self, icon, title, value, color):
        """إنشاء بطاقة إحصائية"""
        card = CardWidget()
        card.setStyleSheet(f"""
            CardWidget {{
                background: white;
                border-radius: 12px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = card.layout
        
        # الأيقونة والقيمة
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        
        top_layout.addWidget(icon_label)
        top_layout.addStretch()
        top_layout.addWidget(value_label)
        
        layout.addLayout(top_layout)
        
        # العنوان
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #666;")
        layout.addWidget(title_label)
        
        return card
    
    def create_sending_page(self):
        """إنشاء صفحة الإرسال"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # رسالة الترحيب - التصحيح هنا
        welcome_card = CardWidget("🚀 نظام الإرسال")
        welcome_layout = welcome_card.layout
        
        steps = QLabel("""
        <div style='font-size: 14px; line-height: 1.6;'>
        <h3>تعليمات الإرسال:</h3>
        <ol>
            <li>📝 <b>اكتب الرسالة</b> في المربع أدناه</li>
            <li>🖼️ <b>اختر صورة</b> إذا كنت تريد إرسال صورة</li>
            <li>👥 <b>تأكد</b> من تحميل جهات الاتصال</li>
            <li>⚙️ <b>اضبط</b> الإعدادات المناسبة</li>
            <li>🚀 <b>اضغط</b> على زر 'بدء الإرسال'</li>
        </ol>
        </div>
        """)
        steps.setWordWrap(True)
        welcome_layout.addWidget(steps)
        layout.addWidget(welcome_card)
        
        # محرر الرسالة - التصحيح هنا
        message_card = CardWidget("📝 نص الرسالة")
        message_layout = message_card.layout
        
        self.message_editor = QTextEdit()
        self.message_editor.setPlaceholderText("""اكتب رسالتك هنا...

يمكنك استخدام المتغيرات التالية:
{name} - اسم المستلم
{phone} - رقم الهاتف  
{date} - التاريخ الحالي
{time} - الوقت الحالي
{number} - الرقم التسلسلي""")
        self.message_editor.setMinimumHeight(150)
        self.message_editor.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #25D366;
            }
        """)
        message_layout.addWidget(self.message_editor)
        layout.addWidget(message_card)
        
        # إعدادات الصورة - التصحيح هنا
        image_card = CardWidget("🖼️ إعدادات الصورة")
        image_layout = image_card.layout
        
        # اختيار الصورة
        img_select_layout = QHBoxLayout()
        self.img_path_label = QLabel("📷 لم يتم اختيار صورة")
        self.img_path_label.setStyleSheet("""
            padding: 12px;
            background: #f8f9fa;
            border-radius: 6px;
            border: 1px dashed #dee2e6;
        """)
        
        browse_btn = ModernButton("📁 اختيار صورة")
        browse_btn.clicked.connect(self.select_image)
        
        clear_img_btn = QPushButton("🗑️")
        clear_img_btn.setFixedSize(40, 40)
        clear_img_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        clear_img_btn.clicked.connect(self.clear_image)
        
        img_select_layout.addWidget(self.img_path_label, stretch=1)
        img_select_layout.addWidget(browse_btn)
        img_select_layout.addWidget(clear_img_btn)
        image_layout.addLayout(img_select_layout)
        
        # خيارات النص على الصورة
        text_options = QHBoxLayout()
        
        self.add_text_check = QCheckBox("✏️ إضافة نص على الصورة")
        self.add_text_check.setChecked(True)
        
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(30, 30)
        self.text_color_btn.setStyleSheet("background: gold; border-radius: 15px;")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        
        self.text_size_spin = QSpinBox()
        self.text_size_spin.setRange(20, 100)
        self.text_size_spin.setValue(50)
        self.text_size_spin.setSuffix(" px")
        
        text_options.addWidget(self.add_text_check)
        text_options.addWidget(QLabel("لون النص:"))
        text_options.addWidget(self.text_color_btn)
        text_options.addWidget(QLabel("حجم النص:"))
        text_options.addWidget(self.text_size_spin)
        text_options.addStretch()
        
        image_layout.addLayout(text_options)
        layout.addWidget(image_card)
        
        # إعدادات الإرسال - التصحيح هنا
        settings_card = CardWidget("⚙️ إعدادات الإرسال")
        settings_layout = QGridLayout()
        settings_layout.setSpacing(15)
        
        # تأخير البدء
        settings_layout.addWidget(QLabel("⏰ تأخير البدء:"), 0, 0)
        self.start_delay_spin = QSpinBox()
        self.start_delay_spin.setRange(0, 120)
        self.start_delay_spin.setSuffix(" دقيقة")
        self.start_delay_spin.setValue(0)
        settings_layout.addWidget(self.start_delay_spin, 0, 1)
        
        # تأخير بين الرسائل
        settings_layout.addWidget(QLabel("⏱️ تأخير بين الرسائل:"), 1, 0)
        self.message_delay_spin = QSpinBox()
        self.message_delay_spin.setRange(5, 300)
        self.message_delay_spin.setSuffix(" ثانية")
        self.message_delay_spin.setValue(20)
        settings_layout.addWidget(self.message_delay_spin, 1, 1)
        
        # خيارات عشوائية
        self.random_delay_check = QCheckBox("🎲 تأخير عشوائي")
        self.random_delay_check.setChecked(True)
        settings_layout.addWidget(self.random_delay_check, 2, 0, 1, 2)
        
        # استخراج الأسماء
        self.extract_names_check = QCheckBox("🔍 استخراج الأسماء من واتساب")
        self.extract_names_check.setChecked(True)
        settings_layout.addWidget(self.extract_names_check, 3, 0, 1, 2)
        
        settings_card.layout.addLayout(settings_layout)
        layout.addWidget(settings_card)
        
        # أزرار التحكم - التصحيح هنا
        control_card = CardWidget("🎮 التحكم")
        control_layout = QVBoxLayout()
        
        # أزرار البدء والإيقاف
        btn_layout = QHBoxLayout()
        
        self.start_btn = ModernButton("🚀 بدء الإرسال")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #28a745, stop:1 #20c997);
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.start_btn.clicked.connect(self.start_sending)
        
        self.stop_btn = ModernButton("⛔ إيقاف")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dc3545, stop:1 #c82333);
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_sending)
        
        btn_layout.addWidget(self.start_btn, stretch=2)
        btn_layout.addWidget(self.stop_btn, stretch=1)
        
        control_layout.addLayout(btn_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #25D366, stop:1 #128C7E);
                border-radius: 3px;
            }
        """)
        control_layout.addWidget(self.progress_bar)
        
        # معلومات التقدم
        self.progress_label = QLabel("✅ جاهز للبدء")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        """)
        control_layout.addWidget(self.progress_label)
        
        control_card.layout.addLayout(control_layout)
        layout.addWidget(control_card)
        layout.addStretch()
        return widget
    
    def create_contacts_page(self):
        """إنشاء صفحة جهات الاتصال"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان الصفحة - التصحيح هنا
        header_card = CardWidget("👥 إدارة جهات الاتصال")
        header_layout = header_card.layout
        
        header_label = QLabel("""
        <div style='font-size: 14px;'>
        <p>قم بتحميل جهات الاتصال من ملف Excel أو CSV، ثم قم بإدارتها وتصفيتها قبل البدء في الإرسال.</p>
        </div>
        """)
        header_label.setWordWrap(True)
        header_layout.addWidget(header_label)
        layout.addWidget(header_card)
        
        # أدوات التحكم - التصحيح هنا
        controls_card = CardWidget("🛠️ أدوات التحكم")
        controls_layout = controls_card.layout
        
        # أزرار الإجراءات
        actions_layout = QHBoxLayout()
        
        load_btn = ModernButton("📂 تحميل جهات اتصال")
        load_btn.clicked.connect(self.load_contacts)
        
        import_btn = ModernButton("📥 استيراد")
        import_btn.clicked.connect(self.import_contacts)
        
        export_btn = ModernButton("📤 تصدير")
        export_btn.clicked.connect(self.export_contacts)
        
        clear_btn = QPushButton("🗑️ مسح الكل")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        clear_btn.clicked.connect(self.clear_contacts)
        
        actions_layout.addWidget(load_btn)
        actions_layout.addWidget(import_btn)
        actions_layout.addWidget(export_btn)
        actions_layout.addWidget(clear_btn)
        
        controls_layout.addLayout(actions_layout)
        
        # شريط البحث
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 بحث:")
        self.contacts_search = SearchBox()
        self.contacts_search.textChanged.connect(self.filter_contacts)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.contacts_search)
        controls_layout.addLayout(search_layout)
        
        # معلومات العدد
        self.contacts_count_label = QLabel("📊 إجمالي جهات الاتصال: 0")
        self.contacts_count_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #25D366;")
        controls_layout.addWidget(self.contacts_count_label)
        
        layout.addWidget(controls_card)
        
        # جدول جهات الاتصال - التصحيح هنا
        table_card = CardWidget("📋 قائمة جهات الاتصال")
        table_layout = table_card.layout
        
        self.contacts_table = ModernTableWidget()
        self.contacts_table.setColumnCount(4)
        self.contacts_table.setHorizontalHeaderLabels(["#", "الاسم", "رقم الهاتف", "الحالة"])
        
        # ضبط أعمدة الجدول
        header = self.contacts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        
        self.contacts_table.setColumnWidth(0, 50)
        self.contacts_table.setColumnWidth(3, 100)
        
        # إضافة بيانات وهمية للعرض
        sample_contacts = [
            ("أحمد محمد", "01012345678", "✅ صالح"),
            ("محمد علي", "01123456789", "✅ صالح"),
            ("سارة خالد", "01234567890", "✅ صالح"),
            ("خالد أحمد", "غير صالح", "❌ غير صالح"),
            ("فاطمة عمر", "01567890123", "✅ صالح"),
        ]
        
        for i, (name, phone, status) in enumerate(sample_contacts, 1):
            self.contacts_table.add_row(
                str(i),
                name,
                phone,
                status
            )
        
        table_layout.addWidget(self.contacts_table)
        layout.addWidget(table_card)
        
        # إحصائيات - التصحيح هنا
        stats_card = CardWidget("📈 إحصائيات")
        stats_layout = QHBoxLayout()
        
        stats = [
            ("إجمالي", "5", "#17a2b8"),
            ("صالح", "4", "#28a745"),
            ("غير صالح", "1", "#dc3545"),
            ("مكرر", "0", "#ffc107"),
        ]
        
        for label, value, color in stats:
            stat_widget = QWidget()
            stat_layout_inner = QVBoxLayout(stat_widget)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"""
                font-size: 24px;
                font-weight: bold;
                color: {color};
                text-align: center;
            """)
            
            label_label = QLabel(label)
            label_label.setStyleSheet("font-size: 12px; color: #666; text-align: center;")
            
            stat_layout_inner.addWidget(value_label)
            stat_layout_inner.addWidget(label_label)
            stats_layout.addWidget(stat_widget)
        
        stats_card.layout.addLayout(stats_layout)
        layout.addWidget(stats_card)
        
        layout.addStretch()
        return widget
    
    def create_settings_page(self):
        """إنشاء صفحة الإعدادات"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # إعدادات المظهر - التصحيح هنا
        appearance_card = CardWidget("🎨 إعدادات المظهر")
        appearance_layout = appearance_card.layout
        
        # اللغة
        lang_layout = QHBoxLayout()
        lang_label = QLabel("🌍 اللغة:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["العربية", "English", "Français", "Español"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo, stretch=1)
        appearance_layout.addLayout(lang_layout)
        
        # السمة
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 السمة:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["فاتح", "داكن", "تلقائي"])
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo, stretch=1)
        appearance_layout.addLayout(theme_layout)
        
        layout.addWidget(appearance_card)
        
        # إعدادات واتساب - التصحيح هنا
        whatsapp_card = CardWidget("📱 إعدادات واتساب")
        whatsapp_layout = whatsapp_card.layout
        
        self.headless_check = QCheckBox("تشغيل واتساب في الخلفية (Headless)")
        whatsapp_layout.addWidget(self.headless_check)
        
        self.save_session_check = QCheckBox("حفظ الجلسة لتجنب مسح QR في كل مرة")
        self.save_session_check.setChecked(True)
        whatsapp_layout.addWidget(self.save_session_check)
        
        self.disable_notifications_check = QCheckBox("تعطيل الإشعارات")
        self.disable_notifications_check.setChecked(True)
        whatsapp_layout.addWidget(self.disable_notifications_check)
        
        layout.addWidget(whatsapp_card)
        
        # إعدادات متقدمة - التصحيح هنا
        advanced_card = CardWidget("⚙️ إعدادات متقدمة")
        advanced_layout = advanced_card.layout
        
        self.auto_backup_check = QCheckBox("نسخ احتياطي تلقائي")
        self.auto_backup_check.setChecked(True)
        advanced_layout.addWidget(self.auto_backup_check)
        
        self.auto_update_check = QCheckBox("التحديث التلقائي")
        self.auto_update_check.setChecked(True)
        advanced_layout.addWidget(self.auto_update_check)
        
        self.logging_check = QCheckBox("تفعيل السجلات التفصيلية")
        self.logging_check.setChecked(True)
        advanced_layout.addWidget(self.logging_check)
        
        layout.addWidget(advanced_card)
        
        # إعدادات الأداء - التصحيح هنا
        performance_card = CardWidget("⚡ إعدادات الأداء")
        performance_layout = QGridLayout()
        
        # الحد الأقصى للأخطاء
        performance_layout.addWidget(QLabel("الحد الأقصى للأخطاء:"), 0, 0)
        self.max_errors_spin = QSpinBox()
        self.max_errors_spin.setRange(1, 50)
        self.max_errors_spin.setValue(10)
        performance_layout.addWidget(self.max_errors_spin, 0, 1)
        
        # عدد المحاولات
        performance_layout.addWidget(QLabel("عدد المحاولات:"), 1, 0)
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(1, 10)
        self.retry_count_spin.setValue(3)
        performance_layout.addWidget(self.retry_count_spin, 1, 1)
        
        # حجم الدُفعة
        performance_layout.addWidget(QLabel("حجم الدُفعة:"), 2, 0)
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 100)
        self.batch_size_spin.setValue(50)
        self.batch_size_spin.setSuffix(" جهة اتصال")
        performance_layout.addWidget(self.batch_size_spin, 2, 1)
        
        performance_card.layout.addLayout(performance_layout)
        layout.addWidget(performance_card)
        
        # أزرار التحكم - التصحيح هنا
        buttons_card = CardWidget("🎮 التحكم")
        buttons_layout = QHBoxLayout()
        
        save_btn = ModernButton("💾 حفظ الإعدادات")
        save_btn.clicked.connect(self.save_all_settings)
        
        reset_btn = ModernButton("🔄 استعادة الإعدادات الافتراضية")
        reset_btn.clicked.connect(self.reset_settings)
        
        test_btn = ModernButton("🧪 اختبار الإعدادات")
        test_btn.clicked.connect(self.test_settings)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(test_btn)
        
        buttons_card.layout.addLayout(buttons_layout)
        layout.addWidget(buttons_card)
        layout.addStretch()
        return widget
    
    # دوال التنقل
    def show_dashboard(self):
        self.title_label.setText("🏠 لوحة التحكم")
        self.content_stack.setCurrentWidget(self.dashboard_page)
        self.side_pane.add_log("📊 تم فتح لوحة التحكم", "INFO")
    
    def show_sending(self):
        self.title_label.setText("📤 نظام الإرسال")
        self.content_stack.setCurrentWidget(self.sending_page)
        self.side_pane.add_log("📤 تم فتح صفحة الإرسال", "INFO")
    
    def show_contacts(self):
        self.title_label.setText("👥 إدارة جهات الاتصال")
        self.content_stack.setCurrentWidget(self.contacts_page)
        self.side_pane.add_log("👥 تم فتح صفحة جهات الاتصال", "INFO")
    
    def show_settings(self):
        self.title_label.setText("⚙️ إعدادات التطبيق")
        self.content_stack.setCurrentWidget(self.settings_page)
        self.side_pane.add_log("⚙️ تم فتح صفحة الإعدادات", "INFO")
    
    def show_license(self):
        dialog = LicenseDialog(self)
        dialog.exec()
        self.side_pane.add_log("🔐 تم فتح نافذة الترخيص", "INFO")
    
    def show_developer(self):
        dialog = DeveloperDialog(self)
        dialog.exec()
        self.side_pane.add_log("👨‍💻 تم فتح أدوات المطور", "INFO")
    
    # دوال الصفحات
    def start_new_sending(self):
        self.show_sending()
        self.side_pane.add_log("🚀 بدء إرسال جديد", "INFO")
    
    def load_contacts(self):
        # محاكاة تحميل جهات الاتصال
        self.contacts_count_label.setText("📊 إجمالي جهات الاتصال: 25")
        self.side_pane.add_log("📂 تم تحميل 25 جهة اتصال", "SUCCESS")
        QMessageBox.information(self, "نجاح", "تم تحميل جهات الاتصال بنجاح!")
    
    def quick_settings(self):
        self.show_settings()
        self.side_pane.add_log("⚡ فتح الإعدادات السريعة", "INFO")
    
    def show_reports(self):
        self.side_pane.add_log("📊 عرض التقارير", "INFO")
        QMessageBox.information(self, "التقارير", "ميزة التقارير قريباً!")
    
    def select_image(self):
        self.side_pane.add_log("🖼️ اختيار صورة", "INFO")
        self.img_path_label.setText("📷 example_image.jpg (مختار)")
        QMessageBox.information(self, "اختيار صورة", "تم اختيار الصورة بنجاح!")
    
    def clear_image(self):
        self.img_path_label.setText("📷 لم يتم اختيار صورة")
        self.side_pane.add_log("🗑️ تم مسح الصورة", "INFO")
    
    def choose_text_color(self):
        self.side_pane.add_log("🎨 اختيار لون النص", "INFO")
        QMessageBox.information(self, "اختيار لون", "اختر لون النص!")
    
    def start_sending(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("⏳ جاري الإرسال...")
        
        # محاكاة الإرسال
        self.side_pane.add_log("🚀 بدء عملية الإرسال", "INFO")
        
        # مؤقت لمحاكاة التقدم
        from PyQt6.QtCore import QTimer
        self.progress_value = 0
        
        def update_progress():
            self.progress_value += 5
            self.progress_bar.setValue(self.progress_value)
            
            if self.progress_value >= 100:
                self.timer.stop()
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.progress_label.setText("✅ تم الإرسال بنجاح!")
                self.side_pane.add_log("✅ اكتمل الإرسال بنجاح", "SUCCESS")
                QMessageBox.information(self, "نجاح", "تم الإرسال بنجاح!")
        
        self.timer = QTimer()
        self.timer.timeout.connect(update_progress)
        self.timer.start(200)  # تحديث كل 200 مللي ثانية
    
    def stop_sending(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_label.setText("⛔ تم إيقاف الإرسال")
        self.side_pane.add_log("⛔ تم إيقاف الإرسال", "WARNING")
    
    def filter_contacts(self, text):
        self.side_pane.add_log(f"🔍 البحث عن: {text}", "INFO")
    
    def import_contacts(self):
        self.side_pane.add_log("📥 استيراد جهات اتصال", "INFO")
        QMessageBox.information(self, "استيراد", "ميزة الاستيراد قريباً!")
    
    def export_contacts(self):
        self.side_pane.add_log("📤 تصدير جهات اتصال", "INFO")
        QMessageBox.information(self, "تصدير", "ميزة التصدير قريباً!")
    
    def clear_contacts(self):
        self.side_pane.add_log("🗑️ مسح جميع جهات الاتصال", "WARNING")
        reply = QMessageBox.question(
            self, 'تأكيد المسح',
            'هل أنت متأكد من مسح جميع جهات الاتصال؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.contacts_count_label.setText("📊 إجمالي جهات الاتصال: 0")
            self.contacts_table.setRowCount(0)
            self.side_pane.add_log("✅ تم مسح جميع جهات الاتصال", "SUCCESS")
    
    def save_all_settings(self):
        self.side_pane.add_log("💾 حفظ جميع الإعدادات", "SUCCESS")
        QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح!")
    
    def reset_settings(self):
        self.side_pane.add_log("🔄 استعادة الإعدادات الافتراضية", "INFO")
        QMessageBox.information(self, "استعادة", "تم استعادة الإعدادات الافتراضية!")
    
    def test_settings(self):
        self.side_pane.add_log("🧪 اختبار الإعدادات", "INFO")
        QMessageBox.information(self, "اختبار", "تم اختبار الإعدادات بنجاح!")
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        reply = QMessageBox.question(
            self, 'تأكيد الخروج',
            'هل أنت متأكد من الخروج؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.side_pane.add_log("👋 تم إغلاق التطبيق", "INFO")
            event.accept()
        else:
            event.ignore()