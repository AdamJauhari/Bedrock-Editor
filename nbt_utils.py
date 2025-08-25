import struct

def nbt_to_dict(nbt, depth=0):
    """Konversi tag amulet-nbt ke dict Python untuk Bedrock level.dat dengan proper type handling"""
    try:
        # Handle NBT tag objects (nbtlib.tag.*)
        if hasattr(nbt, 'tag_id'):
            # Extract actual value from NBT tag
            if hasattr(nbt, 'value'):
                return nbt_to_dict(nbt.value, depth+1)
            elif hasattr(nbt, 'py_data'):
                return nbt.py_data
            elif hasattr(nbt, 'py_int'):
                return nbt.py_int
            elif hasattr(nbt, 'py_float'):
                return nbt.py_float
            elif hasattr(nbt, 'py_str'):
                return nbt.py_str
            elif hasattr(nbt, 'py_bool'):
                return nbt.py_bool
            else:
                # Fallback: try to convert to string and extract value
                str_value = str(nbt)
                if '(' in str_value and ')' in str_value:
                    # Extract value from format like "Byte(1)" or "Int(42)"
                    try:
                        actual_value = str_value.split('(')[1].split(')')[0]
                        # Convert to appropriate type
                        if '.' in actual_value:
                            return float(actual_value)
                        elif actual_value.lower() in ['true', 'false']:
                            return actual_value.lower() == 'true'
                        else:
                            return int(actual_value)
                    except:
                        pass
                return str_value
        
        # Handle NamedTag Bedrock (level.dat root structure)
        if hasattr(nbt, 'compound'):
            return nbt_to_dict(nbt.compound, depth+1)
        # Handle amulet CompoundTag atau dictionary-like structures
        elif hasattr(nbt, 'items') and callable(getattr(nbt, 'items')):
            result = {}
            for k, v in nbt.items():
                try:
                    key_str = str(k)
                    result[key_str] = nbt_to_dict(v, depth+1)
                except Exception:
                    result[str(k)] = str(v)
            return result
        # Handle Python dict
        elif isinstance(nbt, dict):
            result = {}
            for k, v in nbt.items():
                try:
                    result[str(k)] = nbt_to_dict(v, depth+1)
                except Exception:
                    result[str(k)] = str(v)
            return result
        # Handle List tags atau Python list
        elif isinstance(nbt, list) or (hasattr(nbt, '__iter__') and hasattr(nbt, '__len__')):
            result = []
            for v in nbt:
                try:
                    result.append(nbt_to_dict(v, depth+1))
                except Exception:
                    result.append(str(v))
            return result
        # Handle NBT tags with value attribute
        elif hasattr(nbt, 'value'):
            return nbt_to_dict(nbt.value, depth+1)
        # Handle NBT arrays with py_data
        elif hasattr(nbt, 'py_data'):
            return nbt.py_data
        # Handle primitive values
        else:
            return nbt
    except Exception:
        # Fallback to string representation if conversion fails
        return str(nbt)

def get_nbt_value_display(value):
    """Menentukan format tampilan value untuk NBT dengan proper type formatting"""
    # Handle NBT tag objects (nbtlib tags)
    if hasattr(value, 'tag_id'):
        # Extract the actual value from NBT tag
        if hasattr(value, 'value'):
            return str(value.value)
        else:
            return str(value)
    
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



def get_value_type_icon(value, key_name=None):
    """Get icon type for value display"""
    if isinstance(value, dict):
        return "folder"  # Compound tag
    elif isinstance(value, list):
        return "list"    # List tag
    elif isinstance(value, bool):
        return "B"       # Byte/Boolean
    elif isinstance(value, int):
        # Check if this should be a boolean based on value and key patterns
        if value in [0, 1] and key_name and _is_boolean_key(key_name):
            return "B"   # Byte/Boolean
        elif abs(value) > 2147483647:
            return "L"   # Long
        else:
            return "I"   # Integer
    elif isinstance(value, float):
        return "F"       # Float
    elif isinstance(value, str):
        return "S"       # String
    else:
        return "?"       # Unknown

