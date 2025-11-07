import os
import subprocess
import re
import sys

def get_pc_log_folder(create_if_missing=True):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

    psinfo_path = os.path.join(script_dir, "PSTools", "PsInfo.exe")
    machine_ids_dir = os.path.join(project_root, "src", "machine-ids")
    sys_name = None
    base_log_dir = machine_ids_dir

    if create_if_missing:
        os.makedirs(machine_ids_dir, exist_ok=True)

    if os.path.exists(psinfo_path):
        try:
            output = subprocess.check_output([psinfo_path], text=True, stderr=subprocess.STDOUT)
            match = re.search(r'System information for \\\\([^:]+):', output)
            if match:
                sys_name = match.group(1).strip()

            if sys_name:
                base_log_dir = os.path.join(machine_ids_dir, sys_name)
                if create_if_missing:
                    os.makedirs(base_log_dir, exist_ok=True)
                    print(f"[+] Created or verified log folder: {base_log_dir}", file=sys.stderr)
            else:
                print("[!] Could not extract system name from PsInfo output.", file=sys.stderr)

        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to query PsInfo: {e}", file=sys.stderr)
    else:
        print(f"[!] PsInfo.exe not found at {psinfo_path}", file=sys.stderr)

    return base_log_dir