import os
import sys
import winreg
import datetime

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
    sys.exit(1)

# ==========================================
# Main Logic
# ==========================================

def get_registry_value(key_path, value_name):
    """Reads a value from HKLM."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            value, _ = winreg.QueryValueEx(key, value_name)
            return value
    except FileNotFoundError:
        return None
    except OSError:
        return None

def check_and_log():
    # 1. Define Constants
    REG_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    BROKEN_START = 6899
    FIXED_START = 6901
    
    # 2. Get System Info
    major_build = get_registry_value(REG_PATH, "CurrentBuild")
    ubr = get_registry_value(REG_PATH, "UBR")

    # 3. Prepare Log Content
    log_lines = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_lines.append("======================================================================")
    log_lines.append(" WinRE Bug Check - Result Log")
    log_lines.append("======================================================================")
    log_lines.append(f"\nLog generated on: {timestamp}\n")

    # Validation
    if not major_build or ubr is None:
        log_lines.append("Error: Could not read 'CurrentBuild' or 'UBR' from the registry.")
        log_lines.append("Make sure the script is run with sufficient privileges (Administrator).")
    else:
        # Convert UBR to int just in case
        try:
            ubr_int = int(ubr)
        except ValueError:
            ubr_int = 0
            
        log_lines.append(" -- System Information Detected --\n")
        log_lines.append(f"   Major Build         : {major_build}")
        log_lines.append(f"   UBR (Decimal)       : {ubr_int}")
        log_lines.append(f"   Full Version String : {major_build}.{ubr_int}\n")
        
        # 4. Logic Check
        is_target_build = str(major_build) in ["26100", "26200"]
        
        if is_target_build:
            if str(major_build) == "26100":
                log_lines.append("Branch: Windows 11 24H2")
            else:
                log_lines.append("Branch: Windows 11 25H2")

            if ubr_int < BROKEN_START:
                log_lines.append("Status: NOT AFFECTED")
                log_lines.append("This build is earlier than the KB5066835 WinRE bug.")
            elif BROKEN_START <= ubr_int < FIXED_START:
                log_lines.append("Status: BROKEN")
                log_lines.append("Your build is inside the KB5066835 WinRE mouse/keyboard input bug window.")
            else:
                log_lines.append("Status: FIXED")
                log_lines.append("Your build contains KB5070773 or later. WinRE USB input is repaired.")
        else:
            # Replicating the verbose output for unknown builds from your batch file
            log_lines.append("Status: UNKNOWN")
            log_lines.append("This script is intended for Windows 11 24H2 (26100.x) and 25H2 (26200.x).")
            log_lines.append("\n -- Script Analysis --")
            log_lines.append(f"This build was marked as 'UNKNOWN' because the Major Build ({major_build})")
            log_lines.append("is not one of the specific builds this script targets (26100 or 26200).")
            log_lines.append("\n -- Information for Your Research --")
            log_lines.append("The WinRE USB input bug this script checks for was introduced in a Cumulative")
            log_lines.append("Update (KB5066835) for builds 26100 and 26200, and was fixed by a later")
            log_lines.append("update (KB5070773).")
            log_lines.append(f"\nThe script's thresholds for those builds are:")
            log_lines.append(f"  - Broken UBR Range: {BROKEN_START} - 6900")
            log_lines.append(f"  - Fixed UBR Start : {FIXED_START}")
            log_lines.append(f"\nThese UBR numbers are specific to builds 26100/26200 and likely DO NOT APPLY")
            log_lines.append(f"to your build ({major_build}).")

    # 5. Get Log Folder (using pc_logger)
    target_folder = pc_logger.get_pc_log_folder(create_if_missing=True)
    log_file_path = os.path.join(target_folder, "winre_result.log")

    # 6. Write to File
    try:
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines))
        print(f"[+] WinRE check complete. Log saved to: {log_file_path}")
    except OSError as e:
        print(f"[!] Failed to write log file: {e}")

if __name__ == "__main__":
    check_and_log()