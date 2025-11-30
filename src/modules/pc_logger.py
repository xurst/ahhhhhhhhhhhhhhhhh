import os
import subprocess
import re
import sys

def get_pc_log_folder(create_if_missing=True):
    """
    Runs PsInfo (accepting EULA automatically) to identify the machine, 
    creates a specific folder for it, and saves the raw PsInfo output 
    into 'ps_info.log' within that folder.
    """
    # 1. Setup Paths relative to this script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    
    machine_ids_dir = os.path.join(project_root, "src", "machine-ids")
    psinfo_path = os.path.join(script_dir, "PSTools", "PsInfo.exe")
    
    sys_name = None
    psinfo_output = ""
    final_log_dir = machine_ids_dir

    # 2. Run PsInfo
    if os.path.exists(psinfo_path):
        try:
            # ADDED: "/accepteula" flag to prevent exit code 1 on fresh machines
            command = [psinfo_path, "/accepteula"]
            
            # Capture the full standard output
            psinfo_output = subprocess.check_output(
                command, 
                text=True, 
                stderr=subprocess.STDOUT
            )
            
            # Extract System Name via Regex
            match = re.search(r'System information for \\\\([^:]+):', psinfo_output)
            if match:
                sys_name = match.group(1).strip()
            
        except subprocess.CalledProcessError as e:
            # If it fails, capture the output to see WHY (e.g., access denied)
            psinfo_output = e.output 
            if __name__ == "__main__":
                print(f"[!] Failed to query PsInfo. Exit Code: {e.returncode}", file=sys.stderr)
                print(f"[!] Tool Output:\n{e.output}", file=sys.stderr)
    else:
        if __name__ == "__main__":
            print(f"[!] PsInfo.exe not found at {psinfo_path}", file=sys.stderr)

    # 3. Determine Final Directory Path
    if sys_name:
        final_log_dir = os.path.join(machine_ids_dir, sys_name)

    # 4. Create Directory and Write Log File
    if create_if_missing:
        try:
            os.makedirs(final_log_dir, exist_ok=True)

            # Save the PsInfo output (even if it failed/incomplete, we log what we got)
            if psinfo_output:
                log_file_path = os.path.join(final_log_dir, "ps_info.log")
                with open(log_file_path, "w", encoding="utf-8") as f:
                    f.write(psinfo_output)
                
                if __name__ == "__main__":
                    print(f"[+] PsInfo output saved to: {log_file_path}")

        except OSError as e:
            if __name__ == "__main__":
                print(f"[!] Error interacting with filesystem: {e}", file=sys.stderr)

    return final_log_dir

# ==========================================
# Main Execution Block
# ==========================================
if __name__ == "__main__":
    print("Running machine identification...")
    folder = get_pc_log_folder(create_if_missing=True)
    print(f"[+] Target Directory: {folder}")
