import os
import platform

def get_minecraft_worlds_path():
    """Get universal Minecraft Bedrock worlds path untuk berbagai OS dan username"""
    system = platform.system()
    username = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
    
    if system == "Windows":
        # Windows paths - coba berbagai kemungkinan
        possible_paths = [
            # Windows Store version (UWP)
            os.path.expanduser(f"~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"),
            # Windows Store version dengan username spesifik
            f"C:\\Users\\{username}\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds",
            # Legacy Windows Store version
            os.path.expanduser(f"~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"),
            # Windows Store version dengan package ID lama
            os.path.expanduser(f"~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"),
            # Microsoft Store version
            os.path.expanduser(f"~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"),
            # Alternative Windows Store path
            os.path.expanduser(f"~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"),
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            # macOS paths
            os.path.expanduser("~/Library/Application Support/mcpelauncher/games/com.mojang/minecraftWorlds"),
            os.path.expanduser("~/Library/Application Support/mcpelauncher/games/com.mojang/minecraftWorlds"),
        ]
    elif system == "Linux":
        possible_paths = [
            # Linux paths
            os.path.expanduser("~/.local/share/mcpelauncher/games/com.mojang/minecraftWorlds"),
            os.path.expanduser("~/.minecraft/minecraftWorlds"),
        ]
    else:
        # Fallback untuk sistem yang tidak dikenal
        possible_paths = [
            os.path.expanduser("~/minecraftWorlds"),
        ]
    
    # Cari path yang benar-benar ada
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found Minecraft worlds at: {path}")
            return path
    
    # Jika tidak ada yang ditemukan, return path default Windows
    default_path = os.path.expanduser(f"~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds")
    print(f"Minecraft worlds path not found, using default: {default_path}")
    return default_path

# Get universal path
MINECRAFT_WORLDS_PATH = get_minecraft_worlds_path()
