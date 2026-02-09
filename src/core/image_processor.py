"""
معالجة الصور وإضافة النصوص
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class ImageProcessor:
    """معالج الصور المتقدم"""
    
    def __init__(self):
        self.fonts_dir = Path(__file__).parent.parent.parent / "data" / "fonts"
        self.temp_dir = Path(__file__).parent.parent.parent / "data" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def add_text_to_image(
        self,
        image_path: str,
        text: str,
        text_color: Tuple[int, int, int] = (255, 215, 0),  # ذهبي
        font_size: int = 50,
        add_frame: bool = True,
        frame_color: Tuple[int, int, int] = (255, 255, 255),
        frame_width: int = 3
    ) -> Optional[str]:
        """إضافة نص إلى صورة مع إطار"""
        try:
            # فتح الصورة
            img = Image.open(image_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            
            # تحضير النص العربي
            prepared_text = self._prepare_arabic_text(text)
            
            # تحميل الخط
            font = self._load_font(font_size)
            
            # حساب حجم النص
            text_bbox = draw.textbbox((0, 0), prepared_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            img_width, img_height = img.size
            
            # ضبط حجم الخط ليناسب الصورة
            max_text_width = img_width * 0.8
            while text_width > max_text_width and font_size > 20:
                font_size = int(font_size * 0.9)
                font = self._load_font(font_size)
                text_bbox = draw.textbbox((0, 0), prepared_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            
            # حساب الموضع (أعلى الوسط)
            x = (img_width - text_width) // 2
            y = 30
            
            # إضافة إطار إذا كان مطلوباً
            if add_frame:
                self._add_frame(
                    img, draw,
                    x, y, text_width, text_height,
                    frame_color, frame_width
                )
            
            # إضافة ظل للنص
            shadow_offset = 2
            shadow_color = (0, 0, 0, 150)
            draw.text(
                (x + shadow_offset, y + shadow_offset),
                prepared_text,
                font=font,
                fill=shadow_color
            )
            
            # إضافة النص الرئيسي
            draw.text(
                (x, y),
                prepared_text,
                font=font,
                fill=text_color + (255,)  # إضافة قناة ألفا
            )
            
            # حفظ الصورة المؤقتة
            output_path = self._save_temp_image(img, image_path)
            
            return output_path
            
        except Exception as e:
            print(f"❌ خطأ في إضافة النص للصورة: {e}")
            return None
    
    def _prepare_arabic_text(self, text: str) -> str:
        """تحضير النص العربي"""
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            # التحقق إذا كان النص عربياً
            def is_arabic(text: str) -> bool:
                arabic_range = range(0x0600, 0x06FF)
                return any(ord(char) in arabic_range for char in text)
            
            if is_arabic(text):
                reshaped = arabic_reshaper.reshape(text)
                return get_display(reshaped)
            
            return text
            
        except ImportError:
            return text  # إرجاع النص كما هو إذا لم تكن المكتبات مثبتة
        except Exception:
            return text
    
    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """تحميل الخط المناسب"""
        font_paths = [
            self.fonts_dir / "arial.ttf",
            self.fonts_dir / "tahoma.ttf",
            self.fonts_dir / "segoeui.ttf",
            "C:\\Windows\\Fonts\\tahoma.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\segoeui.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(str(font_path), size)
                except:
                    continue
        
        # استخدام الخط الافتراضي
        return ImageFont.load_default()
    
    def _add_frame(
        self,
        img: Image.Image,
        draw: ImageDraw.Draw,
        x: int, y: int,
        width: int, height: int,
        color: Tuple[int, int, int],
        width_px: int
    ):
        """إضافة إطار حول النص"""
        padding = 20
        radius = 15
        
        # إنشاء طبقة شفافية للإطار
        frame_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        frame_draw = ImageDraw.Draw(frame_layer)
        
        # حساب موضع الإطار
        frame_box = [
            x - padding,
            y - padding,
            x + width + padding,
            y + height + padding
        ]
        
        # رسم إطار دائري
        frame_draw.rounded_rectangle(
            frame_box,
            radius=radius,
            outline=color + (255,),  # مع شفافية كاملة
            width=width_px
        )
        
        # دمج الإطار مع الصورة
        img.paste(frame_layer, (0, 0), frame_layer)
    
    def _save_temp_image(self, img: Image.Image, original_path: str) -> str:
        """حفظ الصورة المؤقتة"""
        import time
        import hashlib
        
        # إنشاء اسم فريد للصورة
        timestamp = int(time.time())
        original_hash = hashlib.md5(original_path.encode()).hexdigest()[:8]
        temp_filename = f"temp_{original_hash}_{timestamp}.jpg"
        temp_path = self.temp_dir / temp_filename
        
        # حفظ كـ JPEG بجودة عالية
        img = img.convert("RGB")
        img.save(temp_path, "JPEG", quality=95, optimize=True)
        
        return str(temp_path)
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """تنظيف الملفات المؤقتة القديمة"""
        import time
        
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file in self.temp_dir.glob("temp_*.jpg"):
                file_age = current_time - file.stat().st_mtime
                if file_age > max_age_seconds:
                    file.unlink()
                    
        except Exception as e:
            print(f"⚠️ خطأ في تنظيف الملفات المؤقتة: {e}")
    
    def resize_image(
        self,
        image_path: str,
        max_width: int = 1024,
        max_height: int = 1024,
        quality: int = 85
    ) -> Optional[str]:
        """تغيير حجم الصورة"""
        try:
            img = Image.open(image_path)
            
            # حساب الأبعاد الجديدة مع الحفاظ على التناسب
            img_width, img_height = img.size
            
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width / img_width, max_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # حفظ الصورة المؤقتة
                temp_path = self._save_temp_image(img, image_path)
                return temp_path
            
            return image_path  # الصورة بحجم مناسب
            
        except Exception as e:
            print(f"❌ خطأ في تغيير حجم الصورة: {e}")
            return None
    
    def convert_image_format(
        self,
        image_path: str,
        target_format: str = "JPEG"
    ) -> Optional[str]:
        """تحويل تنسيق الصورة"""
        try:
            img = Image.open(image_path)
            
            if target_format.upper() == "JPEG":
                img = img.convert("RGB")
            
            temp_path = self._save_temp_image(img, image_path)
            return temp_path
            
        except Exception as e:
            print(f"❌ خطأ في تحويل تنسيق الصورة: {e}")
            return None

# إنشاء نسخة عامة من معالج الصور
image_processor = ImageProcessor()