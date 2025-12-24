import os
import platform

def get_minecraft_worlds_path():
    """Get universal Minecraft Bedrock worlds path untuk berbagai OS dan username"""
    system = platform.system()
    username = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
    
    potential_paths = []
    
    if system == "Windows":
        # 1. Custom/Roaming path (Requested Priority)
        # Path: %APPDATA%\Minecraft Bedrock\Users\<User-ID>\games\com.mojang\minecraftWorlds
        # Ini menangani kasus user ID yang berubah-ubah (11409861786820239989 dll) secara dinamis
        appdata = os.getenv('APPDATA')
        if appdata:
            base_roaming_users = os.path.join(appdata, "Minecraft Bedrock", "Users")
            if os.path.exists(base_roaming_users):
                try:
                    # Scan semua folder user ID yang ada
                    user_ids = [d for d in os.listdir(base_roaming_users) 
                                if os.path.isdir(os.path.join(base_roaming_users, d))]
                    
                    for uid in user_ids:
                        target = os.path.join(base_roaming_users, uid, "games", "com.mojang", "minecraftWorlds")
                        potential_paths.append(target)
                except Exception as e:
                    print(f"Error scanning roaming path: {e}")

        # 2. Standard UWP Path
        # Path: %LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds
        localappdata = os.getenv('LOCALAPPDATA')
        if localappdata:
            uwp_path = os.path.join(localappdata, "Packages", "Microsoft.MinecraftUWP_8wekyb3d8bbwe", "LocalState", "games", "com.mojang", "minecraftWorlds")
            potential_paths.append(uwp_path)

        # 3. Fallback UWP variants
        potential_paths.append(os.path.expanduser("~\\AppData\\Local\\Packages\\Microsoft.MinecraftUWP_8wekyb3d8bbwe\\LocalState\\games\\com.mojang\\minecraftWorlds"))
        
    elif system == "Darwin":  # macOS
        potential_paths.append(os.path.expanduser("~/Library/Application Support/mcpelauncher/games/com.mojang/minecraftWorlds"))
        
    elif system == "Linux":
        potential_paths.append(os.path.expanduser("~/.local/share/mcpelauncher/games/com.mojang/minecraftWorlds"))
        potential_paths.append(os.path.expanduser("~/.minecraft/minecraftWorlds"))
    
    # Generic Fallback
    potential_paths.append(os.path.expanduser("~/minecraftWorlds"))
    
    # Cari path yang benar-benar ada
    for path in potential_paths:
        if os.path.exists(path):
            print(f"Found Minecraft worlds at: {path}")
            return path
    
    # Jika tidak ada yang ditemukan, return path default/pertama
    default_path = potential_paths[0] if potential_paths else os.path.expanduser("~/minecraftWorlds")
    print(f"Minecraft worlds path not found, using default: {default_path}")
    return default_path

# Get universal path
MINECRAFT_WORLDS_PATH = get_minecraft_worlds_path()
