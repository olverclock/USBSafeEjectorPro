"""
USB Safe Ejector Pro - v7.3 ULTRA FAST
✅ Montagem com atribuição de letra automática
✅ Abrir no Explorer (botão direito)
✅ Barra de progresso visível desde o início (sem piscar)
✅ MODO RÁPIDO (padrão): Ejeção instantânea como Windows nativo
✅ MODO SEGURO (opcional): Ejeção com verificações completas
✅ Toggle ⚡/🛡 na barra de título para alternar modos
"""

import customtkinter as ctk
import threading
import time
import sys
import ctypes
from typing import List, Dict, Optional, Tuple, Set
import logging
import subprocess
import re
import os

# Importações Windows
try:
    import win32file
    import win32api
    import win32con
    import win32gui
    import pywintypes
    import winerror
    import psutil
    import pythoncom
    import win32com.client
except ImportError:
    print("Erro: pip install customtkinter pywin32 psutil")
    sys.exit(1)

try:
    from CTkMessagebox import CTkMessagebox
except ImportError:
    print("Erro: pip install CTkMessagebox")
    sys.exit(1)

# Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("usb_ejector.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# =========================
# DESIGN SYSTEM PREMIUM
# =========================

class DesignSystem:
    """Design System Windows 11"""
    
    class Colors:
        class Light:
            BG_PRIMARY = "#ffffff"
            BG_SECONDARY = "#f8f8f8"
            BG_TERTIARY = "#ececec"
            BORDER = "#e0e0e0"
            BORDER_FOCUS = "#d0d0d0"
            ACTION_PRIMARY = "#0067c0"
            ACTION_DANGER = "#d32f2f"
            ACTION_WARNING = "#f9a825"
            TEXT_PRIMARY = "#1a1a1a"
            TEXT_SECONDARY = "#666666"
            TEXT_TERTIARY = "#999999"
            PROGRESS_BG = "#e8e8e8"
            PROGRESS_FILL = "#0067c0"
            SPACE_OK = "#0067c0"
            SPACE_WARNING = "#f9a825"
            SPACE_CRITICAL = "#d32f2f"
            SPACE_FREE = "#e8e8e8"
        
        class Dark:
            BG_PRIMARY = "#0f0f0f"
            BG_SECONDARY = "#1a1a1a"
            BG_TERTIARY = "#252525"
            BORDER = "#2a2a2a"
            BORDER_FOCUS = "#3a3a3a"
            ACTION_PRIMARY = "#1e88e5"
            ACTION_DANGER = "#e53935"
            ACTION_WARNING = "#ffa726"
            TEXT_PRIMARY = "#ffffff"
            TEXT_SECONDARY = "#b0b0b0"
            TEXT_TERTIARY = "#808080"
            PROGRESS_BG = "#2a2a2a"
            PROGRESS_FILL = "#1e88e5"
            SPACE_OK = "#1e88e5"
            SPACE_WARNING = "#ffa726"
            SPACE_CRITICAL = "#e53935"
            SPACE_FREE = "#2a2a2a"
    
    SPACE_XS = 4
    SPACE_SM = 6
    SPACE_MD = 8
    SPACE_LG = 12
    SPACE_XL = 16
    RADIUS_SM = 4
    RADIUS_MD = 6
    RADIUS_LG = 8
    RADIUS_FULL = 999
    
    @staticmethod
    def get_fonts():
        return {
            'title': ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            'body': ctk.CTkFont(family="Segoe UI", size=10),
            'small': ctk.CTkFont(family="Segoe UI", size=9),
            'micro': ctk.CTkFont(family="Segoe UI", size=8),
            'icon': ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            'icon_small': ctk.CTkFont(family="Segoe UI", size=12),
        }
    
    ANIM_FAST = 150
    ANIM_NORMAL = 250
    ANIM_SLOW = 350


# Constantes Windows
IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808
IOCTL_STORAGE_MEDIA_REMOVAL = 0x002D4804
FSCTL_LOCK_VOLUME = 0x00090018
FSCTL_DISMOUNT_VOLUME = 0x00090020
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3

DRIVE_UNKNOWN = 0
DRIVE_NO_ROOT_DIR = 1
DRIVE_REMOVABLE = 2
DRIVE_FIXED = 3
DRIVE_REMOTE = 4
DRIVE_CDROM = 5
DRIVE_RAMDISK = 6


# =========================
# CORE / DOMAIN
# =========================

class USBDevice:
    """Modelo de dispositivo USB"""
    
    def __init__(self, letter: str, label: str, filesystem: str,
                 total_size: int, free_size: int, source: str, 
                 is_mounted: bool = True, disk_index: int = -1):
        self.letter = letter
        self.label = label or "Dispositivo USB"
        self.filesystem = filesystem or "FAT32"
        self.total_size = total_size
        self.free_size = free_size
        self.used_size = max(total_size - free_size, 0)
        self.source = source
        self.is_mounted = is_mounted
        self.disk_index = disk_index

    def get_size_gb(self) -> str:
        if self.total_size == 0:
            return "0 GB"
        gb = self.total_size / (1024 ** 3)
        return f"{gb:.1f} GB" if gb >= 1 else f"{self.total_size / (1024**2):.0f} MB"
    
    def get_free_gb(self) -> str:
        if self.free_size == 0:
            return "0 GB"
        gb = self.free_size / (1024 ** 3)
        return f"{gb:.1f} GB" if gb >= 1 else f"{self.free_size / (1024**2):.0f} MB"
    
    def get_used_gb(self) -> str:
        if self.used_size == 0:
            return "0 GB"
        gb = self.used_size / (1024 ** 3)
        return f"{gb:.1f} GB" if gb >= 1 else f"{self.used_size / (1024**2):.0f} MB"
    
    def get_usage_percent(self) -> int:
        if self.total_size == 0:
            return 0
        return int((self.used_size / self.total_size) * 100)
    
    def get_usage_color(self, theme) -> str:
        percent = self.get_usage_percent()
        if percent >= 90:
            return theme.SPACE_CRITICAL
        elif percent >= 80:
            return theme.SPACE_WARNING
        else:
            return theme.SPACE_OK


class ProcessInfo:
    """Processo bloqueador"""
    
    def __init__(self, pid: int, name: str, path: str, files: List[str]):
        self.pid = pid
        self.name = name
        self.path = path
        self.files = files


# =========================
# SERVICES / SYSTEM
# =========================