def convert_to_json_format(data, parent_key=None):
    """Convert NBT data to JSON format matching user's specification"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = convert_to_json_format(value, key)
        return result
    elif isinstance(data, list):
        # 🔧 Auto-detect version arrays based on content and context
        is_version_array = False
        
        # Check if parent key suggests version
        if parent_key and 'version' in parent_key.lower():
            is_version_array = True
        
        # Check if all elements are integers (common for version arrays)
        if len(data) > 0 and all(isinstance(item, int) for item in data):
            is_version_array = True
        
        if is_version_array:
            return [format_value_for_json(item, None) for item in data]  # Don't treat as boolean
        else:
            return [convert_to_json_format(item, parent_key) for item in data]
    else:
        return format_value_for_json(data, parent_key)

def format_value_for_json(value, key_name=None):
    """Format value untuk JSON output sesuai dengan spesifikasi user"""
    if isinstance(value, dict):
        return value
    elif isinstance(value, list):
        return value
    elif isinstance(value, bool):
        return f"{int(value)}b"  # Format as 0b or 1b
    elif isinstance(value, int):
        # Check if it's a large number that should be formatted as long
        if abs(value) > 2147483647:  # Max 32-bit signed int
            return f"{value}L"
        # Check if it's a boolean value (0 or 1) that should be formatted as 0b or 1b
        # Only convert to boolean format if the key name suggests it's a boolean
        elif value in [0, 1] and key_name and _is_boolean_key(key_name):
            return f"{value}b"  # Format as 0b or 1b
        else:
            return value  # Keep integers as-is
    elif isinstance(value, float):
        return f"{value}f"  # Format as float with f suffix
    elif isinstance(value, str):
        return value  # Keep as string
    else:
        return str(value)

def _is_boolean_key(key_name):
    """Check if a key name suggests the value should be treated as boolean using auto-detection"""
    if not key_name:
        return False
    
    key_lower = key_name.lower()
    
    # 🔧 Exclude keys that should NOT be boolean
    non_boolean_exclusions = [
        'worldversion', 'editorworldtype', 'eduoffer', 'permissionlevel', 
        'playerpermissionlevel', 'randomtickspeed', 'lastplayed', 'currenttick',
        'gametype', 'generator', 'randomseed', 'lightninglevel', 'rainlevel',
        'difficulty', 'storageversion', 'networkversion', 'platform', 'netherscale', 
        'time', 'lightningtime', 'raintime', 'limitedworlddepth', 'limitedworldwidth', 
        'maxcommandchainlength', 'permissionslevel', 'playerpermissionslevel', 
        'playerssleepingpercentage', 'serverchunktickrange', 'spawnradius', 
        'worldstartcount', 'functioncommandlimit', 'limitedworldoriginx', 
        'limitedworldoriginy', 'limitedworldoriginz', 'spawnx', 'spawny', 'spawnz', 
        'platformbroadcastintent', 'xblbroadcastintent', 'daylightcycle', 'lanbroadcastintent'
    ]
    
    # Check exclusions first
    for exclusion in non_boolean_exclusions:
        if exclusion in key_lower:
            return False
    
    # 🔧 Use auto-detected patterns if available (this will be set by the parser)
    # For now, use basic detection patterns
    basic_boolean_patterns = [
        'enabled', 'disabled', 'true', 'false', 'on', 'off'
    ]
    
    # Check if key contains basic boolean patterns
    for pattern in basic_boolean_patterns:
        if pattern in key_lower:
            return True
    
    # Check if key starts with common boolean prefixes
    boolean_prefixes = ['is', 'has', 'can', 'do', 'show', 'allow']
    for prefix in boolean_prefixes:
        if key_lower.startswith(prefix):
            return True
    
    # Check if key ends with common boolean suffixes
    boolean_suffixes = ['enabled', 'disabled', 'allowed', 'active']
    for suffix in boolean_suffixes:
        if key_lower.endswith(suffix):
            return True
    
    # Check for specific boolean patterns that are very reliable
    specific_boolean_patterns = [
        'attack', 'build', 'flying', 'invulnerable', 'lightning', 'mayfly', 'mine', 'op', 'teleport',
        'instabuild', 'hardcore', 'broadcast', 'intent', 'multiplayer', 'cheats', 'commands',
        'entity', 'fire', 'immediate', 'insomnia', 'limited', 'mob', 'tile', 'weather', 'drowning',
        'fall', 'freeze', 'immutable', 'locked', 'random', 'single', 'template', 'keep', 'natural',
        'projectile', 'pvp', 'recipe', 'require', 'respawn', 'send', 'spawn', 'start', 'texture',
        'tnt', 'use', 'world', 'output', 'blocks', 'damage', 'griefing', 'regeneration', 'sleeping',
        'drops', 'spawning', 'explode', 'feedback', 'border', 'coordinates', 'days', 'death', 'tags',
        'mobs', 'radius', 'map', 'packs', 'explosion', 'decay', 'gamertags', 'doorsandswitches',
        'opencontainers', 'bonuschest', 'commandblock', 'education'
    ]
    
    for pattern in specific_boolean_patterns:
        if pattern in key_lower:
            return True
    
    return False

