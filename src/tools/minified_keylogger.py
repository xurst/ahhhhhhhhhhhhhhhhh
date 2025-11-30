import os
import sys
import subprocess

# ==========================================
# Path Setup (To find pc_logger)
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.abspath(os.path.join(current_dir, "..", "modules"))
sys.path.append(modules_dir)

try:
    import pc_logger
except ImportError:
    print(f"[!] Could not import pc_logger from {modules_dir}")
    sys.exit(1)

# ==========================================
# Main Logic
# ==========================================

def get_clipboard_content():
    """
    Uses PowerShell to get the current clipboard text.
    This avoids needing 'pip install pyperclip'.
    """
    try:
        # PowerShell command to get text from clipboard
        cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", "Get-Clipboard"]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[Error retrieving clipboard] Exit Code: {result.returncode}"
            
    except Exception as e:
        return f"[Error executing PowerShell]: {e}"

def run_fetch():
    print("Fetching Clipboard content...")
    
    # 1. Get Content
    content = get_clipboard_content()

    # Handle empty clipboard (or non-text data like images)
    if not content:
        content = "[Clipboard is empty or contains non-text data (images/files)]"

    # 2. Get Log Folder
    target_folder = pc_logger.get_pc_log_folder(create_if_missing=True)
    log_file_path = os.path.join(target_folder, "clipboard_content.txt")

    # 3. Write to file
    try:
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Clipboard saved to: {log_file_path}")
    except OSError as e:
        print(f"[!] Failed to write log file: {e}")

if __name__ == "__main__":
    run_fetch()