class USBEjector:
    """Serviço de ejeção USB"""

    @staticmethod
    def is_admin() -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception as e:
            logger.debug(f"Erro admin: {e}")
            return False

    @staticmethod
    def run_as_admin():
        try:
            if sys.platform == "win32":
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
        except Exception as e:
            logger.error(f"Erro run admin: {e}")

    @staticmethod
    def is_valid_physical_drive(letter: str) -> bool:
        drive_path = f"{letter}:\\"
        try:
            drive_type = win32file.GetDriveType(drive_path)
            if drive_type in (DRIVE_REMOTE, DRIVE_CDROM, DRIVE_RAMDISK, DRIVE_UNKNOWN, DRIVE_NO_ROOT_DIR):
                return False
            try:
                volume_info = win32api.GetVolumeInformation(drive_path)
                if not volume_info:
                    return False
            except Exception:
                return False
            try:
                free_bytes, total_bytes = win32api.GetDiskFreeSpaceEx(drive_path)[0:2]
                if total_bytes == 0:
                    return False
            except Exception:
                return False
            try:
                for part in psutil.disk_partitions(all=False):
                    if part.device.upper().startswith(letter):
                        opts_lower = part.opts.lower()
                        if any(x in opts_lower for x in ['network', 'remote', 'cdrom']):
                            return False
                        if 'rw' in opts_lower and 'removable' not in opts_lower and 'fixed' not in opts_lower:
                            fs = part.fstype.lower()
                            if fs in ['fuse', 'winfsp', 'dokan', 'webdav']:
                                return False
            except Exception:
                pass
            return True
        except Exception:
            return False

    @staticmethod
    def get_usb_letters_wmi() -> Set[str]:
        usb_letters: Set[str] = set()
        try:
            pythoncom.CoInitialize()
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            svc = wmi.ConnectServer(".", "root\\cimv2")
            query = "SELECT * FROM Win32_DiskDrive WHERE InterfaceType='USB' AND MediaType='Removable Media'"
            
            for disk in svc.ExecQuery(query):
                disk_id = disk.DeviceID.replace("\\", "\\\\")
                query_parts = f"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{disk_id}'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition"
                
                for partition in svc.ExecQuery(query_parts):
                    part_id = partition.DeviceID.replace("\\", "\\\\")
                    query_logical = f"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{part_id}'}} WHERE AssocClass=Win32_LogicalDiskToPartition"
                    
                    for logical in svc.ExecQuery(query_logical):
                        letter = logical.DeviceID
                        if letter and len(letter) >= 1:
                            letter_only = letter[0].upper()
                            if USBEjector.is_valid_physical_drive(letter_only):
                                usb_letters.add(letter_only)
            
            pythoncom.CoUninitialize()
        except Exception as e:
            logger.debug(f"WMI error: {e}")
        
        return usb_letters

    @staticmethod
    def get_usb_letters_psutil() -> Set[str]:
        usb_letters: Set[str] = set()
        try:
            for partition in psutil.disk_partitions(all=False):
                drive_letter = partition.device[0].upper() if partition.device else None
                if not drive_letter or drive_letter == 'C':
                    continue
                if 'removable' in partition.opts.lower():
                    if USBEjector.is_valid_physical_drive(drive_letter):
                        usb_letters.add(drive_letter)
        except Exception as e:
            logger.debug(f"psutil error: {e}")
        
        return usb_letters

    @staticmethod
    def get_usb_letters_fallback() -> Set[str]:
        usb_letters: Set[str] = set()
        try:
            drives = win32api.GetLogicalDriveStrings()
            for drive in drives.split('\x00')[:-1]:
                if len(drive) < 2:
                    continue
                letter = drive[0].upper()
                if letter == 'C':
                    continue
                try:
                    if win32file.GetDriveType(f"{letter}:\\") == DRIVE_REMOVABLE:
                        if USBEjector.is_valid_physical_drive(letter):
                            usb_letters.add(letter)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Fallback error: {e}")
        
        return usb_letters

    @staticmethod
    def get_removable_drives() -> List[USBDevice]:
        all_usb_letters: Set[str] = set()
        
        try:
            all_usb_letters.update(USBEjector.get_usb_letters_wmi())
        except Exception:
            pass
        try:
            all_usb_letters.update(USBEjector.get_usb_letters_psutil())
        except Exception:
            pass
        try:
            all_usb_letters.update(USBEjector.get_usb_letters_fallback())
        except Exception:
            pass
        
        devices: Dict[str, USBDevice] = {}
        for letter in all_usb_letters:
            if not USBEjector.is_valid_physical_drive(letter):
                continue
            device = USBEjector._build_device(letter, source="USB")
            if device and device.total_size > 0:
                devices[letter] = device
        
        return list(devices.values())

    @staticmethod
    def get_unmounted_usb_drives() -> List[USBDevice]:
        """Detecção USB não montados"""
        unmounted = []
        mounted_indices = set()
        
        try:
            pythoncom.CoInitialize()
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            svc = wmi.ConnectServer(".", "root\\cimv2")
            
            query = "SELECT * FROM Win32_DiskDrive WHERE InterfaceType='USB'"
            for disk in svc.ExecQuery(query):
                try:
                    disk_id = disk.DeviceID.replace("\\", "\\\\")
                    disk_index = int(disk.Index) if disk.Index else -1
                    
                    query_parts = f"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{disk_id}'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition"
                    partitions = list(svc.ExecQuery(query_parts))
                    
                    if partitions:
                        for partition in partitions:
                            part_id = partition.DeviceID.replace("\\", "\\\\")
                            query_logical = f"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{part_id}'}} WHERE AssocClass=Win32_LogicalDiskToPartition"
                            logical_disks = list(svc.ExecQuery(query_logical))
                            if logical_disks:
                                mounted_indices.add(disk_index)
                                break
                except Exception as e:
                    logger.debug(f"Erro processar disco: {e}")
                    continue
            
            logger.info(f"🔍 Discos montados (WMI): {mounted_indices}")
            
            for disk in svc.ExecQuery(query):
                try:
                    disk_index = int(disk.Index) if disk.Index else -1
                    
                    if disk_index not in mounted_indices:
                        size_bytes = int(disk.Size) if disk.Size else 0
                        model = disk.Model if disk.Model else "USB Drive"
                        
                        logger.info(f"🔴 USB NÃO MONTADO (WMI): {model} ({size_bytes / (1024**3):.2f} GB)")
                        
                        device = USBDevice(
                            letter="?", label=model, filesystem="Não montado",
                            total_size=size_bytes, free_size=0, source="USB",
                            is_mounted=False, disk_index=disk_index
                        )
                        unmounted.append(device)
                except Exception as e:
                    logger.debug(f"Erro processar não montado: {e}")
                    continue
            
            pythoncom.CoUninitialize()
        
        except Exception as e:
            logger.warning(f"⚠️ WMI falhou: {e}")
        
        if not unmounted:
            logger.info("🔧 Tentando diskpart...")
            unmounted.extend(USBEjector._detect_via_diskpart())
        
        if not unmounted:
            logger.info("🔧 Tentando ctypes...")
            unmounted.extend(USBEjector._detect_via_ctypes())
        
        logger.info(f"📊 Total não montados: {len(unmounted)}")
        return unmounted

    @staticmethod
    def _detect_via_diskpart() -> List[USBDevice]:
        """Detectar via diskpart"""
        unmounted = []
        try:
            script = "list disk\n"
            result = subprocess.run(
                ["diskpart"], input=script.encode(), 
                capture_output=True, timeout=10, text=False
            )
            
            output = result.stdout.decode('cp850', errors='ignore')
            logger.info(f"📋 Diskpart:\n{output}")
            
            lines = output.split('\n')
            for line in lines:
                match = re.match(r'\s+Disk\s+(\d+)\s+(\w+)\s+(\d+\s+\w+)', line.strip())
                if match:
                    disk_num = int(match.group(1))
                    status = match.group(2)
                    size_str = match.group(3)
                    
                    if status.lower() not in ['online']:
                        if USBEjector._is_usb_disk(disk_num):
                            size_bytes = USBEjector._parse_size(size_str)
                            device = USBDevice(
                                letter="?", label=f"Disk {disk_num}", filesystem="Não montado",
                                total_size=size_bytes, free_size=0, source="USB",
                                is_mounted=False, disk_index=disk_num
                            )
                            unmounted.append(device)
                            logger.info(f"✅ USB via diskpart: Disk {disk_num}")
        
        except Exception as e:
            logger.error(f"❌ Erro diskpart: {e}")
        
        return unmounted

    @staticmethod
    def _detect_via_ctypes() -> List[USBDevice]:
        """Detectar via ctypes"""
        unmounted = []
        try:
            for i in range(10):
                drive_name = f"PhysicalDrive{i}"
                target = (ctypes.c_wchar * 32768)()
                target_len = ctypes.windll.kernel32.QueryDosDeviceW(drive_name, target, len(target))
                
                if target_len:
                    if USBEjector._is_usb_disk(i):
                        if not USBEjector._is_disk_mounted(i):
                            device = USBDevice(
                                letter="?", label=f"PhysicalDrive{i}", filesystem="Não montado",
                                total_size=0, free_size=0, source="USB",
                                is_mounted=False, disk_index=i
                            )
                            unmounted.append(device)
                            logger.info(f"✅ USB via ctypes: {drive_name}")
        
        except Exception as e:
            logger.error(f"❌ Erro ctypes: {e}")
        
        return unmounted

    @staticmethod
    def _is_usb_disk(disk_index: int) -> bool:
        """Verificar se é USB"""
        try:
            pythoncom.CoInitialize()
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            svc = wmi.ConnectServer(".", "root\\cimv2")
            query = f"SELECT * FROM Win32_DiskDrive WHERE Index={disk_index} AND InterfaceType='USB'"
            result = list(svc.ExecQuery(query))
            pythoncom.CoUninitialize()
            return len(result) > 0
        except Exception:
            return False

    @staticmethod
    def _is_disk_mounted(disk_index: int) -> bool:
        """Verificar se tem letra"""
        try:
            pythoncom.CoInitialize()
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            svc = wmi.ConnectServer(".", "root\\cimv2")
            disk_id = f"\\\\.\\PHYSICALDRIVE{disk_index}"
            disk_id_escaped = disk_id.replace("\\", "\\\\")
            query_parts = f"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{disk_id_escaped}'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition"
            
            for partition in svc.ExecQuery(query_parts):
                part_id = partition.DeviceID.replace("\\", "\\\\")
                query_logical = f"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{part_id}'}} WHERE AssocClass=Win32_LogicalDiskToPartition"
                logical = list(svc.ExecQuery(query_logical))
                if logical:
                    pythoncom.CoUninitialize()
                    return True
            
            pythoncom.CoUninitialize()
            return False
        except Exception:
            return False

    @staticmethod
    def _parse_size(size_str: str) -> int:
        """Parser tamanho diskpart"""
        try:
            parts = size_str.strip().split()
            if len(parts) != 2:
                return 0
            value = float(parts[0])
            unit = parts[1].upper()
            
            multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
            return int(value * multipliers.get(unit, 0))
        except Exception:
            return 0

    @staticmethod
    def mount_drive(device: USBDevice) -> Tuple[bool, str]:
        """🔧 MONTAGEM PROFISSIONAL com atribuição de letra automática"""
        try:
            logger.info(f"🔧 Montando disco {device.disk_index}...")
            
            # Script diskpart para online + atribuir letra automaticamente
            script = f"""select disk {device.disk_index}
online disk
attributes disk clear readonly
rescan
"""
            
            # Executar diskpart
            result = subprocess.run(
                ["diskpart"], 
                input=script.encode('utf-8'), 
                capture_output=True, 
                timeout=15
            )
            
            output = result.stdout.decode('cp850', errors='ignore')
            logger.info(f"📋 Diskpart output:\n{output}")
            
            # Aguardar Windows atribuir letra
            time.sleep(0.1)
            
            # Verificar se apareceu letra
            new_letter = USBEjector._get_disk_letter(device.disk_index)
            if new_letter:
                logger.info(f"✅ Drive montado com sucesso: {new_letter}:")
                return True, f"Montado como {new_letter}:"
            else:
                logger.warning("⚠️ Drive online mas sem letra. Tentando atribuir...")
                # Tentar atribuir letra manualmente
                letter = USBEjector._assign_drive_letter(device.disk_index)
                if letter:
                    return True, f"Montado como {letter}:"
                else:
                    return False, "Não foi possível atribuir letra"
        
        except Exception as e:
            logger.error(f"❌ Erro ao montar: {e}")
            return False, f"Erro: {str(e)}"

    @staticmethod
    def _get_disk_letter(disk_index: int) -> Optional[str]:
        """Obter letra de disco físico"""
        try:
            pythoncom.CoInitialize()
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            svc = wmi.ConnectServer(".", "root\\cimv2")
            
            disk_id = f"\\\\.\\PHYSICALDRIVE{disk_index}"
            disk_id_escaped = disk_id.replace("\\", "\\\\")
            query_parts = f"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{disk_id_escaped}'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition"
            
            for partition in svc.ExecQuery(query_parts):
                part_id = partition.DeviceID.replace("\\", "\\\\")
                query_logical = f"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{part_id}'}} WHERE AssocClass=Win32_LogicalDiskToPartition"
                
                for logical in svc.ExecQuery(query_logical):
                    letter = logical.DeviceID
                    if letter and len(letter) >= 1:
                        pythoncom.CoUninitialize()
                        return letter[0].upper()
            
            pythoncom.CoUninitialize()
            return None
        except Exception as e:
            logger.debug(f"Erro get letter: {e}")
            return None

    @staticmethod
    def _assign_drive_letter(disk_index: int) -> Optional[str]:
        """Atribuir letra automaticamente"""
        try:
            # Encontrar primeira letra disponível
            used_letters = set()
            drives = win32api.GetLogicalDriveStrings()
            for drive in drives.split('\x00')[:-1]:
                if len(drive) >= 1:
                    used_letters.add(drive[0].upper())
            
            # Letras possíveis (D-Z)
            for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
                if letter not in used_letters:
                    # Tentar atribuir via diskpart
                    script = f"""select disk {disk_index}
select partition 1
assign letter={letter}
"""
                    result = subprocess.run(
                        ["diskpart"], 
                        input=script.encode('utf-8'), 
                        capture_output=True, 
                        timeout=10
                    )
                    time.sleep(0.1)
                    
                    # Verificar se funcionou
                    if os.path.exists(f"{letter}:\\"):
                        logger.info(f"✅ Letra {letter}: atribuída")
                        return letter
            
            return None
        except Exception as e:
            logger.error(f"❌ Erro assign letter: {e}")
            return None

    @staticmethod
    def _build_device(letter: str, source: str) -> Optional[USBDevice]:
        drive = f"{letter}:\\"
        try:
            label = "Dispositivo USB"
            filesystem = "FAT32"
            total_bytes = 0
            free_bytes = 0
            
            try:
                volume_info = win32api.GetVolumeInformation(drive)
                if volume_info and volume_info[0]:
                    label = volume_info[0].strip()
                if volume_info and len(volume_info) > 4 and volume_info[4]:
                    filesystem = volume_info[4]
            except Exception:
                return None
            
            try:
                disk_space = win32api.GetDiskFreeSpaceEx(drive)
                free_bytes = disk_space[0]
                total_bytes = disk_space[1]
                if total_bytes == 0:
                    return None
            except Exception:
                return None
            
            if not label or label.strip() == "":
                label = f"Removível ({letter}:)"
            
            return USBDevice(letter, label, filesystem, total_bytes, free_bytes, source, is_mounted=True)
        except Exception:
            return None

    @staticmethod
    def find_locking_processes(drive_letter: str) -> List[ProcessInfo]:
        locking_processes: List[ProcessInfo] = []
        drive_path = f"{drive_letter.upper()}:\\"
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe'], ad_value=None):
                try:
                    info = proc.info
                    pid = info.get('pid')
                    name = info.get('name') or "Desconhecido"
                    exe = info.get('exe') or ""
                    open_files: List[str] = []
                    
                    try:
                        for f in proc.open_files():
                            if f.path.upper().startswith(drive_path.upper()):
                                open_files.append(f.path)
                                break
                    except Exception:
                        pass
                    
                    if exe and exe.upper().startswith(drive_path.upper()):
                        open_files.append(exe)
                    
                    if open_files:
                        locking_processes.append(ProcessInfo(pid, name, exe, open_files))
                
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"Erro processos: {e}")
        
        return locking_processes

    @staticmethod
    def verify_safe_to_eject(drive_letter: str) -> Tuple[bool, str, List[ProcessInfo]]:
        logger.info(f"🔍 Verificando {drive_letter}:")
        
        if not USBEjector.is_valid_physical_drive(drive_letter):
            return False, "Inacessível", []
        
        procs = USBEjector.find_locking_processes(drive_letter)
        if procs:
            logger.warning(f"⚠️ {len(procs)} processo(s) bloqueando")
            return False, f"{len(procs)} processo(s)", procs
        
        logger.info("✓ Seguro")
        return True, "Seguro", []

    @staticmethod
    def kill_process(pid: int) -> bool:
        try:
            process = psutil.Process(pid)
            process.terminate()
            try:
                process.wait(timeout=1)
                return True
            except Exception:
                process.kill()
                return True
        except Exception as e:
            logger.debug(f"Erro kill {pid}: {e}")
            return False

    @staticmethod
    def eject_drive(drive_letter: str, progress_callback=None, safe_mode: bool = False) -> Tuple[bool, str]:
        logger.info(f"⏏ Ejetando {drive_letter}: ({'SEGURO' if safe_mode else 'RÁPIDO'})")
        volume_path = f"\\\\.\\{drive_letter}:"
        
        try:
            handle = win32file.CreateFile(
                volume_path, GENERIC_READ | GENERIC_WRITE, 
                FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, None
            )
            
            try:
                if safe_mode:
                    # MODO SEGURO: Todas operações
                    logger.info("  1️⃣ □ Cache...")
                if progress_callback:
                    progress_callback(20)
                try:
                    win32file.FlushFileBuffers(handle)
                    logger.info("     ✓ Cache")
                except Exception:
                    pass
                
                logger.info("  2️⃣ □ Bloqueio...")
                if progress_callback:
                    progress_callback(40)
                try:
                    win32file.DeviceIoControl(handle, IOCTL_STORAGE_MEDIA_REMOVAL, b"\x00", None)
                    logger.info("     ✓ Bloqueio")
                except Exception:
                    pass
                
                logger.info("  3️⃣ □ Lock...")
                if progress_callback:
                    progress_callback(60)
                try:
                    win32file.DeviceIoControl(handle, FSCTL_LOCK_VOLUME, None, None)
                    logger.info("     ✓ Lock")
                except Exception:
                    pass
                
                logger.info("  4️⃣ □ Dismount...")
                if progress_callback:
                    progress_callback(80)
                try:
                    win32file.DeviceIoControl(handle, FSCTL_DISMOUNT_VOLUME, None, None)
                    logger.info("     ✓ Dismount")
                except Exception:
                    pass
                
                else:
                    # MODO RÁPIDO: Apenas dismount
                    logger.info("  ⚡ Dismount rápido...")
                    if progress_callback:
                        progress_callback(50)
                    try:
                        win32file.DeviceIoControl(handle, FSCTL_DISMOUNT_VOLUME, None, None)
                        logger.info("     ✓ Dismount")
                    except Exception:
                        pass

                # Ejeção final (ambos modos)
                logger.info("  ⏏ Ejetando...")
                if progress_callback:
                    progress_callback(90)
                win32file.DeviceIoControl(handle, IOCTL_STORAGE_EJECT_MEDIA, None, None)
                logger.info("     ✓ Ejetado")
                
                if progress_callback:
                    progress_callback(100)
                
                msg = f"✓ {drive_letter}: removido"
                logger.info(msg)
                return True, msg
            
            finally:
                win32file.CloseHandle(handle)
        
        except pywintypes.error as e:
            code = e.winerror
            if code == winerror.ERROR_SHARING_VIOLATION:
                return False, "Em uso"
            elif code == winerror.ERROR_ACCESS_DENIED:
                return False, "Acesso negado"
            else:
                return False, f"Erro {code}"
        except Exception as e:
            logger.error(f"Erro ejeção: {e}")
            return False, "Erro"


