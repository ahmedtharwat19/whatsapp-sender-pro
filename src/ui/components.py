"""
مكونات واجهة المستخدم المخصصة
"""

from PyQt6.QtWidgets import (
    QPushButton, QFrame, QLabel, QLineEdit, QTextEdit,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QSlider,
    QGroupBox, QScrollArea, QWidget, QSizePolicy, QHBoxLayout,
    QVBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QColor, QFont, QPalette, QLinearGradient, QBrush,
    QPainter, QPen, QPainterPath, QMouseEvent
)

class ModernButton(QPushButton):
    """زر حديث بتصميم متطور"""
    
    clicked_with_data = pyqtSignal(object)
    
    def __init__(self, text="", icon=None, parent=None, data=None):
        super().__init__(text, parent)
        self.data = data
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        
        if icon:
            self.setIcon(icon)
        
        self.apply_default_style()
    
    def apply_default_style(self):
        """تطبيق التصميم الافتراضي"""
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #25D366, stop:1 #128C7E);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #128C7E, stop:1 #075E54);
            }
            QPushButton:pressed {
                background: #075E54;
                padding: 11px 20px 9px 20px;
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """)
    
    def apply_style(self, style_type: str):
        """تطبيق نمط محدد"""
        styles = {
            "primary": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #007bff, stop:1 #0056b3);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0056b3, stop:1 #004085);
                }
            """,
            "success": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #28a745, stop:1 #1e7e34);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1e7e34, stop:1 #155724);
                }
            """,
            "danger": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #dc3545, stop:1 #c82333);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #c82333, stop:1 #bd2130);
                }
            """,
            "warning": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ffc107, stop:1 #e0a800);
                    color: #212529;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #e0a800, stop:1 #d39e00);
                }
            """,
            "info": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #17a2b8, stop:1 #138496);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #138496, stop:1 #117a8b);
                }
            """
        }
        
        base_style = self.styleSheet()
        if style_type in styles:
            self.setStyleSheet(base_style + styles[style_type])
    
    def mousePressEvent(self, event):
        """معالجة ضغط الماوس"""
        super().mousePressEvent(event)
        if self.data is not None:
            self.clicked_with_data.emit(self.data)

class CardWidget(QFrame):
    """بطاقة بتصميم حديث"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            CardWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding-bottom: 10px;
                border-bottom: 2px solid #25D366;
                margin-bottom: 10px;
            """)
            self.layout.addWidget(self.title_label)
    
    def add_widget(self, widget, stretch=0):
        """إضافة عنصر واجهة"""
        self.layout.addWidget(widget, stretch)
    
    def add_layout(self, layout):
        """إضافة تخطيط"""
        self.layout.addLayout(layout)
    
    def add_stretch(self, stretch=0):
        """إضافة مساحة مرنة"""
        self.layout.addStretch(stretch)

