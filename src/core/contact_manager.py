"""
إدارة جهات الاتصال
"""

import pandas as pd
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Contact:
    """جهة اتصال"""
    name: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """التحقق من صحة جهة الاتصال"""
        return bool(self.phone and self._clean_phone(self.phone))
    
    def _clean_phone(self, phone: str) -> str:
        """تنظيف رقم الهاتف"""
        # إزالة جميع الأحرف غير الرقمية
        cleaned = re.sub(r'\D', '', str(phone))
        
        # التحقق من طول الرقم
        if len(cleaned) < 8:
            return ""
        
        # معالجة الأرقام الدولية
        if cleaned.startswith('00'):
            cleaned = cleaned[2:]
        elif cleaned.startswith('+'):
            cleaned = cleaned[1:]
        
        # إضافة رمز مصر افتراضياً إذا كان الرقم محلياً
        if len(cleaned) == 10 and cleaned.startswith('01'):
            cleaned = '20' + cleaned[1:]
        
        return cleaned
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "name": self.name,
            "phone": self.phone,
            "clean_phone": self._clean_phone(self.phone),
            "email": self.email,
            "company": self.company,
            "notes": self.notes,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
            "is_valid": self.is_valid()
        }

class ContactManager:
    """مدير جهات الاتصال"""
    
    def __init__(self):
        self.contacts: List[Contact] = []
        self.filtered_contacts: List[Contact] = []
        self.current_filter = ""
        self.stats = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "duplicates": 0
        }
    
    def load_from_file(self, file_path: str) -> Tuple[bool, str]:
        """تحميل جهات الاتصال من ملف"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.xlsx':
                df = pd.read_excel(file_path)
            elif file_ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                return False, f"تنسيق الملف غير مدعوم: {file_ext}"
            
            # تحويل البيانات إلى جهات اتصال
            self.contacts = self._dataframe_to_contacts(df)
            
            # تحديث الإحصائيات
            self._update_stats()
            
            return True, f"تم تحميل {len(self.contacts)} جهة اتصال"
            
        except Exception as e:
            return False, f"خطأ في تحميل الملف: {str(e)}"
    
    def _dataframe_to_contacts(self, df: pd.DataFrame) -> List[Contact]:
        """تحويل DataFrame إلى قائمة جهات اتصال"""
        contacts = []
        
        for _, row in df.iterrows():
            contact = Contact()
            
            # البحث عن الحقول في الأعمدة
            for col in df.columns:
                col_lower = str(col).lower()
                
                # البحث عن رقم الهاتف
                if any(keyword in col_lower for keyword in ['phone', 'mobile', 'tel', 'هاتف', 'رقم', 'جوال']):
                    contact.phone = str(row[col])
                
                # البحث عن الاسم
                elif any(keyword in col_lower for keyword in ['name', 'اسم', 'contact', 'جهة', 'person']):
                    contact.name = str(row[col])
                
                # البحث عن البريد الإلكتروني
                elif any(keyword in col_lower for keyword in ['email', 'mail', 'بريد', 'إيميل']):
                    contact.email = str(row[col])
                
                # البحث عن الشركة
                elif any(keyword in col_lower for keyword in ['company', 'شركة', 'عمل', 'organization']):
                    contact.company = str(row[col])
            
            # إضافة جهة الاتصال إذا كان لديها رقم هاتف
            if contact.phone:
                contacts.append(contact)
        
        return contacts
    
    def add_contact(self, contact: Contact) -> bool:
        """إضافة جهة اتصال جديدة"""
        if contact.is_valid():
            self.contacts.append(contact)
            self._update_stats()
            return True
        return False
    
    def remove_contact(self, index: int) -> bool:
        """حذف جهة اتصال"""
        if 0 <= index < len(self.contacts):
            self.contacts.pop(index)
            self._update_stats()
            return True
        return False
    
    def update_contact(self, index: int, contact: Contact) -> bool:
        """تحديث جهة اتصال"""
        if 0 <= index < len(self.contacts) and contact.is_valid():
            self.contacts[index] = contact
            self._update_stats()
            return True
        return False
    
    def filter_contacts(self, query: str) -> List[Contact]:
        """تصفية جهات الاتصال"""
        self.current_filter = query.lower()
        
        if not query:
            self.filtered_contacts = self.contacts.copy()
            return self.filtered_contacts
        
        filtered = []
        for contact in self.contacts:
            # البحث في جميع الحقول
            search_text = (
                f"{contact.name} {contact.phone} {contact.email} "
                f"{contact.company} {contact.notes} {' '.join(contact.tags)}"
            ).lower()
            
            if query.lower() in search_text:
                filtered.append(contact)
        
        self.filtered_contacts = filtered
        return filtered
    
    def export_to_file(self, file_path: str, format: str = "excel") -> Tuple[bool, str]:
        """تصدير جهات الاتصال إلى ملف"""
        try:
            # تحويل إلى DataFrame
            data = [contact.to_dict() for contact in self.contacts]
            df = pd.DataFrame(data)
            
            if format.lower() == "excel":
                df.to_excel(file_path, index=False)
            elif format.lower() == "csv":
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif format.lower() == "json":
                df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            else:
                return False, f"تنسيق التصدير غير مدعوم: {format}"
            
            return True, f"تم تصدير {len(self.contacts)} جهة اتصال إلى {file_path}"
            
        except Exception as e:
            return False, f"خطأ في التصدير: {str(e)}"
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات جهات الاتصال"""
        return self.stats.copy()
    
    def _update_stats(self):
        """تحديث الإحصائيات"""
        valid_contacts = [c for c in self.contacts if c.is_valid()]
        
        # البحث عن مكررات
        phone_counts = {}
        for contact in valid_contacts:
            clean_phone = contact._clean_phone(contact.phone)
            phone_counts[clean_phone] = phone_counts.get(clean_phone, 0) + 1
        
        duplicates = sum(1 for count in phone_counts.values() if count > 1)
        
        self.stats = {
            "total": len(self.contacts),
            "valid": len(valid_contacts),
            "invalid": len(self.contacts) - len(valid_contacts),
            "duplicates": duplicates,
            "unique": len(phone_counts)
        }
    
    def validate_phone_numbers(self) -> List[Tuple[int, str, str]]:
        """التحقق من صحة أرقام الهواتف وإرجاع النتائج"""
        results = []
        
        for i, contact in enumerate(self.contacts):
            clean_phone = contact._clean_phone(contact.phone)
            if clean_phone:
                results.append((i, contact.phone, clean_phone, "صالح"))
            else:
                results.append((i, contact.phone, "", "غير صالح"))
        
        return results
    
    def deduplicate(self) -> int:
        """إزالة المكررات"""
        seen_phones = set()
        unique_contacts = []
        removed_count = 0
        
        for contact in self.contacts:
            clean_phone = contact._clean_phone(contact.phone)
            if clean_phone and clean_phone not in seen_phones:
                seen_phones.add(clean_phone)
                unique_contacts.append(contact)
            else:
                removed_count += 1
        
        self.contacts = unique_contacts
        self._update_stats()
        
        return removed_count
    
    def get_contacts(self, filtered: bool = False) -> List[Contact]:
        """الحصول على جهات الاتصال"""
        if filtered and self.current_filter:
            return self.filtered_contacts
        return self.contacts
    
    def get_contact(self, index: int) -> Optional[Contact]:
        """الحصول على جهة اتصال محددة"""
        if 0 <= index < len(self.contacts):
            return self.contacts[index]
        return None
    
    def clear(self):
        """مسح جميع جهات الاتصال"""
        self.contacts.clear()
        self.filtered_contacts.clear()
        self.current_filter = ""
        self._update_stats()

# إنشاء نسخة عامة من مدير جهات الاتصال
contact_manager = ContactManager()