class USBDeviceMonitor:
    """Monitor USB"""
    
    def __init__(self, callback):
        self.callback = callback
        self.hwnd = None
        self.running = False

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()

    def stop(self):
        self.running = False
        if self.hwnd:
            try:
                win32gui.DestroyWindow(self.hwnd)
            except Exception:
                pass

    def _monitor_loop(self):
        try:
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._wnd_proc
            wc.lpszClassName = "USBMonitorClass"
            wc.hInstance = win32api.GetModuleHandle(None)
            class_atom = win32gui.RegisterClass(wc)
            self.hwnd = win32gui.CreateWindow(
                class_atom, "USBMonitor", 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
            )
            win32gui.PumpMessages()
        except Exception as e:
            logger.debug(f"Monitor error: {e}")

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DEVICECHANGE:
            if wparam in (0x8000, 0x8004):
                threading.Timer(0.3, self.callback).start()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


# =========================
# UI COMPONENTS
# =========================

class SpaceCanvas(ctk.CTkCanvas):
    """Gráfico circular"""
    
    def __init__(self, master, device: USBDevice, theme, **kwargs):
        super().__init__(
            master, width=32, height=32, 
            bg=theme.BG_SECONDARY, highlightthickness=0, **kwargs
        )
        self.device = device
        self.theme = theme
        self.draw_chart()
    
    def draw_chart(self):
        self.delete("all")
        size = 32
        cx, cy = size // 2, size // 2
        radius = 12
        
        usage_percent = self.device.get_usage_percent()
        usage_color = self.device.get_usage_color(self.theme)
        
        self.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            fill=self.theme.SPACE_FREE, outline=""
        )
        
        if usage_percent > 0:
            extent = -360 * (usage_percent / 100)
            self.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=90, extent=extent, fill=usage_color, outline=""
            )
        
        inner_r = 7
        self.create_oval(
            cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r,
            fill=self.theme.BG_SECONDARY, outline=""
        )
        
        self.create_text(
            cx, cy, text=f"{usage_percent}%",
            fill=self.theme.TEXT_PRIMARY,
            font=("Segoe UI", 7, "bold")
        )