class SidePane(QFrame):
    """الشريط الجانبي للسجلات"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350)
        self.setStyleSheet("""
            SidePane {
                background-color: #f8f9fa;
                border-left: 1px solid #dee2e6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # عنوان السجلات
        header = QLabel("📋 سجل النشاط")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding: 10px;
            background: #e9ecef;
            border-radius: 8px;
        """)
        layout.addWidget(header)
        
        # شريط البحث
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث...")
        self.search_input.setStyleSheet("""
            padding: 8px;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            background: white;
        """)
        
        search_btn = QPushButton("🔍")
        search_btn.setFixedWidth(40)
        search_btn.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # عرض السجلات
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_display)
        
        # أزرار التحكم في السجلات
        buttons_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑️ مسح")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        
        self.save_btn = QPushButton("💾 حفظ")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        
        self.export_btn = QPushButton("📊 تصدير تقرير")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.export_btn)
        layout.addLayout(buttons_layout)
        
        # معلومات سريعة
        self.stats_label = QLabel("📊 إحصائيات")
        self.stats_label.setStyleSheet("""
            font-size: 12px;
            color: #6c757d;
            padding: 10px;
            background: #e9ecef;
            border-radius: 6px;
        """)
        layout.addWidget(self.stats_label)
        
        self.logs = []
    
    def add_log(self, message, level="INFO"):
        """إضافة سجل جديد"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append({"time": timestamp, "level": level, "message": message, "full": log_entry})
        
        color = "#000000"
        if level == "ERROR":
            color = "#dc3545"
        elif level == "WARNING":
            color = "#ffc107"
        elif level == "SUCCESS":
            color = "#28a745"
        
        self.log_display.append(f'<span style="color: {color};">{log_entry}</span>')
        
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        self.update_stats()
    
    def filter_logs(self, text):
        """تصفية السجلات"""
        self.log_display.clear()
        for log in self.logs:
            if text.lower() in log["message"].lower() or text.lower() in log["level"].lower():
                self.log_display.append(log["full"])
    
    def clear_logs(self):
        """مسح السجلات"""
        self.logs = []
        self.log_display.clear()
        self.add_log("تم مسح السجلات", "INFO")
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        total = len(self.logs)
        errors = len([l for l in self.logs if l["level"] == "ERROR"])
        warnings = len([l for l in self.logs if l["level"] == "WARNING"])
        
        stats_text = f"📊 الإجمالي: {total} | ❌ أخطاء: {errors} | ⚠️ تحذيرات: {warnings}"
        self.stats_label.setText(stats_text)

class AnimatedProgressBar(QProgressBar):
    """شريط تقدم متحرك"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.setDuration(500)
    
    def set_value_animated(self, value):
        """تعيين القيمة مع حركة"""
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()

class GradientLabel(QLabel):
    """نص بتدرج لوني"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.gradient_start = QColor(37, 211, 102)  # لون واتساب
        self.gradient_end = QColor(18, 140, 126)    # لون واتساب داكن
    
    def set_gradient(self, start: QColor, end: QColor):
        """تعيين التدرج اللوني"""
        self.gradient_start = start
        self.gradient_end = end
        self.update()
    
    def paintEvent(self, event):
        """رسم النص بالتدرج"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # إنشاء التدرج
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, self.gradient_start)
        gradient.setColorAt(1, self.gradient_end)
        
        painter.setPen(QPen(gradient, 2))
        painter.setBrush(QBrush(gradient))
        
        # رسم النص
        painter.setFont(self.font())
        painter.drawText(self.rect(), self.alignment(), self.text())

class SearchBox(QLineEdit):
    """مربع بحث مع أيقونة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("🔍 ابحث...")
        self.setClearButtonEnabled(True)
        
        self.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #25D366;
                background: #f8f9ff;
            }
            QLineEdit:hover {
                border-color: #adb5bd;
            }
        """)

class ModernTableWidget(QTableWidget):
    """جدول حديث مع ميزات متقدمة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # تحسين مظهر الرأس
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background: white;
                gridline-color: #e9ecef;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background: #f8f9fa;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e9ecef;
            }
            QTableWidget::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
        """)
    
    def add_row(self, *items):
        """إضافة صف جديد"""
        row = self.rowCount()
        self.insertRow(row)
        
        for col, item in enumerate(items):
            if isinstance(item, str):
                self.setItem(row, col, QTableWidgetItem(item))
            else:
                self.setItem(row, col, item)

class ToggleSwitch(QCheckBox):
    """مفتاح تبديل حديث"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # إعداد التصميم
        self.setStyleSheet("""
            QCheckBox {
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 50px;
                height: 25px;
                border-radius: 12.5px;
                background: #cccccc;
                border: 1px solid #999999;
            }
            QCheckBox::indicator:checked {
                background: #25D366;
                border: 1px solid #128C7E;
            }
            QCheckBox::indicator:unchecked:hover {
                background: #b3b3b3;
            }
            QCheckBox::indicator:checked:hover {
                background: #128C7E;
            }
            QCheckBox::indicator:checked:pressed {
                background: #075E54;
            }
        """)


class ModernComboBox(QComboBox):
    """قائمة منسدلة حديثة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                min-height: 40px;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox:focus {
                border-color: #25D366;
                background: #f8f9ff;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 16px;
                height: 16px;
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background: white;
                selection-background-color: #25D366;
                selection-color: white;
                padding: 5px;
            }
        """)

# تصدير الكلاسات الرئيسية
__all__ = [
    'ModernButton',
    'CardWidget', 
    'SidePane',
    'AnimatedProgressBar',
    'GradientLabel',
    'SearchBox',
    'ModernTableWidget',
    'ToggleSwitch',
    'ModernComboBox'
]