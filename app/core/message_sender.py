# app/core/message_sender.py
"""
مرسل الرسائل - لإدارة وتنظيم عملية الإرسال
"""

import pandas as pd
import json
import csv
from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path
from datetime import datetime
import logging
import threading
from queue import Queue

class MessageSender:
    def __init__(self, whatsapp_manager):
        """تهيئة مرسل الرسائل"""
        self.logger = logging.getLogger(__name__)
        self.whatsapp_manager = whatsapp_manager
        self.is_sending = False
        self.progress_queue = Queue()
        self.current_progress = 0
        
    def load_contacts(self, file_path):
        """تحميل جهات الاتصال من ملف"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                raise ValueError("تنسيق الملف غير مدعوم")
            
            # تنظيف بيانات الهواتف
            contacts = []
            for _, row in df.iterrows():
                phone = str(row.get('phone', '') or row.get('Phone', '') or row.get('PHONE', ''))
                name = str(row.get('name', '') or row.get('Name', '') or row.get('NAME', ''))
                
                # تنظيف رقم الهاتف
                phone = ''.join(filter(str.isdigit, phone))
                
                if phone:
                    contacts.append({
                        'phone': phone,
                        'name': name if name else phone,
                        'data': row.to_dict()
                    })
            
            self.logger.info(f"تم تحميل {len(contacts)} جهة اتصال")
            return contacts
            
        except Exception as e:
            self.logger.error(f"خطأ في تحميل جهات الاتصال: {e}")
            return []
    
    def add_text_to_image(self, image_path, text, font_size=30, font_color=(255, 255, 255), 
                          position='bottom', background_color=(0, 0, 0, 128)):
        """إضافة نص إلى صورة"""
        try:
            img = Image.open(image_path).convert("RGBA")
            draw = ImageDraw.Draw(img)
            
            # تحميل الخط
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # حساب حجم النص
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # تحديد موضع النص
            img_width, img_height = img.size
            padding = 20
            
            if position == 'top':
                x = (img_width - text_width) // 2
                y = padding
            elif position == 'bottom':
                x = (img_width - text_width) // 2
                y = img_height - text_height - padding
            elif position == 'center':
                x = (img_width - text_width) // 2
                y = (img_height - text_height) // 2
            else:
                x = padding
                y = padding
            
            # إضافة خلفية شبه شفافة للنص
            bg_rect = [
                x - 10, y - 5,
                x + text_width + 10, y + text_height + 5
            ]
            draw.rectangle(bg_rect, fill=background_color)
            
            # إضافة النص
            draw.text((x, y), text, font=font, fill=font_color)
            
            # حفظ الصورة المعدلة
            output_path = Path(image_path).parent / f"modified_{Path(image_path).name}"
            img.save(output_path)
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"خطأ في إضافة النص إلى الصورة: {e}")
            return image_path
    
    def send_bulk_messages(self, contacts, message_template, image_path=None, 
                          font_color='white', text_position='bottom', delay=2):
        """إرسال رسائل جماعية"""
        self.is_sending = True
        self.current_progress = 0
        total_contacts = len(contacts)
        
        for i, contact in enumerate(contacts):
            if not self.is_sending:
                break
            
            try:
                # تخصيص الرسالة
                personalized_message = message_template
                for key, value in contact['data'].items():
                    placeholder = f"{{{key}}}"
                    personalized_message = personalized_message.replace(
                        placeholder, str(value)
                    )
                
                # تخصيص الصورة
                if image_path and os.path.exists(image_path):
                    # إضافة اسم المستلم على الصورة
                    modified_image = self.add_text_to_image(
                        image_path=image_path,
                        text=contact['name'],
                        font_color=self._parse_color(font_color),
                        position=text_position
                    )
                else:
                    modified_image = None
                
                # إرسال الرسالة
                success = self.whatsapp_manager.send_message(
                    phone_number=contact['phone'],
                    message=personalized_message,
                    image_path=modified_image
                )
                
                if success:
                    status = f"تم الإرسال إلى {contact['name']}"
                    self.logger.info(status)
                else:
                    status = f"فشل الإرسال إلى {contact['name']}"
                    self.logger.error(status)
                
                # تحديث التقدم
                self.current_progress = int(((i + 1) / total_contacts) * 100)
                self.progress_queue.put({
                    'contact': contact['name'],
                    'status': status,
                    'progress': self.current_progress
                })
                
                # تأخير بين الرسائل
                time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"خطأ في إرسال رسالة لـ {contact['name']}: {e}")
                continue
        
        self.is_sending = False
    
    def _parse_color(self, color_str):
        """تحويل سلسلة اللون إلى RGB"""
        color_map = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255)
        }
        
        if color_str.lower() in color_map:
            return color_map[color_str.lower()]
        else:
            try:
                # محاولة تحليل hex color
                if color_str.startswith('#'):
                    hex_color = color_str.lstrip('#')
                    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            except:
                pass
        
        return (255, 255, 255)  # لون افتراضي
    
    def stop_sending(self):
        """إيقاف عملية الإرسال"""
        self.is_sending = False