# =========================
# UI SCREENS
# =========================

class PremiumUSBEjectorGUI:
    """Interface Premium COMPLETA"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.overrideredirect(True)
        
        w, h = 290, 320
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        # Posição EXATA: canto inferior direito, encostado nas bordas
        x = sw - w  # Sem margem - encostado na borda direita
        y = sh - h - 40  # 40px acima (altura da barra de tarefas do Windows)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.update()
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.is_dark = True  # Modo escuro inicial
        self.theme = DesignSystem.Colors.Dark  # Tema escuro
        self.fonts = DesignSystem.get_fonts()
        ctk.set_appearance_mode("dark")  # Aparência escura

        self.devices: List[USBDevice] = []
        self.usb_monitor = USBDeviceMonitor(callback=self.on_usb_change)
        self.ejecting_drives: Set[str] = set()
        self.eject_progress: Dict[str, int] = {}
        self.progress_bars: Dict[str, ctk.CTkFrame] = {}
        self.progress_containers: Dict[str, ctk.CTkFrame] = {}  # 🔥 NOVO: containers
        self.last_click_time: Dict[str, float] = {}
        self.show_unmounted = False
        self.safe_eject_mode = False  # Modo rápido padrão
        self.safe_eject_mode = False  # Modo rápido padrão  # 🚀 Modo rápido por padrão
        
        
        self.drag_x = 0
        self.drag_y = 0

        self.setup_ui()
        self.refresh_devices()
        self.usb_monitor.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.usb_monitor.stop()
        self.root.destroy()

    def on_usb_change(self):
        self.root.after(0, self.refresh_devices)

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme = DesignSystem.Colors.Dark if self.is_dark else DesignSystem.Colors.Light
        ctk.set_appearance_mode("dark" if self.is_dark else "light")
        self.refresh_ui()

    def toggle_unmounted(self):
        """Mostrar/ocultar dispositivos não montados"""
        self.show_unmounted = not self.show_unmounted
        logger.info(f"👁 Mostrar não montados: {self.show_unmounted}")
        self.refresh_devices()

    def toggle_theme(self):
        """Alternar tema claro/escuro"""
        self.is_dark = not self.is_dark
        self.theme = DesignSystem.Colors.Dark if self.is_dark else DesignSystem.Colors.Light
        ctk.set_appearance_mode("dark" if self.is_dark else "light")
        self.refresh_ui()


    def toggle_eject_mode(self):
        """⚡ Alternar entre modo rápido e seguro"""
        self.safe_eject_mode = not self.safe_eject_mode
        mode = "SEGURO" if self.safe_eject_mode else "RÁPIDO"
        logger.info(f"⚡ Modo: {mode}")
        self.refresh_devices()

    def refresh_ui(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.setup_ui()
        self.refresh_devices()

    def start_drag(self, e):
        self.drag_x = e.x
        self.drag_y = e.y

    def do_drag(self, e):
        x = self.root.winfo_x() + e.x - self.drag_x
        y = self.root.winfo_y() + e.y - self.drag_y
        self.root.geometry(f"+{x}+{y}")

    def setup_ui(self):
        main = ctk.CTkFrame(
            self.root, fg_color=self.theme.BG_PRIMARY,
            corner_radius=8, border_width=1, border_color=self.theme.BORDER
        )
        main.pack(fill="both", expand=True)
        
        self.create_titlebar(main)
        if not USBEjector.is_admin():
            self.create_admin_banner(main)
        self.create_devices_container(main)

    def create_titlebar(self, parent):
        bar = ctk.CTkFrame(
            parent, fg_color=self.theme.BG_SECONDARY, 
            height=32, corner_radius=0
        )
        bar.pack(fill="x")
        bar.pack_propagate(False)
        bar.bind("<Button-1>", self.start_drag)
        bar.bind("<B1-Motion>", self.do_drag)
        
        title = ctk.CTkLabel(
            bar, text="USB Ejector", 
            font=self.fonts['title'], 
            text_color=self.theme.TEXT_PRIMARY
        )
        title.pack(side="left", padx=DesignSystem.SPACE_LG)
        title.bind("<Button-1>", self.start_drag)
        title.bind("<B1-Motion>", self.do_drag)
        
        controls = ctk.CTkFrame(bar, fg_color="transparent")
        controls.pack(side="right", padx=4)
        
        self._create_control_btn(
            controls, "👁" if self.show_unmounted else "👁‍🗨", 
            self.toggle_unmounted,
            fg=self.theme.ACTION_PRIMARY if self.show_unmounted else "transparent"
        )
        self._create_control_btn(
            controls, "⚡" if not self.safe_eject_mode else "🛡",
            self.toggle_eject_mode,
            fg=self.theme.ACTION_WARNING if self.safe_eject_mode else self.theme.ACTION_PRIMARY
        )
        self._create_control_btn(controls, "🌙" if not self.is_dark else "☀", self.toggle_theme)
        self._create_control_btn(controls, "↻", self.refresh_devices)
        self._create_control_btn(controls, "ℹ️", self.show_about, hover=self.theme.BG_TERTIARY)
        self._create_control_btn(controls, "✕", self.on_closing, hover=self.theme.ACTION_DANGER)

    def _create_control_btn(self, parent, text, cmd, fg="transparent", hover=None):
        btn = ctk.CTkButton(
            parent, text=text, width=24, height=24, corner_radius=4,
            fg_color=fg, hover_color=hover or self.theme.BG_TERTIARY,
            font=self.fonts['icon_small'], 
            text_color=self.theme.TEXT_SECONDARY,
            command=cmd
        )
        btn.pack(side="left", padx=2)
        return btn

    def create_admin_banner(self, parent):
        banner = ctk.CTkFrame(
            parent, fg_color=self.theme.ACTION_WARNING, 
            height=24, corner_radius=0
        )
        banner.pack(fill="x")
        banner.pack_propagate(False)
        
        lbl = ctk.CTkLabel(
            banner, text="⚠ Execute como Admin",
            font=self.fonts['small'], text_color="#000000"
        )
        lbl.pack(expand=True)
        
        for w in [banner, lbl]:
            w.bind("<Button-1>", lambda e: [USBEjector.run_as_admin(), self.root.quit()])
            w.configure(cursor="hand2")

    def create_devices_container(self, parent):
        self.devices_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=self.theme.BG_PRIMARY, corner_radius=0, border_width=0,
            scrollbar_button_color=self.theme.BG_TERTIARY,
            scrollbar_button_hover_color=self.theme.BORDER_FOCUS
        )
        self.devices_scroll.pack(
            fill="both", expand=True, 
            padx=DesignSystem.SPACE_SM, pady=DesignSystem.SPACE_SM
        )

    def refresh_devices(self):
        """🔥 Refresh SEM piscar barra de progresso"""
        for w in self.devices_scroll.winfo_children():
            w.destroy()
        
        # NÃO limpar progress_bars/containers se estiver ejetando
        # (mantém referências para atualização)
        
        self.devices = USBEjector.get_removable_drives()
        unmounted = []
        if self.show_unmounted:
            unmounted = USBEjector.get_unmounted_usb_drives()
        
        all_devs = self.devices + unmounted
        
        if not all_devs:
            self.show_empty_state()
        else:
            for dev in all_devs:
                if dev.is_mounted:
                    self.create_device_card(dev)
                else:
                    self.create_unmounted_card(dev)

    def show_empty_state(self):
        empty = ctk.CTkFrame(self.devices_scroll, fg_color="transparent")
        empty.pack(expand=True, pady=40)
        ctk.CTkLabel(empty, text="🔌", font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(
            empty, text="Nenhum USB", font=self.fonts['small'], 
            text_color=self.theme.TEXT_SECONDARY
        ).pack(pady=(6, 0))

    def create_unmounted_card(self, device: USBDevice):
        """Card USB não montado"""
        card = ctk.CTkFrame(
            self.devices_scroll, fg_color=self.theme.BG_SECONDARY,
            corner_radius=8, border_width=1, border_color=self.theme.BORDER, height=52
        )
        card.pack(fill="x", pady=3)
        card.pack_propagate(False)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=DesignSystem.SPACE_SM, pady=DesignSystem.SPACE_SM)
        
        icon = ctk.CTkFrame(
            content, fg_color="transparent", 
            border_width=2, border_color=self.theme.TEXT_TERTIARY,
            corner_radius=999, width=36, height=36
        )
        icon.pack(side="left")
        icon.pack_propagate(False)
        
        ctk.CTkLabel(
            icon, text="?", font=self.fonts['icon'], 
            text_color=self.theme.TEXT_TERTIARY
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        info = ctk.CTkFrame(content, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=(DesignSystem.SPACE_SM, 0))
        
        ctk.CTkLabel(
            info, text=device.label[:16] if len(device.label) <= 16 else device.label[:13] + "...",
            font=self.fonts['body'], text_color=self.theme.TEXT_SECONDARY, anchor="w"
        ).pack(fill="x", anchor="w")
        
        size_text = f"Não montado • {device.get_size_gb()}" if device.total_size > 0 else "Não montado"
        ctk.CTkLabel(
            info, text=size_text,
            font=self.fonts['micro'], text_color=self.theme.TEXT_TERTIARY, anchor="w"
        ).pack(fill="x", anchor="w")
        
        ctk.CTkButton(
            content, text="📁", width=32, height=32, corner_radius=6,
            fg_color=self.theme.ACTION_PRIMARY, hover_color=self.theme.ACTION_PRIMARY,
            font=self.fonts['icon'], text_color="#ffffff",
            command=lambda: self.mount_device(device)
        ).pack(side="right")

    def mount_device(self, device: USBDevice):
        """Montar USB"""
        def _mount():
            success, msg = USBEjector.mount_drive(device)
            self.root.after(0, lambda: self._handle_mount_result(success, msg, device))
        threading.Thread(target=_mount, daemon=True).start()

    def _handle_mount_result(self, success: bool, msg: str, device: USBDevice):
        if success:
            CTkMessagebox(title="Sucesso", message=f"✓ {device.label}\n\n{msg}", icon="check")
            self.root.after(1500, self.refresh_devices)
        else:
            CTkMessagebox(title="Erro", message=f"Falha:\n{msg}", icon="warning")

    def create_device_card(self, device: USBDevice):
        """🎨 CARD USB MONTADO PREMIUM"""
        is_ejecting = device.letter in self.ejecting_drives
        progress = self.eject_progress.get(device.letter, 0)
        
        card_container = ctk.CTkFrame(self.devices_scroll, fg_color="transparent")
        card_container.pack(fill="x", pady=3)
        
        card = ctk.CTkFrame(
            card_container, fg_color=self.theme.BG_SECONDARY,
            corner_radius=8, border_width=1, border_color=self.theme.BORDER, height=58
        )
        card.pack(fill="x")
        card.pack_propagate(False)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=DesignSystem.SPACE_SM, pady=DesignSystem.SPACE_SM)
        
        # Ícone outline
        icon_frame = ctk.CTkFrame(
            content, fg_color="transparent",
            border_width=2, border_color=self.theme.ACTION_PRIMARY,
            corner_radius=999, width=36, height=36
        )
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_frame, text=device.letter, 
            font=self.fonts['icon'], 
            text_color=self.theme.ACTION_PRIMARY
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Info
        info = ctk.CTkFrame(content, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=(DesignSystem.SPACE_SM, 0))
        
        name_lbl = ctk.CTkLabel(
            info, text=device.label[:16] if len(device.label) <= 16 else device.label[:13] + "...",
            font=self.fonts['body'], text_color=self.theme.TEXT_PRIMARY, anchor="w"
        )
        name_lbl.pack(fill="x", anchor="w")
        
        # Informação progressiva
        usage = device.get_usage_percent()
        meta_text_normal = f"{device.letter}: • {device.get_size_gb()}"
        meta_text_hover = f"{device.get_free_gb()} livre • {usage}% usado"
        
        meta_lbl = ctk.CTkLabel(
            info, text=meta_text_normal,
            font=self.fonts['micro'], 
            text_color=device.get_usage_color(self.theme) if usage >= 80 else self.theme.TEXT_TERTIARY,
            anchor="w"
        )
        meta_lbl.pack(fill="x", anchor="w")
        
        # Gráfico
        SpaceCanvas(content, device, self.theme).pack(side="right", padx=(4, 0))
        
        # Botão ejetar
        eject_btn = ctk.CTkButton(
            content, text="⏏" if not is_ejecting else "⏳",
            width=32, height=32, corner_radius=6, fg_color="transparent",
            hover_color=self.theme.BG_TERTIARY, border_width=1,
            border_color=self.theme.BORDER, font=self.fonts['icon'],
            text_color=self.theme.TEXT_SECONDARY,
            command=lambda: self.eject_device(device)
        )
        eject_btn.pack(side="right", padx=(4, 0))
        
        # 🔥 Barra progresso SEMPRE CRIADA (visível desde início)
        prog_container = ctk.CTkFrame(
            card_container, fg_color=self.theme.PROGRESS_BG, 
            height=2, corner_radius=1
        )
        
        if is_ejecting:
            prog_container.pack(fill="x", pady=(2, 0))
            prog_container.pack_propagate(False)
            
            prog_fill = ctk.CTkFrame(
                prog_container, fg_color=self.theme.PROGRESS_FILL, 
                height=2, corner_radius=1
            )
            prog_fill.place(relx=0, rely=0, relwidth=progress/100, relheight=1)
            
            # Salvar referências
            self.progress_bars[device.letter] = prog_fill
            self.progress_containers[device.letter] = prog_container
        
        # Micro-interações
        def on_double_click(e):
            if device.letter not in self.ejecting_drives:
                self.eject_device(device)
        
        def on_enter(e):
            if device.letter not in self.ejecting_drives:
                card.configure(
                    fg_color=self.theme.BG_TERTIARY, 
                    border_color=self.theme.BORDER_FOCUS,
                    cursor="hand2"
                )
                meta_lbl.configure(text=meta_text_hover)
            elif is_ejecting:
                card.configure(cursor="watch")
        
        def on_leave(e):
            if device.letter not in self.ejecting_drives:
                card.configure(
                    fg_color=self.theme.BG_SECONDARY, 
                    border_color=self.theme.BORDER,
                    cursor=""
                )
                meta_lbl.configure(text=meta_text_normal)
        
        for w in [card, content, info, name_lbl]:
            w.bind("<Double-Button-1>", on_double_click)
            w.bind("<Button-3>", lambda e, d=device: self.show_context_menu(d, e.x_root, e.y_root))
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def update_progress(self, letter: str, progress: int):
        """Atualizar barra SEM redesenhar"""
        self.eject_progress[letter] = progress
        if letter in self.progress_bars:
            try:
                self.progress_bars[letter].place_configure(relwidth=progress/100)
                self.root.update()  # Forçar atualização visual
            except Exception:
                pass

    def eject_device(self, device: USBDevice):
        """🔥 Ejeção SEM PISCAR"""
        letter = device.letter
        now = time.time()
        
        # Debounce
        if letter in self.last_click_time:
            if now - self.last_click_time[letter] < 1.5:
                return
        self.last_click_time[letter] = now
        
        if letter in self.ejecting_drives:
            return
        
        # Marcar como ejetando
        self.ejecting_drives.add(letter)
        self.eject_progress[letter] = 0
        
        # 🔥 Refresh IMEDIATO para mostrar barra desde início
        self.refresh_devices()
        
        def progress_cb(p):
            self.root.after(0, lambda: self.update_progress(letter, p))
        
        def _eject():
            try:
                # MODO RÁPIDO: pula verificação de processos
                if self.safe_eject_mode:
                    safe, msg, procs = USBEjector.verify_safe_to_eject(letter)
                    if not safe and procs:
                        self.root.after(0, lambda: self.show_lock_warning(device, procs))
                        return
                success, result = USBEjector.eject_drive(letter, progress_cb, safe_mode=self.safe_eject_mode)
                self.root.after(0, lambda: self._handle_eject_result(success, result, device))
            finally:
                if letter in self.ejecting_drives:
                    self.ejecting_drives.remove(letter)
                if letter in self.eject_progress:
                    del self.eject_progress[letter]
                if letter in self.progress_bars:
                    del self.progress_bars[letter]
                if letter in self.progress_containers:
                    del self.progress_containers[letter]
                self.root.after(300, self.refresh_devices)
        
        threading.Thread(target=_eject, daemon=True).start()

    def show_context_menu(self, device: USBDevice, x: int, y: int):
        """🎯 MENU CONTEXTO COM EXPLORER"""
        if device.letter in self.ejecting_drives:
            return
        
        menu = ctk.CTkToplevel(self.root)
        menu.overrideredirect(True)
        menu.attributes("-topmost", True)
        menu.geometry(f"180x120+{x}+{y}")  # +30px altura
        menu.configure(fg_color=self.theme.BG_SECONDARY)
        
        frame = ctk.CTkFrame(
            menu, fg_color=self.theme.BG_SECONDARY, corner_radius=6,
            border_width=1, border_color=self.theme.BORDER
        )
        frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # 🆕 OPÇÃO ABRIR NO EXPLORER
        ctk.CTkButton(
            frame, text="📂 Abrir no Explorer", fg_color="transparent", hover_color=self.theme.BG_TERTIARY,
            anchor="w", height=26, font=self.fonts['small'], 
            text_color=self.theme.TEXT_PRIMARY,
            command=lambda: [menu.destroy(), self.open_in_explorer(device)]
        ).pack(fill="x", padx=4, pady=(4, 2))
        
        for txt, cmd in [
            ("Ejetar", lambda: [menu.destroy(), self.eject_device(device)]),
            ("Ver Bloqueios", lambda: [menu.destroy(), self.check_locks(device)]),
            ("Forçar Ejeção", lambda: [menu.destroy(), self.force_eject(device)])
        ]:
            ctk.CTkButton(
                frame, text=txt, fg_color="transparent", hover_color=self.theme.BG_TERTIARY,
                anchor="w", height=26, font=self.fonts['small'], 
                text_color=self.theme.ACTION_WARNING if "Forçar" in txt else self.theme.TEXT_PRIMARY,
                command=cmd
            ).pack(fill="x", padx=4, pady=2)
        
        
        # About - Créditos
        ctk.CTkButton(
            frame, text="ℹ️ About - by olverclock",
            fg_color="transparent",
            hover_color=self.theme.BG_TERTIARY,
            anchor="w", height=26,
            font=self.fonts["small"],
            text_color=self.theme.TEXT_TERTIARY,
            command=lambda: (menu.destroy(), self.show_about())
        ).pack(fill="x", padx=4, pady=(2, 4))

        self.root.after(100, lambda: self.root.bind("<Button-1>", lambda e: menu.destroy()))

    def open_in_explorer(self, device: USBDevice):
        """🆕 Abrir USB no Windows Explorer"""
        try:
            path = f"{device.letter}:\\"
            os.startfile(path)
            logger.info(f"📂 Abrindo {path} no Explorer")
        except Exception as e:
            logger.error(f"❌ Erro ao abrir Explorer: {e}")
            CTkMessagebox(title="Erro", message=f"Não foi possível abrir:\n{str(e)}", icon="warning")

    def check_locks(self, device: USBDevice):
        """Verificar processos"""
        def _check():
            procs = USBEjector.find_locking_processes(device.letter)
            self.root.after(0, lambda: self._show_lock_result(device, procs))
        threading.Thread(target=_check, daemon=True).start()

    def _show_lock_result(self, device: USBDevice, procs: List[ProcessInfo]):
        if not procs:
            CTkMessagebox(title="Verificação", message=f"✓ Nenhum bloqueio\n\nSeguro para ejetar {device.label}", icon="check")
        else:
            self.show_lock_warning(device, procs)

    def show_lock_warning(self, device: USBDevice, procs: List[ProcessInfo]):
        """Diálogo processos"""
        if device.letter in self.ejecting_drives:
            self.ejecting_drives.remove(device.letter)
            self.refresh_devices()
        
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Processos Bloqueando")
        dlg.geometry("320x280")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(fg_color=self.theme.BG_PRIMARY)
        
        ctk.CTkLabel(
            dlg, text=f"⚠ {len(procs)} processo(s) usando {device.letter}:",
            font=self.fonts['body']
        ).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(dlg, fg_color=self.theme.BG_SECONDARY, corner_radius=6)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        for proc in procs:
            pf = ctk.CTkFrame(scroll, fg_color=self.theme.BG_TERTIARY, corner_radius=6)
            pf.pack(fill="x", pady=3)
            
            info = ctk.CTkFrame(pf, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True, padx=8, pady=6)
            
            ctk.CTkLabel(info, text=proc.name, font=self.fonts['small'], anchor="w", text_color=self.theme.TEXT_PRIMARY).pack(fill="x")
            ctk.CTkLabel(info, text=f"PID {proc.pid}", font=self.fonts['micro'], text_color=self.theme.TEXT_TERTIARY, anchor="w").pack(fill="x")
            
            ctk.CTkButton(
                pf, text="✖", width=28, height=28, corner_radius=999,
                fg_color=self.theme.ACTION_DANGER, hover_color="#b01f23",
                font=self.fonts['icon_small'],
                command=lambda p=proc: self._kill_and_retry(p, device, dlg)
            ).pack(side="right", padx=6)
        
        btns = ctk.CTkFrame(dlg, fg_color="transparent")
        btns.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(
            btns, text="Cancelar", height=32, corner_radius=6,
            fg_color=self.theme.BG_TERTIARY, hover_color=self.theme.BORDER_FOCUS,
            font=self.fonts['small'], command=dlg.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        ctk.CTkButton(
            btns, text="Encerrar Tudo", height=32, corner_radius=6,
            fg_color=self.theme.ACTION_DANGER, hover_color="#b01f23",
            font=self.fonts['small'],
            command=lambda: [dlg.destroy(), self._force_eject_all(device, procs)]
        ).pack(side="right", fill="x", expand=True, padx=(4, 0))

    def _kill_and_retry(self, proc: ProcessInfo, device: USBDevice, dlg):
        if USBEjector.kill_process(proc.pid):
            dlg.destroy()
            self.root.after(200, lambda: self.eject_device(device))

    def force_eject(self, device: USBDevice):
        """Forçar ejeção"""
        def _force():
            procs = USBEjector.find_locking_processes(device.letter)
            if procs:
                self.root.after(0, lambda: self._confirm_force(device, procs))
            else:
                self.eject_device(device)
        threading.Thread(target=_force, daemon=True).start()

    def _confirm_force(self, device: USBDevice, procs: List[ProcessInfo]):
        mb = CTkMessagebox(
            title="Confirmar", 
            message=f"Encerrar {len(procs)} processo(s)?\n\n⚠ Dados não salvos serão perdidos!",
            icon="warning", option_1="Cancelar", option_2="Forçar"
        )
        if mb.get() == "Forçar":
            self._force_eject_all(device, procs)

    def _force_eject_all(self, device: USBDevice, procs: List[ProcessInfo]):
        def _force():
            for proc in procs:
                USBEjector.kill_process(proc.pid)
                time.sleep(0.1)
            time.sleep(0.05)
            success, msg = USBEjector.eject_drive(device.letter)
            self.root.after(0, lambda: self._handle_eject_result(success, msg, device))
        threading.Thread(target=_force, daemon=True).start()

    def _handle_eject_result(self, success: bool, msg: str, device: USBDevice):
        if device.letter in self.ejecting_drives:
            self.ejecting_drives.remove(device.letter)
        
        if success:
            CTkMessagebox(title="Sucesso", message=f"✓ {device.label} ejetado\n\nPode remover o dispositivo.", icon="check")
            self.root.after(300, self.refresh_devices)
        else:
            CTkMessagebox(title="Erro", message=f"Falha:\n{msg}", icon="warning")
            self.refresh_devices()

    def show_about(self):
        """Mostrar informações sobre o desenvolvedor"""
        try:
            CTkMessagebox(
                title="About - USB Safe Ejector Pro",
                message="USB Safe Ejector Pro v7.3\n\n"
                       "Desenvolvido por: olverclock\n\n"
                       "✨ Recursos:\n"
                       "• Ejeção rápida e segura\n"
                       "• Detecção inteligente de USBs\n"
                       "• Interface moderna\n"
                       "• Modo claro/escuro\n\n"
                       "© 2025 olverclock",
                icon="info",
                option_1="OK"
            )
        except:
            logger.info("About: Desenvolvido por olverclock")

    def run(self):
        logger.info("=== USB Safe Ejector Pro v7.2 PROFESSIONAL FIX ===")
        self.root.mainloop()


def main():
    try:
        app = PremiumUSBEjectorGUI()
        app.run()
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()