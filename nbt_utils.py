import struct

def nbt_to_dict(nbt, depth=0):
    """Konversi tag amulet-nbt ke dict Python untuk Bedrock level.dat dengan proper type handling"""
    try:
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

def format_value_for_json(value):
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
        else:
            return value  # Keep integers as-is, don't convert 0/1 to boolean format
    elif isinstance(value, float):
        return f"{value}f"  # Format as float with f suffix
    elif isinstance(value, str):
        return value  # Keep as string
    else:
        return str(value)

def get_value_type_icon(value):
    """Get icon type for value display"""
    if isinstance(value, dict):
        return "folder"  # Compound tag
    elif isinstance(value, list):
        return "list"    # List tag
    elif isinstance(value, bool):
        return "B"       # Byte/Boolean
    elif isinstance(value, int):
        if abs(value) > 2147483647:
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
        # Special handling for version arrays - they should be all integers
        if parent_key and 'version' in parent_key.lower():
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
    """Check if a key name suggests the value should be treated as boolean"""
    if not key_name:
        return False
    
    key_lower = key_name.lower()
    
    # Common boolean patterns - no hardcoded specific keys
    boolean_patterns = [
        'enabled', 'disabled', 'attack', 'build', 'flying', 'invulnerable',
        'lightning', 'mayfly', 'mine', 'op', 'teleport', 'instabuild',
        'hardcore', 'broadcast', 'intent', 'multiplayer', 'cheats',
        'commands', 'daylight', 'entity', 'fire', 'immediate',
        'insomnia', 'limited', 'mob', 'tile', 'weather', 'drowning',
        'fall', 'freeze', 'immutable', 'locked', 'random', 'single',
        'template', 'keep', 'natural', 'projectile', 'pvp', 'recipe',
        'require', 'respawn', 'send', 'show', 'spawn', 'start',
        'texture', 'tnt', 'use', 'world', 'output', 'blocks',
        'damage', 'griefing', 'regeneration', 'sleeping', 'drops',
        'spawning', 'explode', 'feedback', 'border', 'coordinates',
        'days', 'death', 'recipe', 'tags', 'mobs', 'radius',
        'map', 'packs', 'explosion', 'decay', 'gamertags'
    ]
    
    # Check if any pattern matches
    for pattern in boolean_patterns:
        if pattern in key_lower:
            return True
    
    return False
