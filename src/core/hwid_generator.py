# app/core/hwid_generator.py
"""
مولد معرف الجهاز الفريد - لإنشاء وتتبع معرفات الأجهزة
"""

import hashlib
import platform
import subprocess
import uuid
import psutil
import json
import logging
from cryptography.fernet import Fernet
import base64

class HWIDGenerator:
    @staticmethod
    def generate():
        """إنشاء معرف جهاز فريد"""
        try:
            # جمع معلومات النظام
            system_info = {
                'machine': platform.machine(),
                'processor': platform.processor(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'node': platform.node(),
                'mac_address': HWIDGenerator._get_mac_address(),
                'cpu_info': HWIDGenerator._get_cpu_info(),
                'disk_info': HWIDGenerator._get_disk_info(),
                'bios_info': HWIDGenerator._get_bios_info()
            }
            
            # تحويل المعلومات إلى سلسلة
            info_string = json.dumps(system_info, sort_keys=True)
            
            # إنشاء الهاش
            hwid_hash = hashlib.sha256(info_string.encode()).hexdigest()
            
            # إضافة بعض التخصيص
            final_hwid = f"WS-{hwid_hash[:8]}-{hwid_hash[8:16]}-{hwid_hash[16:24]}-{hwid_hash[24:32]}"
            
            return final_hwid
            
        except Exception as e:
            logging.getLogger(__name__).error(f"خطأ في إنشاء HWID: {e}")
            # معرف افتراضي في حالة الخطأ
            return f"WS-{uuid.uuid4().hex[:32].upper()}"
    
    @staticmethod
    def _get_mac_address():
        """الحصول على عنوان MAC"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 8*6, 8)][::-1])
            return mac
        except:
            return "00:00:00:00:00:00"
    
    @staticmethod
    def _get_cpu_info():
        """الحصول على معلومات المعالج"""
        try:
            cpu_info = {}
            
            if platform.system() == "Windows":
                output = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode()
                cpu_info['processor_id'] = output.strip().split('\n')[-1]
            elif platform.system() == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('serial'):
                            cpu_info['serial'] = line.split(':')[1].strip()
            
            cpu_info['cores'] = psutil.cpu_count(logical=False)
            cpu_info['logical_cores'] = psutil.cpu_count(logical=True)
            cpu_info['frequency'] = psutil.cpu_freq().current if psutil.cpu_freq() else None
            
            return cpu_info
            
        except:
            return {"cores": 0, "logical_cores": 0}
    
    @staticmethod
    def _get_disk_info():
        """الحصول على معلومات القرص الصلب"""
        try:
            disk_info = {}
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'total': usage.total,
                        'serial': HWIDGenerator._get_disk_serial(partition.device)
                    }
                except:
                    continue
            
            return disk_info
            
        except:
            return {}
    
    @staticmethod
    def _get_disk_serial(device):
        """الحصول على الرقم التسلسلي للقرص"""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    f"wmic diskdrive where deviceid='{device}' get serialnumber",
                    shell=True
                ).decode()
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
            elif platform.system() == "Linux":
                output = subprocess.check_output(
                    f"udevadm info --query=property --name={device} | grep ID_SERIAL",
                    shell=True
                ).decode()
                if output:
                    return output.split('=')[1].strip()
            
            return "Unknown"
        except:
            return "Unknown"
    
    @staticmethod
    def _get_bios_info():
        """الحصول على معلومات BIOS"""
        try:
            bios_info = {}
            
            if platform.system() == "Windows":
                output = subprocess.check_output("wmic bios get serialnumber", shell=True).decode()
                bios_info['serial'] = output.strip().split('\n')[-1]
                
                output = subprocess.check_output("wmic bios get version", shell=True).decode()
                bios_info['version'] = output.strip().split('\n')[-1]
            
            return bios_info
            
        except:
            return {}
    
    @staticmethod
    def encrypt_hwid(hwid, key):
        """تشفير HWID"""
        try:
            fernet = Fernet(key)
            encrypted = fernet.encrypt(hwid.encode())
            return encrypted.decode()
        except:
            return hwid
    
    @staticmethod
    def decrypt_hwid(encrypted_hwid, key):
        """فك تشفير HWID"""
        try:
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted_hwid.encode())
            return decrypted.decode()
        except:
            return encrypted_hwid