"""
Admin Utilities
Handles administrator privileges and elevation
"""

import sys
import ctypes

def is_admin():
    """Check if the current process has administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the application with administrator privileges"""
    try:
        if not is_admin():
            # Re-run the program with admin rights
            result = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                " ".join(sys.argv), 
                None, 
                1
            )
            if result > 32:  # Success
                sys.exit(0)
            else:
                print("⚠️ User cancelled admin elevation")
                return False
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False
    return False  # Don't exit if already admin

def check_admin_privileges():
    """Check and request admin privileges if needed"""
    if not is_admin():
        print("⚠️ Program membutuhkan hak akses Administrator untuk mengakses file Minecraft")
        print("🔄 Memulai ulang program dengan hak akses Administrator...")
        
        # Try to elevate privileges
        if run_as_admin():
            return False  # Exit if elevation is needed
        else:
            print("⚠️ Gagal mendapatkan hak akses Administrator, menjalankan dalam mode terbatas...")
            return True  # Continue in limited mode
    else:
        print("✅ Program berjalan dengan hak akses Administrator")
        return True
