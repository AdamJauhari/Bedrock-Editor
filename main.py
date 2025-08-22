import sys
import os
import subprocess
def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Install required packages
for pkg in ["PyQt5", "nbtlib"]:
    ensure_package(pkg)

# Try to import amulet-nbt, but make it optional
try:
    from amulet_nbt import load as amulet_load
    AMULET_AVAILABLE = True
except ImportError:
    print("Warning: amulet-nbt not available, using nbtlib only")
    AMULET_AVAILABLE = False

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, QAction, QMessageBox, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QHBoxLayout, QSizePolicy, QLineEdit
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
import nbtlib
import struct

# Path ke folder worlds Minecraft Bedrock - Universal untuk semua komputer
def get_minecraft_worlds_path():
    """Get universal Minecraft Bedrock worlds path untuk berbagai OS dan username"""
    import os
    import platform
    
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

class NBTEditor(QMainWindow):
    def nbt_to_dict(self, nbt, depth=0):
        # Konversi tag amulet-nbt ke dict Python untuk Bedrock level.dat
        try:
            # Handle NamedTag Bedrock (level.dat root structure)
            if hasattr(nbt, 'compound'):
                return self.nbt_to_dict(nbt.compound, depth+1)
            # Handle amulet CompoundTag atau dictionary-like structures
            elif hasattr(nbt, 'items') and callable(getattr(nbt, 'items')):
                result = {}
                for k, v in nbt.items():
                    try:
                        key_str = str(k)
                        result[key_str] = self.nbt_to_dict(v, depth+1)
                    except Exception:
                        result[str(k)] = str(v)
                return result
            # Handle Python dict
            elif isinstance(nbt, dict):
                result = {}
                for k, v in nbt.items():
                    try:
                        result[str(k)] = self.nbt_to_dict(v, depth+1)
                    except Exception:
                        result[str(k)] = str(v)
                return result
            # Handle List tags atau Python list
            elif isinstance(nbt, list) or (hasattr(nbt, '__iter__') and hasattr(nbt, '__len__')):
                result = []
                for v in nbt:
                    try:
                        result.append(self.nbt_to_dict(v, depth+1))
                    except Exception:
                        result.append(str(v))
                return result
            # Handle NBT tags with value attribute
            elif hasattr(nbt, 'value'):
                return self.nbt_to_dict(nbt.value, depth+1)
            # Handle NBT arrays with py_data
            elif hasattr(nbt, 'py_data'):
                return nbt.py_data
            # Handle primitive values
            else:
                return nbt
        except Exception:
            return str(nbt)
        except Exception:
            # Fallback to string representation if conversion fails
            return str(nbt)
    
    def parse_bedrock_level_dat_manual(self, file_path):
        """
        Hybrid parser untuk Bedrock level.dat dengan pattern matching dan NBT parsing
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            print(f"Using hybrid parsing approach for {len(data)} bytes")
            
            result = {}
            
            # Define all known level.dat fields dengan expected types
            level_dat_fields = {
                # String fields
                'BiomeOverride': ('string', r'BiomeOverride'),
                'FlatWorldLayers': ('string', r'FlatWorldLayers'), 
                'InventoryVersion': ('string', r'InventoryVersion'),
                'LevelName': ('string', r'LevelName'),
                'baseGameVersion': ('string', r'baseGameVersion'),
                'prid': ('string', r'prid'),
                
                # Byte fields (0 atau 1)
                'CenterMapsToOrigin': ('byte', r'CenterMapsToOrigin'),
                'ConfirmedPlatformLockedContent': ('byte', r'ConfirmedPlatformLockedContent'),
                'ForceGameType': ('byte', r'ForceGameType'),
                'IsHardcore': ('byte', r'IsHardcore'),
                'LANBroadcast': ('byte', r'LANBroadcast'),
                'LANBroadcastIntent': ('byte', r'LANBroadcastIntent'),
                'MultiplayerGame': ('byte', r'MultiplayerGame'),
                'MultiplayerGameIntent': ('byte', r'MultiplayerGameIntent'),
                'PlayerHasDied': ('byte', r'PlayerHasDied'),
                'SpawnV1Villagers': ('byte', r'SpawnV1Villagers'),
                'bonusChestEnabled': ('byte', r'bonusChestEnabled'),
                'bonusChestSpawned': ('byte', r'bonusChestSpawned'),
                'cheatsEnabled': ('byte', r'cheatsEnabled'),
                'commandblockoutput': ('byte', r'commandblockoutput'),
                'commandblocksenabled': ('byte', r'commandblocksenabled'),
                'commandsEnabled': ('byte', r'commandsEnabled'),
                'dodaylightcycle': ('byte', r'dodaylightcycle'),
                'doentitydrops': ('byte', r'doentitydrops'),
                'dofiretick': ('byte', r'dofiretick'),
                'doimmediaterespawn': ('byte', r'doimmediaterespawn'),
                'doinsomnia': ('byte', r'doinsomnia'),
                'dolimitedcrafting': ('byte', r'dolimitedcrafting'),
                'domobloot': ('byte', r'domobloot'),
                'domobspawning': ('byte', r'domobspawning'),
                'dotiledrops': ('byte', r'dotiledrops'),
                'doweathercycle': ('byte', r'doweathercycle'),
                'drowningdamage': ('byte', r'drowningdamage'),
                'educationFeaturesEnabled': ('byte', r'educationFeaturesEnabled'),
                'falldamage': ('byte', r'falldamage'),
                'firedamage': ('byte', r'firedamage'),
                'freezedamage': ('byte', r'freezedamage'),
                'hasBeenLoadedInCreative': ('byte', r'hasBeenLoadedInCreative'),
                'hasLockedBehaviorPack': ('byte', r'hasLockedBehaviorPack'),
                'hasLockedResourcePack': ('byte', r'hasLockedResourcePack'),
                'immutableWorld': ('byte', r'immutableWorld'),
                'isCreatedInEditor': ('byte', r'isCreatedInEditor'),
                'isExportedFromEditor': ('byte', r'isExportedFromEditor'),
                'isFromLockedTemplate': ('byte', r'isFromLockedTemplate'),
                'isFromWorldTemplate': ('byte', r'isFromWorldTemplate'),
                'isRandomSeedAllowed': ('byte', r'isRandomSeedAllowed'),
                'isSingleUseWorld': ('byte', r'isSingleUseWorld'),
                'isWorldTemplateOptionLocked': ('byte', r'isWorldTemplateOptionLocked'),
                'keepinventory': ('byte', r'keepinventory'),
                'mobgriefing': ('byte', r'mobgriefing'),
                'naturalregeneration': ('byte', r'naturalregeneration'),
                'projectilescanbreakblocks': ('byte', r'projectilescanbreakblocks'),
                'pvp': ('byte', r'pvp'),
                'recipesunlock': ('byte', r'recipesunlock'),
                'requiresCopiedPackRemovalCheck': ('byte', r'requiresCopiedPackRemovalCheck'),
                'respawnblocksexplode': ('byte', r'respawnblocksexplode'),
                'sendcommandfeedback': ('byte', r'sendcommandfeedback'),
                'showbordereffect': ('byte', r'showbordereffect'),
                'showcoordinates': ('byte', r'showcoordinates'),
                'showdaysplayed': ('byte', r'showdaysplayed'),
                'showdeathmessages': ('byte', r'showdeathmessages'),
                'showrecipemessages': ('byte', r'showrecipemessages'),
                'showtags': ('byte', r'showtags'),
                'spawnMobs': ('byte', r'spawnMobs'),
                'startWithMapEnabled': ('byte', r'startWithMapEnabled'),
                'texturePacksRequired': ('byte', r'texturePacksRequired'),
                'tntexplodes': ('byte', r'tntexplodes'),
                'tntexplosiondropdecay': ('byte', r'tntexplosiondropdecay'),
                'useMsaGamertagsOnly': ('byte', r'useMsaGamertagsOnly'),
                
                # Integer fields
                'Difficulty': ('int', r'Difficulty'),
                'GameType': ('int', r'GameType'),
                'Generator': ('int', r'Generator'),
                'LimitedWorldOriginX': ('int', r'LimitedWorldOriginX'),
                'LimitedWorldOriginY': ('int', r'LimitedWorldOriginY'),
                'LimitedWorldOriginZ': ('int', r'LimitedWorldOriginZ'),
                'NetherScale': ('int', r'NetherScale'),
                'NetworkVersion': ('int', r'NetworkVersion'),
                'Platform': ('int', r'Platform'),
                'PlatformBroadcastIntent': ('int', r'PlatformBroadcastIntent'),
                'SpawnX': ('int', r'SpawnX'),
                'SpawnY': ('int', r'SpawnY'),
                'SpawnZ': ('int', r'SpawnZ'),
                'StorageVersion': ('int', r'StorageVersion'),
                'WorldVersion': ('int', r'WorldVersion'),
                'XBLBroadcastIntent': ('int', r'XBLBroadcastIntent'),
                'daylightCycle': ('int', r'daylightCycle'),
                'editorWorldType': ('int', r'editorWorldType'),
                'eduOffer': ('int', r'eduOffer'),
                'functioncommandlimit': ('int', r'functioncommandlimit'),
                'lightningTime': ('int', r'lightningTime'),
                'limitedWorldDepth': ('int', r'limitedWorldDepth'),
                'limitedWorldWidth': ('int', r'limitedWorldWidth'),
                'maxcommandchainlength': ('int', r'maxcommandchainlength'),
                'permissionsLevel': ('int', r'permissionsLevel'),
                'playerPermissionsLevel': ('int', r'playerPermissionsLevel'),
                'playerssleepingpercentage': ('int', r'playerssleepingpercentage'),
                'rainTime': ('int', r'rainTime'),
                'randomtickspeed': ('int', r'randomtickspeed'),
                'serverChunkTickRange': ('int', r'serverChunkTickRange'),
                'spawnradius': ('int', r'spawnradius'),
                
                # Long fields  
                'LastPlayed': ('long', r'LastPlayed'),
                'RandomSeed': ('long', r'RandomSeed'),
                'Time': ('long', r'Time'),
                'currentTick': ('long', r'currentTick'),
                'worldStartCount': ('long', r'worldStartCount'),
                
                # Float fields
                'lightningLevel': ('float', r'lightningLevel'),
                'rainLevel': ('float', r'rainLevel'),
            }
            
            # Parse each field
            for field_name, (field_type, pattern) in level_dat_fields.items():
                field_bytes = pattern.encode('utf-8')
                pos = data.find(field_bytes)
                
                if pos > 0:
                    try:
                        value_pos = pos + len(field_bytes)
                        value = self._extract_value_by_type(data, value_pos, field_type)
                        if value is not None:
                            result[field_name] = value
                    except Exception:
                        continue
            
            # Try to parse compound fields (nested structures)
            compound_fields = ['abilities', 'experiments', 'world_policies', 
                             'MinimumCompatibleClientVersion', 'lastOpenedWithVersion']
            
            for compound_name in compound_fields:
                compound_bytes = compound_name.encode('utf-8')
                pos = data.find(compound_bytes)
                if pos > 0:
                    try:
                        # Try to parse as compound after the name
                        value_pos = pos + len(compound_bytes)
                        compound_data = self._try_parse_compound_at(data, value_pos)
                        if compound_data:
                            result[compound_name] = compound_data
                    except Exception:
                        continue
            
            print(f"Hybrid parser extracted {len(result)} fields from level.dat")
            return result
            
        except Exception as e:
            print(f"Hybrid parser failed: {e}")
            return {}
    
    def _parse_nbt_tag(self, data, pos=0):
        """Parse NBT tag secara rekursif"""
        try:
            if pos >= len(data):
                return None, pos
            
            # Read tag type
            tag_type = data[pos]
            pos += 1
            
            if tag_type == 0:  # TAG_End
                return None, pos
            
            # Read tag name (for named tags)
            name = ""
            if pos + 2 <= len(data):
                name_length = struct.unpack('<H', data[pos:pos+2])[0]
                pos += 2
                if pos + name_length <= len(data):
                    name = data[pos:pos+name_length].decode('utf-8', errors='replace')
                    pos += name_length
            
            # Parse tag value based on type
            value, pos = self._parse_nbt_value(data, pos, tag_type)
            
            return {name: value} if name else value, pos
            
        except Exception as e:
            return None, pos
    
    def _parse_nbt_value(self, data, pos, tag_type):
        """Parse NBT value berdasarkan tipe tag"""
        try:
            if tag_type == 1:  # TAG_Byte
                if pos < len(data):
                    return data[pos], pos + 1
                    
            elif tag_type == 2:  # TAG_Short
                if pos + 2 <= len(data):
                    return struct.unpack('<h', data[pos:pos+2])[0], pos + 2
                    
            elif tag_type == 3:  # TAG_Int
                if pos + 4 <= len(data):
                    return struct.unpack('<i', data[pos:pos+4])[0], pos + 4
                    
            elif tag_type == 4:  # TAG_Long
                if pos + 8 <= len(data):
                    return struct.unpack('<q', data[pos:pos+8])[0], pos + 8
                    
            elif tag_type == 5:  # TAG_Float
                if pos + 4 <= len(data):
                    return struct.unpack('<f', data[pos:pos+4])[0], pos + 4
                    
            elif tag_type == 6:  # TAG_Double
                if pos + 8 <= len(data):
                    return struct.unpack('<d', data[pos:pos+8])[0], pos + 8
                    
            elif tag_type == 7:  # TAG_Byte_Array
                if pos + 4 <= len(data):
                    length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    if pos + length <= len(data):
                        return list(data[pos:pos+length]), pos + length
                        
            elif tag_type == 8:  # TAG_String
                if pos + 2 <= len(data):
                    length = struct.unpack('<H', data[pos:pos+2])[0]
                    pos += 2
                    if pos + length <= len(data):
                        return data[pos:pos+length].decode('utf-8', errors='replace'), pos + length
                        
            elif tag_type == 9:  # TAG_List
                if pos + 5 <= len(data):
                    list_type = data[pos]
                    pos += 1
                    length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    
                    result_list = []
                    for i in range(length):
                        if pos >= len(data):
                            break
                        value, pos = self._parse_nbt_value(data, pos, list_type)
                        result_list.append(value)
                    return result_list, pos
                    
            elif tag_type == 10:  # TAG_Compound
                result_dict = {}
                while pos < len(data):
                    # Read next tag
                    if pos >= len(data):
                        break
                        
                    next_tag_type = data[pos]
                    if next_tag_type == 0:  # TAG_End
                        pos += 1
                        break
                    
                    # Parse named tag
                    pos += 1  # Skip tag type
                    
                    # Read name
                    if pos + 2 <= len(data):
                        name_length = struct.unpack('<H', data[pos:pos+2])[0]
                        pos += 2
                        if pos + name_length <= len(data):
                            name = data[pos:pos+name_length].decode('utf-8', errors='replace')
                            pos += name_length
                            
                            # Parse value
                            value, pos = self._parse_nbt_value(data, pos, next_tag_type)
                            result_dict[name] = value
                        else:
                            break
                    else:
                        break
                        
                return result_dict, pos
                
            elif tag_type == 11:  # TAG_Int_Array
                if pos + 4 <= len(data):
                    length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    if pos + length * 4 <= len(data):
                        result = []
                        for i in range(length):
                            result.append(struct.unpack('<i', data[pos:pos+4])[0])
                            pos += 4
                        return result, pos
                        
            elif tag_type == 12:  # TAG_Long_Array
                if pos + 4 <= len(data):
                    length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    if pos + length * 8 <= len(data):
                        result = []
                        for i in range(length):
                            result.append(struct.unpack('<q', data[pos:pos+8])[0])
                            pos += 8
                        return result, pos
            
            return None, pos
            
        except Exception as e:
            return None, pos
    
    def _extract_value_by_type(self, data, pos, field_type):
        """Extract value dengan tipe yang diharapkan dari posisi data"""
        try:
            if field_type == 'string':
                # Cari string length (berbagai kemungkinan format)
                for offset in [0, 1, 2, 3, 4]:
                    try:
                        if pos + offset + 2 <= len(data):
                            str_len = struct.unpack('<H', data[pos+offset:pos+offset+2])[0]
                            if 1 <= str_len <= 10000:  # Reasonable string length
                                str_start = pos + offset + 2
                                if str_start + str_len <= len(data):
                                    value = data[str_start:str_start+str_len].decode('utf-8', errors='replace')
                                    if len(value.strip()) > 0:  # Non-empty string
                                        return value
                    except:
                        continue
                        
            elif field_type == 'byte':
                # Try different offsets for byte values
                for offset in [0, 1, 2, 3, 4]:
                    if pos + offset < len(data):
                        value = data[pos + offset]
                        if value in [0, 1]:  # Boolean byte values
                            return value
                        
            elif field_type == 'int':
                # Try different offsets for 4-byte integers
                for offset in [0, 1, 2, 3, 4]:
                    if pos + offset + 4 <= len(data):
                        try:
                            value = struct.unpack('<i', data[pos+offset:pos+offset+4])[0]
                            if -2147483648 <= value <= 2147483647:  # Valid int range
                                return value
                        except:
                            continue
                            
            elif field_type == 'long':
                # Try different offsets for 8-byte long values
                for offset in [0, 1, 2, 3, 4, 8, 12]:
                    if pos + offset + 8 <= len(data):
                        try:
                            value = struct.unpack('<q', data[pos+offset:pos+offset+8])[0]
                            return value
                        except:
                            continue
                            
            elif field_type == 'float':
                # Try different offsets for 4-byte float values
                for offset in [0, 1, 2, 3, 4]:
                    if pos + offset + 4 <= len(data):
                        try:
                            value = struct.unpack('<f', data[pos+offset:pos+offset+4])[0]
                            if not (value != value):  # Not NaN
                                return value
                        except:
                            continue
            
            return None
            
        except Exception:
            return None
    
    def _try_parse_compound_at(self, data, pos):
        """Coba parse compound/array data di posisi tertentu"""
        try:
            # Coba parse sebagai list integer (untuk version arrays)
            if pos + 4 <= len(data):
                try:
                    list_len = struct.unpack('<i', data[pos:pos+4])[0]
                    if 1 <= list_len <= 10:  # Reasonable list length for version arrays
                        pos += 4
                        result = []
                        for i in range(list_len):
                            if pos + 4 <= len(data):
                                value = struct.unpack('<i', data[pos:pos+4])[0]
                                result.append(value)
                                pos += 4
                            else:
                                break
                        if len(result) == list_len:
                            return result
                except:
                    pass
            
            # Coba parse sebagai simple compound dengan beberapa fields
            result_dict = {}
            
            # Look for common ability fields
            abilities_fields = ['attackmobs', 'attackplayers', 'build', 'doorsandswitches', 
                              'flying', 'instabuild', 'invulnerable', 'lightning', 'mayfly', 
                              'mine', 'op', 'opencontainers', 'teleport']
            
            for field in abilities_fields:
                field_bytes = field.encode('utf-8')
                field_pos = data.find(field_bytes, pos, pos + 200)  # Look in nearby range
                if field_pos > 0:
                    value_pos = field_pos + len(field_bytes)
                    # Try to get byte value
                    for offset in [0, 1, 2, 3]:
                        if value_pos + offset < len(data):
                            value = data[value_pos + offset]
                            if value in [0, 1]:
                                result_dict[field] = value
                                break
            
            # Look for float fields in abilities
            float_fields = ['flySpeed', 'walkSpeed', 'verticalFlySpeed']
            for field in float_fields:
                field_bytes = field.encode('utf-8')
                field_pos = data.find(field_bytes, pos, pos + 200)
                if field_pos > 0:
                    value_pos = field_pos + len(field_bytes)
                    for offset in [0, 1, 2, 3, 4]:
                        if value_pos + offset + 4 <= len(data):
                            try:
                                value = struct.unpack('<f', data[value_pos+offset:value_pos+offset+4])[0]
                                if not (value != value):  # Not NaN
                                    result_dict[field] = value
                                    break
                            except:
                                continue
            
            return result_dict if len(result_dict) > 0 else None
            
        except Exception:
            return None
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bedrock NBT/DAT Editor")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.png"))
        self.nbt_file = None
        self.nbt_data = None
        self.search_results = []  # Store search result items
        
        # Timer for search debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_live_search)
        
        # Flag to prevent itemChanged signal during search/programmatic changes
        self.is_programmatic_change = False
        
        self.init_ui()

    def init_ui(self):
        # Menu dan Toolbar
        menubar = self.menuBar()
        
        # File Menu
        open_action = QAction(QIcon(), "Buka File", self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction(QIcon(), "Simpan", self)
        save_action.triggered.connect(self.save_file)
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        
        # Toolbar dengan Save Button
        toolbar = self.addToolBar("Main")
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #23272e;
                border: none;
                spacing: 10px;
                padding: 8px;
            }
            QToolBar QToolButton {
                background-color: #00d084;
                color: white;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 2px;
            }
            QToolBar QToolButton:hover {
                background-color: #00b36b;
            }
            QToolBar QToolButton:pressed {
                background-color: #009658;
            }
        """)
        
        # Save button di toolbar
        save_toolbar_action = QAction("💾 Simpan Perubahan", self)
        save_toolbar_action.triggered.connect(self.save_file)
        toolbar.addAction(save_toolbar_action)
        
        # Author attribution dengan format dua baris
        author_label = QLabel("Bedrock NBT/DAT Editor\nBy Adam Arias Jauhari")
        author_label.setStyleSheet("""
            color: #00bfff;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 8px 15px;
            margin: 0px 15px;
            background-color: rgba(0, 191, 255, 0.1);
            border: 1px solid rgba(0, 191, 255, 0.3);
            border-radius: 6px;
            line-height: 1.3;
        """)
        author_label.setAlignment(Qt.AlignCenter)
        toolbar.addWidget(author_label)

        # Main widget & layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # Sidebar: World List
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        label_world = QLabel("Daftar Dunia Minecraft Bedrock")
        label_world.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        sidebar.addWidget(label_world)
        self.world_list = QListWidget()
        self.world_list.setMaximumWidth(280)
        self.world_list.setStyleSheet("""
            QListWidget {
                background-color: #23272e;
                color: #e1e1e1;
                font-size: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0px;
                border-radius: 6px;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: #2d3139;
                border: 1px solid #0078d4;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        self.world_list.itemClicked.connect(self.on_world_selected)
        self.load_worlds()
        sidebar.addWidget(self.world_list)
        main_layout.addLayout(sidebar)

        # Center: NBT Tree
        center_layout = QVBoxLayout()
        label_nbt = QLabel("Isi File NBT/DAT")
        label_nbt.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        center_layout.addWidget(label_nbt)
        
        # Search Box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        # Live search input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter key - hanya tampilkan yang mengandung teks (contoh: 'crea', 'level', 'time')")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d3139;
                color: #e1e1e1;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid #404040;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #00bfff;
                background-color: #23272e;
            }
            QLineEdit::placeholder {
                color: #888888;
                font-style: italic;
            }
        """)
        # Connect live search
        self.search_input.textChanged.connect(self.on_search_text_changed)
        
        # Search status label
        self.search_status = QLabel("Siap untuk mencari...")
        self.search_status.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 4px 8px;
        """)
        
        # Show all items button
        self.clear_search_btn = QPushButton("👁 Tampilkan Semua")
        self.clear_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #e1e1e1;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        self.clear_search_btn.clicked.connect(self.clear_search)
        
        search_layout.addWidget(self.search_input, 1)  # Stretch factor 1 untuk mengambil lebih banyak space
        search_layout.addWidget(self.search_status)
        search_layout.addWidget(self.clear_search_btn)
        
        center_layout.addLayout(search_layout)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        
        # Set column widths untuk tabel yang lebih besar
        self.tree.setColumnWidth(0, 300)  # Key column - diperbesar
        self.tree.setColumnWidth(1, 500)  # Value column - diperbesar
        
        # Enhanced tree styling with better contrast
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #23272e;
                color: #e1e1e1;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px;
                selection-background-color: #0078d4;
                outline: none;
                gridline-color: #404040;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                margin: 1px 0px;
                border-radius: 4px;
                color: #e1e1e1;
                background-color: transparent;
            }
            QTreeWidget::item:hover {
                background-color: #2d3139;
                color: #ffffff;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTreeWidget::item:alternate {
                background-color: #1e2328;
            }
            QTreeWidget QLineEdit {
                background-color: #2d3139 !important;
                color: #ffffff !important;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 3px solid #ff6b35 !important;
                border-radius: 6px;
                padding: 6px 12px;
                selection-background-color: #4da6ff !important;
                selection-color: #ffffff !important;
                min-height: 20px;
            }
            QTreeWidget QLineEdit:focus {
                border: 4px solid #ff9500 !important;
                background-color: #2d3139 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #1e2328;
                color: #00bfff;
                font-weight: bold;
                font-size: 15px;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #404040;
                border-bottom: 2px solid #00bfff;
            }
            QHeaderView::section:hover {
                background-color: #2d3139;
            }
        """)
        
        # Set alternating row colors
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(20)
        
        center_layout.addWidget(self.tree)
        main_layout.addLayout(center_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setStyleSheet("background-color: #181a20;")


    def load_worlds(self):
        from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy
        from PyQt5.QtGui import QPixmap
        self.world_list.clear()
        if os.path.exists(MINECRAFT_WORLDS_PATH):
            for folder in os.listdir(MINECRAFT_WORLDS_PATH):
                world_path = os.path.join(MINECRAFT_WORLDS_PATH, folder)
                level_dat = os.path.join(world_path, "level.dat")
                levelname_txt = os.path.join(world_path, "levelname.txt")
                icon_path = os.path.join(world_path, "world_icon.png")
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(world_path, "icon.png")
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(world_path, "world_icon.jpeg")
                world_name = folder
                # Coba ambil dari levelname.txt
                if os.path.exists(levelname_txt):
                    try:
                        with open(levelname_txt, "r", encoding="utf-8") as f:
                            txt_name = f.read().strip()
                            if txt_name:
                                world_name = txt_name
                    except Exception:
                        pass
                # Jika tidak ada, fallback ke LevelName di level.dat
                elif os.path.exists(level_dat):
                    try:
                        nbt_data = nbtlib.load(level_dat, gzipped=True)
                        name_tag = nbt_data.root.get("LevelName")
                        if name_tag:
                            world_name = str(name_tag)
                    except Exception:
                        pass
                # Buat widget custom untuk world
                item_widget = QWidget()
                vbox = QVBoxLayout()
                vbox.setContentsMargins(15, 15, 15, 15)
                vbox.setSpacing(10)
                # Icon
                icon_label = QLabel()
                icon_label.setFixedSize(130, 90)
                icon_label.setAlignment(Qt.AlignCenter)
                icon_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                if os.path.exists(icon_path):
                    pixmap = QPixmap(icon_path)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(130, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        icon_label.setPixmap(pixmap)
                        icon_label.setStyleSheet("""
                            background-color: #1e2328;
                            border: 2px solid #404040;
                            border-radius: 8px;
                            margin-bottom: 4px;
                        """)
                    else:
                        icon_label.setText("🌍")
                        icon_label.setStyleSheet("""
                            background-color: #2d3139;
                            color: #00bfff;
                            border: 2px solid #404040;
                            border-radius: 8px;
                            font-size: 32px;
                            margin-bottom: 4px;
                        """)
                else:
                    icon_label.setText("🌍")
                    icon_label.setStyleSheet("""
                        background-color: #2d3139;
                        color: #00bfff;
                        border: 2px solid #404040;
                        border-radius: 8px;
                        font-size: 32px;
                        margin-bottom: 4px;
                    """)
                vbox.addWidget(icon_label, alignment=Qt.AlignHCenter)
                # Nama world dengan spacing yang cukup
                name_label = QLabel(world_name)
                name_label.setStyleSheet("""
                    color: #e1e1e1;
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    padding: 8px 10px;
                    margin-top: 8px;
                    background-color: rgba(30, 35, 40, 0.9);
                    border: 1px solid rgba(0, 191, 255, 0.3);
                    border-radius: 8px;
                """)
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setWordWrap(True)
                name_label.setMaximumHeight(50)  # Batasi tinggi untuk mencegah overlap
                vbox.addWidget(name_label)
                item_widget.setLayout(vbox)
                # Tambahkan ke QListWidget
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.world_list.addItem(item)
                self.world_list.setItemWidget(item, item_widget)

    def on_world_selected(self, item):
        # Cari folder berdasarkan urutan di world_list
        idx = self.world_list.row(item)
        folder = os.listdir(MINECRAFT_WORLDS_PATH)[idx]
        world_path = os.path.join(MINECRAFT_WORLDS_PATH, folder)
        level_dat = os.path.join(world_path, "level.dat")
        if os.path.exists(level_dat):
            self.nbt_file = level_dat
            try:
                # Deteksi format Bedrock/Java dengan magic bytes yang lebih akurat
                with open(level_dat, 'rb') as f:
                    first_8_bytes = f.read(8)
                    f.seek(0)
                    all_data = f.read(12)
                
                # Magic bytes untuk Bedrock Edition
                is_bedrock = (
                    first_8_bytes[:4] in [b'\x08\x00\x00\x00', b'\x0A\x00\x00\x00'] or  # Little endian header
                    first_8_bytes[:4] == b'\x00\x00\x00\x08' or  # Big endian
                    all_data[:4] in [b'\x08\x00\x00\x00', b'\x0A\x00\x00\x00'] or
                    len(first_8_bytes) >= 4 and first_8_bytes[0] in [0x08, 0x0A]  # NBT compound/list tag
                )
                
                nbt_data = None
                
                # Coba baca dengan amulet-nbt untuk Bedrock (jika tersedia)
                if is_bedrock and AMULET_AVAILABLE:
                    try:
                        print(f"Membaca {level_dat} sebagai Bedrock format dengan amulet-nbt...")
                        raw_nbt = amulet_load(level_dat)
                        print(f"Tipe raw_nbt: {type(raw_nbt)}")
                        print(f"Atribut raw_nbt: {dir(raw_nbt)}")
                        print(f"Raw NBT repr: {repr(raw_nbt)}")
                        
                        if hasattr(raw_nbt, 'compound'):
                            print(f"Compound ada, tipe: {type(raw_nbt.compound)}")
                            print(f"Compound keys: {list(raw_nbt.compound.keys()) if hasattr(raw_nbt.compound, 'keys') else 'no keys'}")
                        
                        nbt_data = self.nbt_to_dict(raw_nbt)
                        print(f"Hasil konversi nbt_to_dict: {len(nbt_data) if isinstance(nbt_data, dict) else 'not dict'} keys")
                        if isinstance(nbt_data, dict) and len(nbt_data) > 0:
                            print(f"Keys hasil konversi: {list(nbt_data.keys())[:10]}")  # Tampilkan 10 key pertama
                    except Exception as e:
                        print(f"amulet-nbt gagal: {e}, mencoba nbtlib...")
                        # Fallback ke nbtlib
                
                # Jika amulet-nbt tidak tersedia atau gagal, gunakan nbtlib
                if not AMULET_AVAILABLE or nbt_data is None:
                    try:
                        nbt_obj = nbtlib.load(level_dat)
                        nbt_data = getattr(nbt_obj, 'root', nbt_obj)
                    except Exception:
                        nbt_obj = nbtlib.load(level_dat, gzipped=True)
                        nbt_data = getattr(nbt_obj, 'root', nbt_obj)
                else:
                    # Untuk Java Edition, gunakan nbtlib
                    try:
                        print(f"Membaca {level_dat} sebagai Java format dengan nbtlib...")
                        nbt_obj = nbtlib.load(level_dat, gzipped=True)
                        nbt_data = getattr(nbt_obj, 'root', nbt_obj)
                    except Exception:
                        try:
                            nbt_obj = nbtlib.load(level_dat)
                            nbt_data = getattr(nbt_obj, 'root', nbt_obj)
                        except Exception as e:
                            # Jika gagal, coba amulet-nbt sebagai fallback (jika tersedia)
                            if AMULET_AVAILABLE:
                                print(f"nbtlib gagal: {e}, mencoba amulet-nbt...")
                                try:
                                    nbt_data = amulet_load(level_dat)
                                    nbt_data = self.nbt_to_dict(nbt_data)
                                except Exception as amulet_error:
                                    print(f"amulet-nbt juga gagal: {amulet_error}")
                            else:
                                print(f"nbtlib gagal: {e}, amulet-nbt tidak tersedia")
                
                # Jika kedua parser standar gagal, coba manual parser
                if nbt_data is None or (isinstance(nbt_data, dict) and len(nbt_data) == 0):
                    print("Parser standar gagal, mencoba manual parser untuk Bedrock...")
                    manual_data = self.parse_bedrock_level_dat_manual(level_dat)
                    if manual_data and len(manual_data) > 0:
                        nbt_data = manual_data
                        print(f"Manual parser berhasil mengekstrak {len(manual_data)} fields")
                    else:
                        raise Exception("Semua parser gagal membaca level.dat")
                
                if nbt_data is None:
                    raise Exception("File level.dat tidak dapat dibaca dengan metode apapun.")
                
                # Validasi bahwa data berisi struktur level.dat yang benar
                if isinstance(nbt_data, dict):
                    expected_keys = ['LevelName', 'GameType', 'Difficulty', 'Generator']
                    found_keys = [key for key in expected_keys if key in nbt_data]
                    print(f"Ditemukan {len(found_keys)} key level.dat yang diharapkan: {found_keys}")
                    if len(found_keys) == 0:
                        # Cek key alternatif dari manual parser
                        alt_keys = ['LevelName', 'InventoryVersion', 'Platform']  
                        found_alt = [key for key in alt_keys if key in nbt_data]
                        print(f"Ditemukan {len(found_alt)} key alternatif: {found_alt}")
                    
                self.nbt_data = nbt_data
                
                # Clear any previous search results
                self.clear_search()
                
                # Set flag untuk mencegah itemChanged signal saat populate
                self.is_programmatic_change = True
                
                self.tree.clear()
                self.populate_tree(self.nbt_data, self.tree.invisibleRootItem())
                
                # Reset flag setelah populate
                self.is_programmatic_change = False
                
                # Auto-expand first level untuk kemudahan navigasi
                self.tree.expandToDepth(0)
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka level.dat: {e}")
                msg.setStyleSheet("QLabel{color:#ff4444;font-size:15px;} QPushButton{color:#23272e;background:#ff4444;font-weight:bold;}")
                msg.exec_()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Buka File NBT/DAT/SNBT", "", "NBT/DAT/SNBT Files (*.nbt *.dat *.snbt *.txt)")
        if file_path:
            self.nbt_file = file_path
            try:
                # Jika file SNBT/text, parse manual
                if file_path.endswith('.snbt') or file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        snbt_text = f.read()
                    # SNBT sederhana: key: value\n
                    def parse_snbt(text):
                        tree = {}
                        for line in text.splitlines():
                            if ':' in line:
                                key, value = line.split(':', 1)
                                tree[key.strip()] = value.strip()
                        return tree
                    self.nbt_data = parse_snbt(snbt_text)
                    
                                        # Clear any previous search results
                    self.clear_search()
                    
                    # Set flag untuk mencegah itemChanged signal saat populate
                    self.is_programmatic_change = True
                    
                    self.tree.clear()
                    self.populate_tree(self.nbt_data, self.tree.invisibleRootItem())
                    
                    # Reset flag setelah populate
                    self.is_programmatic_change = False
                else:
                    # Gunakan logic parsing NBT yang sama seperti level.dat
                    nbt_data = None
                    
                    # Deteksi format file berdasarkan magic bytes
                    with open(file_path, 'rb') as f:
                        first_bytes = f.read(8)
                    
                    is_bedrock_format = (
                        first_bytes[:4] in [b'\x08\x00\x00\x00', b'\x0A\x00\x00\x00'] or
                        len(first_bytes) >= 4 and first_bytes[0] in [0x08, 0x0A]
                    )
                    
                    # Coba berbagai metode parsing
                    parsing_methods = []
                    
                    if is_bedrock_format:
                        parsing_methods = []
                        if AMULET_AVAILABLE:
                            parsing_methods.append(("amulet-nbt", lambda: self.nbt_to_dict(amulet_load(file_path))))
                        parsing_methods.extend([
                            ("nbtlib", lambda: nbtlib.load(file_path)),
                            ("nbtlib-gzipped", lambda: nbtlib.load(file_path, gzipped=True))
                        ])
                    else:
                        parsing_methods = [
                            ("nbtlib-gzipped", lambda: nbtlib.load(file_path, gzipped=True)),
                            ("nbtlib", lambda: nbtlib.load(file_path))
                        ]
                        if AMULET_AVAILABLE:
                            parsing_methods.append(("amulet-nbt", lambda: self.nbt_to_dict(amulet_load(file_path))))
                    
                    for method_name, method_func in parsing_methods:
                        try:
                            print(f"Mencoba parsing dengan {method_name}...")
                            nbt_data = method_func()
                            print(f"Berhasil dengan {method_name}")
                            break
                        except Exception as e:
                            print(f"{method_name} gagal: {e}")
                            continue
                    
                    if nbt_data is None:
                        raise Exception("Tidak dapat membaca file dengan metode parsing apapun")
                    
                    # Proses data NBT
                    self.nbt_data = nbt_data
                    
                    # Clear any previous search results
                    self.clear_search()
                    
                    self.tree.clear()
                    root_tag = getattr(nbt_data, 'root', nbt_data)
                    
                    if not hasattr(root_tag, 'items') and not isinstance(root_tag, (list, dict)):
                        QMessageBox.warning(self, "Kosong", "File tidak berisi data NBT yang dapat ditampilkan.")
                        return
                    
                    # Set flag untuk mencegah itemChanged signal saat populate
                    self.is_programmatic_change = True
                    
                    self.populate_tree(root_tag, self.tree.invisibleRootItem())
                    
                    # Reset flag setelah populate
                    self.is_programmatic_change = False
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka file: {e}")
                msg.setStyleSheet("QLabel{color:#ff4444;font-size:15px;} QPushButton{color:#23272e;background:#ff4444;font-weight:bold;}")
                msg.exec_()

    def save_file(self):
        if self.nbt_file and self.nbt_data:
            try:
                nbtlib.save(self.nbt_data, self.nbt_file)
                # Success message dengan styling yang match
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Sukses")
                msg.setText("File berhasil disimpan!")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #23272e;
                        color: #e1e1e1;
                    }
                    QMessageBox QPushButton {
                        background-color: #00d084;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                """)
                msg.exec_()
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal menyimpan file: {e}")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #23272e;
                        color: #e1e1e1;
                    }
                    QMessageBox QPushButton {
                        background-color: #ff4444;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                """)
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Peringatan")
            msg.setText("Tidak ada file yang terbuka untuk disimpan!")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #23272e;
                    color: #e1e1e1;
                }
                QMessageBox QPushButton {
                    background-color: #ff9500;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            msg.exec_()

    def get_nbt_value_display(self, value):
        """Menentukan format tampilan value untuk NBT"""
        if isinstance(value, dict):
            return f"{len(value)} entries"
        elif isinstance(value, list):
            return f"{len(value)} entries"
        elif isinstance(value, bool):
            return str(int(value))  # Display as 1 or 0
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, float):
            return str(value)
        elif isinstance(value, str):
            return value  # Show string without quotes for cleaner display
        else:
            return str(value)
    
    def populate_tree(self, nbt_node, parent_item, entry_count=None):
        # Tampilkan semua entri NBT sebagai tree dengan Key dan Value terpisah
        if isinstance(nbt_node, dict) or hasattr(nbt_node, 'items'):
            # dict atau compound tag
            items = dict(nbt_node.items()) if hasattr(nbt_node, 'items') else nbt_node
            
            # Urutkan kunci untuk konsistensi tampilan
            sorted_items = sorted(items.items(), key=lambda x: str(x[0]))
            
            for key, value in sorted_items:
                value_display = self.get_nbt_value_display(value)
                
                if isinstance(value, (dict, list)) or hasattr(value, 'items'):
                    # Untuk compound/list, tampilkan key dan jumlah entries
                    item = QTreeWidgetItem([str(key), value_display])
                    
                    # Set icon berdasarkan tipe  
                    if isinstance(value, dict):
                        item.setIcon(0, self.style().standardIcon(self.style().SP_DirIcon))
                    elif isinstance(value, list):
                        item.setIcon(0, self.style().standardIcon(self.style().SP_FileDialogDetailedView))
                    
                    parent_item.addChild(item)
                    self.populate_tree(value, item)
                else:
                    # Untuk nilai primitif - key di kolom 1, value di kolom 2
                    item = QTreeWidgetItem([str(key), value_display])
                    # Set hanya kolom Value (1) yang editable
                    item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    
                    # Set warna yang kontras untuk semua tipe data
                    if isinstance(value, int):
                        item.setForeground(1, QColor("#4da6ff"))  # Light blue untuk angka
                    elif isinstance(value, float):
                        item.setForeground(1, QColor("#ff6b6b"))  # Light red untuk float
                    elif isinstance(value, str):
                        item.setForeground(1, QColor("#51cf66"))  # Light green untuk string
                    else:
                        item.setForeground(1, QColor("#e1e1e1"))  # Default light gray
                    
                    parent_item.addChild(item)
                    
        elif isinstance(nbt_node, list):
            # List NBT - tampilkan index sebagai key
            for idx, value in enumerate(nbt_node):
                value_display = self.get_nbt_value_display(value)
                
                if isinstance(value, (dict, list)) or hasattr(value, 'items'):
                    item = QTreeWidgetItem([f"[{idx}]", value_display])
                    parent_item.addChild(item)
                    self.populate_tree(value, item)
                else:
                    item = QTreeWidgetItem([f"[{idx}]", value_display])
                    # Set hanya kolom Value (1) yang editable
                    item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    parent_item.addChild(item)
        else:
            # Nilai tunggal
            value_display = self.get_nbt_value_display(nbt_node)
            item = QTreeWidgetItem(["Value", value_display])
            parent_item.addChild(item)

    def on_tree_item_double_clicked(self, item, column):
        """Handle double-click untuk inline editing"""
        # Hanya allow edit pada kolom Value (column 1) dan untuk item yang bukan compound/list
        if column == 1 and not item.text(1).endswith(" entries"):
            # Set item sebagai editable untuk inline editing
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.tree.editItem(item, column)

    def on_item_changed(self, item, column):
        """Handle perubahan value dengan dialog konfirmasi"""
        # Skip if this is a programmatic change (search, color updates, etc.)
        if self.is_programmatic_change:
            return
            
        if column == 1:  # Hanya untuk kolom Value
            # Tampilkan dialog konfirmasi seperti di foto
            reply = self.show_confirmation_dialog(item.text(0), item.text(1))
            if reply == QMessageBox.Yes:
                # Konfirm perubahan
                print(f"Value changed for {item.text(0)}: {item.text(1)}")
                # TODO: Update actual NBT data structure
                pass
            else:
                # Batalkan perubahan - restore nilai asli jika diperlukan
                pass
    
    def show_confirmation_dialog(self, key, new_value):
        """Tampilkan dialog konfirmasi seperti di foto"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirm")
        msg.setText(f"Change '{key}' to '{new_value}'?")
        
        # Style dialog seperti tema aplikasi
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #23272e;
                color: #e1e1e1;
            }
            QMessageBox QPushButton {
                background-color: #00bfff;
                color: #23272e;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #0099cc;
            }
        """)
        
        # Set custom buttons
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        # Ubah text button menjadi "Confirm" dan "Cancel"
        yes_button = msg.button(QMessageBox.Yes)
        no_button = msg.button(QMessageBox.No)
        yes_button.setText("Confirm")
        no_button.setText("Cancel")
        
        return msg.exec_()
    
    def show_all_items(self):
        """Tampilkan kembali semua items yang disembunyikan dan reset colors"""
        # Set flag untuk mencegah itemChanged signal jika belum di-set
        was_programmatic = self.is_programmatic_change
        if not was_programmatic:
            self.is_programmatic_change = True
        
        def show_all_recursive(parent_item):
            """Recursively show all tree items"""
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                # Show the item
                child.setHidden(False)
                # Reset background dan foreground colors
                child.setBackground(0, QColor("transparent"))
                child.setBackground(1, QColor("transparent"))
                self.restore_item_colors(child)
                # Continue with children
                show_all_recursive(child)
        
        # Start from root
        show_all_recursive(self.tree.invisibleRootItem())
        
        # Reset flag hanya jika kita yang set (tidak override flag yang sudah ada)
        if not was_programmatic:
            self.is_programmatic_change = False
    
    def on_search_text_changed(self):
        """Handle text changes in search input untuk live search"""
        # Stop previous timer jika ada
        self.search_timer.stop()
        
        search_text = self.search_input.text().strip()
        
        if not search_text:
            # Jika search box kosong, tampilkan semua items
            # Set flag untuk mencegah itemChanged signal
            self.is_programmatic_change = True
            
            self.show_all_items()
            self.search_results = []
            self.search_status.setText("Siap untuk mencari...")
            self.search_status.setStyleSheet("""
                color: #888888;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 8px;
            """)
            # Reset search input style
            self.update_search_input_style("#404040")
            # Reset window title
            self.setWindowTitle("Bedrock NBT/DAT Editor")
            
            # Reset flag setelah selesai
            self.is_programmatic_change = False
            return
        
        # Update status saat mengetik
        self.search_status.setText(f"Mencari '{search_text}'...")
        self.search_status.setStyleSheet("""
            color: #00bfff;
            font-size: 12px;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 4px 8px;
        """)
        
        # Start timer dengan delay 300ms untuk debouncing
        self.search_timer.start(300)
    
    def perform_live_search(self):
        """Perform actual search dengan filter hasil - hanya tampilkan yang cocok"""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
        
        # Set flag untuk mencegah itemChanged signal
        self.is_programmatic_change = True
        
        # Reset previous search state
        self.show_all_items()
        
        # Search through tree items dan hide yang tidak cocok
        found_items = []
        all_items = []
        
        def collect_and_filter_items(parent_item):
            """Recursively collect dan filter tree items"""
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                all_items.append(child)
                key_text = child.text(0).lower()
                
                # Check if search term matches key name
                if search_text.lower() in key_text:
                    found_items.append(child)
                    # Highlight the found item
                    child.setBackground(0, QColor("#ff6b35"))  # Orange background for key
                    child.setBackground(1, QColor("#ff6b35"))  # Orange background for value
                    child.setForeground(0, QColor("#ffffff"))  # White text for key
                    child.setForeground(1, QColor("#ffffff"))  # White text for value
                    
                    # Show this item dan semua parent-nya
                    child.setHidden(False)
                    parent = child.parent()
                    while parent and parent != self.tree.invisibleRootItem():
                        parent.setHidden(False)
                        self.tree.expandItem(parent)
                        parent = parent.parent()
                else:
                    # Hide item yang tidak cocok
                    child.setHidden(True)
                
                # Continue searching in children
                collect_and_filter_items(child)
        
        # Start search from root
        collect_and_filter_items(self.tree.invisibleRootItem())
        
        # Store results and update UI
        self.search_results = found_items
        
        if found_items:
            # Scroll to first result and select it
            self.tree.setCurrentItem(found_items[0])
            self.tree.scrollToItem(found_items[0])
            
            # Show success status
            self.search_status.setText(f"✓ Menampilkan {len(found_items)} dari {len(all_items)} item untuk '{search_text}'")
            self.search_status.setStyleSheet("""
                color: #00d084;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 8px;
                font-weight: bold;
            """)
            
            # Green border untuk success
            self.update_search_input_style("#00d084")
            
            # Update window title dengan search results count
            original_title = "Bedrock NBT/DAT Editor"
            self.setWindowTitle(f"{original_title} - Filtered: {len(found_items)}/{len(all_items)} items")
        else:
            # Show no results status - hide semua items
            for item in all_items:
                item.setHidden(True)
            
            self.search_status.setText(f"✗ Tidak ada hasil untuk '{search_text}' - {len(all_items)} item disembunyikan")
            self.search_status.setStyleSheet("""
                color: #ff6b6b;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 8px;
                font-weight: bold;
            """)
            
            # Red border untuk no results
            self.update_search_input_style("#ff6b6b")
        
        # Reset flag setelah selesai programmatic changes
        self.is_programmatic_change = False
    
    def update_search_input_style(self, border_color):
        """Update search input border color"""
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2d3139;
                color: #e1e1e1;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 16px;
            }}
            QLineEdit:focus {{
                border: 2px solid #00bfff;
                background-color: #23272e;
            }}
            QLineEdit::placeholder {{
                color: #888888;
                font-style: italic;
            }}
        """)
    
    def restore_item_colors(self, item):
        """Restore original colors untuk item"""
        # Ensure programmatic flag is set untuk color changes
        was_programmatic = self.is_programmatic_change
        if not was_programmatic:
            self.is_programmatic_change = True
        
        key_text = item.text(0)
        value_text = item.text(1)
        
        # Set default key color
        item.setForeground(0, QColor("#e1e1e1"))
        
        # Set value color based on data type (same logic as populate_tree)
        if not value_text.endswith(" entries"):  # Not a compound/list
            # Try to determine data type from value
            try:
                # Check if it's a number
                if '.' in value_text:
                    float(value_text)
                    item.setForeground(1, QColor("#ff6b6b"))  # Light red untuk float
                else:
                    int(value_text)
                    item.setForeground(1, QColor("#4da6ff"))  # Light blue untuk angka
            except ValueError:
                # It's a string
                item.setForeground(1, QColor("#51cf66"))  # Light green untuk string
        else:
            item.setForeground(1, QColor("#e1e1e1"))  # Default light gray for compounds
        
        # Reset flag hanya jika kita yang set
        if not was_programmatic:
            self.is_programmatic_change = False
    
    def clear_search(self):
        """Clear search results dan restore original appearance"""
        # Stop search timer jika ada
        self.search_timer.stop()
        
        # Set flag untuk mencegah itemChanged signal
        self.is_programmatic_change = True
        
        # Show all items dan restore colors
        self.show_all_items()
        
        # Clear search results list
        self.search_results = []
        
        # Clear search input
        self.search_input.clear()
        
        # Reset search status
        self.search_status.setText("Siap untuk mencari...")
        self.search_status.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 4px 8px;
        """)
        
        # Reset search input style
        self.update_search_input_style("#404040")
        
        # Reset window title
        self.setWindowTitle("Bedrock NBT/DAT Editor")
        
        # Collapse all tree items untuk clean view
        self.tree.collapseAll()
        
        # Expand only first level
        if self.tree.topLevelItemCount() > 0:
            self.tree.expandToDepth(0)
        
        # Reset flag setelah selesai programmatic changes
        self.is_programmatic_change = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditor()
    window.show()
    sys.exit(app.exec_())
