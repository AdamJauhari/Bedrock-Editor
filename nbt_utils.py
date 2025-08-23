import struct

def nbt_to_dict(nbt, depth=0):
    """Konversi tag amulet-nbt ke dict Python untuk Bedrock level.dat"""
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
