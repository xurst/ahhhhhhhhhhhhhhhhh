import os
import sys
import ctypes
import subprocess
from ctypes import wintypes

# ==========================================
# Path Setup (To find pc_logger)
# ==========================================
# Get directory of this script: .../src/tools/
current_dir = os.path.dirname(os.path.abspath(__file__))

# Calculate path to modules: .../src/modules/
modules_dir = os.path.abspath(os.path.join(current_dir, "..", "modules"))

# Add to Python path so we can import pc_logger
sys.path.append(modules_dir)

try:
    import pc_logger
except ImportError:
    print(f"[!] Could not import pc_logger from {modules_dir}")
    print("    Make sure the file exists and the path is correct.")
    sys.exit(1)

# ==========================================
# Helper Functions
# ==========================================

def run_powershell(cmd):
    """Executes a PowerShell command and returns the stripped output."""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, timeout=10
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def get_bitlocker_status(drive_letter):
    """
    Returns the BitLocker protection status integer.
    1, 3, 5 = Protected
    2 = Unprotected / Off
    """
    # PowerShell script to check protection status using COM object
    script = f"(New-Object -Com Shell.Application).NameSpace('{drive_letter}').Self.ExtendedProperty('System.Volume.BitLockerProtection')"
    val = run_powershell(script)
    
    if val and val.isdigit():
        return int(val)
    return None

def get_logical_drives():
    """Returns a list of drive letters (e.g., ['C:\\', 'D:\\'])"""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        if bitmask & (1 << i):
            drive = f"{chr(65+i)}:\\"
            # Get drive type: 2=Removable, 3=Fixed, 4=Remote, 5=CDROM
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(wintypes.LPCWSTR(drive))
            if drive_type in (2, 3, 4, 5): 
                drives.append(drive)
    return drives

# ==========================================
# Main Logic
# ==========================================

def scan_and_log():
    print("Running BitLocker scan...")
    
    # 1. Prepare the log content
    log_lines = []
    log_lines.append("=== BitLocker Checker Log ===")
    log_lines.append("Scanning system drives...\n")

    encrypted_count = 0
    unprotected_count = 0

    # 2. Iterate through drives
    for drive in get_logical_drives():
        status = get_bitlocker_status(drive)
        clean_drive_name = drive[:-1] 

        if status in (1, 3, 5):
            log_lines.append(f"{clean_drive_name} : PROTECTED")
            encrypted_count += 1
        elif status == 2:
            log_lines.append(f"{clean_drive_name} : UNPROTECTED")
            unprotected_count += 1
        else:
            log_lines.append(f"{clean_drive_name} : NO DATA / UNKNOWN")

    # 3. Add Summary
    log_lines.append("\n=== Summary ===")
    log_lines.append(f"Protected Drives   : {encrypted_count}")
    log_lines.append(f"Unprotected Drives : {unprotected_count}")

    # 4. Get the Log Folder using pc_logger
    # Since pc_logger is in modules, it calculates paths relative to itself
    # It will find/create: src/machine-ids/<PC_NAME>/
    target_folder = pc_logger.get_pc_log_folder(create_if_missing=True)
    
    # 5. Write the file
    log_file_path = os.path.join(target_folder, "bitlocker_status.log")
    
    try:
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
        print(f"[+] BitLocker status saved to: {log_file_path}")
    except OSError as e:
        print(f"[!] Failed to write log file: {e}")

if __name__ == "__main__":
    scan_and_log()