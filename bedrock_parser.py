import struct
import re
import nbtlib
import gzip
import io

# Import AMULET_AVAILABLE from package_manager
try:
    from package_manager import AMULET_AVAILABLE, amulet_load
except ImportError:
    AMULET_AVAILABLE = False
    amulet_load = None

class BedrockParser:
    """Advanced parser untuk Bedrock level.dat dengan complete NBT support"""
    
    # NBT Tag Types
    TAG_END = 0
    TAG_BYTE = 1
    TAG_SHORT = 2
    TAG_INT = 3
    TAG_LONG = 4
    TAG_FLOAT = 5
    TAG_DOUBLE = 6
    TAG_BYTE_ARRAY = 7
    TAG_STRING = 8
    TAG_LIST = 9
    TAG_COMPOUND = 10
    TAG_INT_ARRAY = 11
    TAG_LONG_ARRAY = 12
    
    def parse_bedrock_level_dat_manual(self, file_path):
        """
        Complete NBT parser untuk Bedrock level.dat yang bisa membaca 100% data
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            print(f"Parsing {len(data)} bytes from {file_path}")
            
            # Try different parsing methods in order of preference
            result = {}
            
            # Method 1: Try amulet-nbt (best for Bedrock)
            if AMULET_AVAILABLE and amulet_load:
                try:
                    print("Trying amulet-nbt parser...")
                    nbt_data = amulet_load(file_path)
                    result = self._convert_amulet_nbt_to_dict(nbt_data)
                    if result and len(result) > 0:
                        print(f"✅ amulet-nbt successful: {len(result)} keys detected")
                        return result
                except Exception as e:
                    print(f"❌ amulet-nbt failed: {e}")
            
            # Method 2: Try nbtlib with different options
            for gzipped in [False, True]:
                try:
                    print(f"Trying nbtlib parser (gzipped={gzipped})...")
                    nbt_data = nbtlib.load(file_path, gzipped=gzipped)
                    print(f"nbtlib loaded data type: {type(nbt_data)}")
                    print(f"nbtlib data attributes: {dir(nbt_data)}")
                    result = self._convert_nbtlib_to_dict(nbt_data)
                    print(f"Converted result type: {type(result)}")
                    print(f"Converted result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                    if result and len(result) > 0:
                        print(f"✅ nbtlib (gzipped={gzipped}) successful: {len(result)} keys detected")
                        # Validate that we got meaningful data
                        if len(result) > 10:  # Should have more than 10 keys
                            return result
                        else:
                            print(f"⚠️  nbtlib returned only {len(result)} keys, trying next method")
                except Exception as e:
                    print(f"❌ nbtlib (gzipped={gzipped}) failed: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Method 3: Manual NBT parser as fallback
            print("Trying manual NBT parser...")
            result = self._parse_nbt_manual(data)
            if result and len(result) > 0:
                print(f"✅ Manual parser successful: {len(result)} keys detected")
                return result
            
            print("❌ All parsing methods failed")
            return {}
            
        except Exception as e:
            print(f"Parser failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _convert_amulet_nbt_to_dict(self, nbt_data):
        """Convert amulet-nbt data to Python dict with proper type handling"""
        try:
            if hasattr(nbt_data, 'compound'):
                return self._convert_amulet_nbt_to_dict(nbt_data.compound)
            elif hasattr(nbt_data, 'items') and callable(getattr(nbt_data, 'items')):
                result = {}
                for k, v in nbt_data.items():
                    key_str = str(k)
                    result[key_str] = self._convert_amulet_value(v)
                return result
            elif isinstance(nbt_data, dict):
                result = {}
                for k, v in nbt_data.items():
                    result[str(k)] = self._convert_amulet_value(v)
                return result
            else:
                return self._convert_amulet_value(nbt_data)
        except Exception as e:
            print(f"Error converting amulet-nbt: {e}")
            return {}
    
    def _convert_amulet_value(self, value):
        """Convert individual amulet-nbt value with proper type preservation"""
        try:
            if hasattr(value, 'value'):
                return self._convert_amulet_value(value.value)
            elif hasattr(value, 'py_data'):
                return value.py_data
            elif hasattr(value, 'items') and callable(getattr(value, 'items')):
                result = {}
                for k, v in value.items():
                    result[str(k)] = self._convert_amulet_value(v)
                return result
            elif isinstance(value, (list, tuple)):
                return [self._convert_amulet_value(v) for v in value]
            else:
                return value
        except Exception:
            return str(value)
    
    def _convert_nbtlib_to_dict(self, nbt_data):
        """Convert nbtlib data to Python dict with proper type handling"""
        try:
            print(f"Converting nbtlib data: {type(nbt_data)}")
            
            # Handle nbtlib.File objects
            if hasattr(nbt_data, 'root'):
                print(f"Found root attribute: {nbt_data.root}")
                return self._convert_nbtlib_value(nbt_data.root)
            elif hasattr(nbt_data, 'items'):
                print(f"Data has items method, converting directly")
                return self._convert_nbtlib_value(nbt_data)
            else:
                print(f"No root or items found, trying direct conversion")
                return self._convert_nbtlib_value(nbt_data)
        except Exception as e:
            print(f"Error converting nbtlib: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _convert_nbtlib_value(self, value):
        """Convert individual nbtlib value with proper type preservation"""
        try:
            print(f"Converting value: {type(value)} - {value}")
            
            if hasattr(value, 'items') and callable(getattr(value, 'items')):
                print(f"Converting dict-like object with {len(list(value.items()))} items")
                result = {}
                for k, v in value.items():
                    print(f"Converting key: {k} -> {type(v)}")
                    result[str(k)] = self._convert_nbtlib_value(v)
                return result
            elif isinstance(value, (list, tuple)):
                print(f"Converting list/tuple with {len(value)} items")
                return [self._convert_nbtlib_value(v) for v in value]
            elif hasattr(value, 'value'):
                print(f"Converting value attribute: {value.value}")
                return self._convert_nbtlib_value(value.value)
            elif hasattr(value, 'py_data'):
                print(f"Converting py_data: {value.py_data}")
                return value.py_data
            elif hasattr(value, 'py_int'):
                print(f"Converting py_int: {value.py_int}")
                return value.py_int
            elif hasattr(value, 'py_float'):
                print(f"Converting py_float: {value.py_float}")
                return value.py_float
            elif hasattr(value, 'py_str'):
                print(f"Converting py_str: {value.py_str}")
                return value.py_str
            elif hasattr(value, 'py_bool'):
                print(f"Converting py_bool: {value.py_bool}")
                return value.py_bool
            else:
                print(f"Returning value as-is: {value}")
                return value
        except Exception as e:
            print(f"Error converting nbtlib value: {e}")
            import traceback
            traceback.print_exc()
            return str(value)
    
    def _parse_nbt_manual(self, data):
        """Manual NBT parser that handles all tag types"""
        try:
            # Check if data is gzipped
            if data[:2] == b'\x1f\x8b':
                print("Detected gzipped data, decompressing...")
                try:
                    data = gzip.decompress(data)
                except Exception as e:
                    print(f"Failed to decompress gzipped data: {e}")
                    return {}
            
            # Start parsing from the beginning
            pos = 0
            result = {}
            
            # Try different byte orders and formats
            if len(data) < 4:
                print("Data too short")
                return {}
            # Check for different possible headers and try multiple approaches
            possible_headers = [
                (b'\x0A', '>'),  # Compound tag, big endian
                (b'\x08', '>'),  # List tag, big endian
                (b'\x0A', '<'),  # Compound tag, little endian
                (b'\x08', '<'),  # List tag, little endian
            ]
            # Try each header approach
            for header_byte, endian in possible_headers:
                if data[pos] == header_byte[0]:
                    print(f"Detected header: {header_byte.hex()} with {endian} endian")
                    pos += 1
                    # Read name length
                    if pos + 2 <= len(data):
                        try:
                            if endian == '>':
                                name_length = struct.unpack('>H', data[pos:pos+2])[0]
                            else:
                                name_length = struct.unpack('<H', data[pos:pos+2])[0]
                            pos += 2
                            if pos + name_length <= len(data):
                                compound_name = data[pos:pos+name_length].decode('utf-8', errors='replace')
                                pos += name_length
                                print(f"Found compound: {compound_name}")
                                # Parse compound contents
                                compound_data, new_pos = self._parse_compound_manual(data, pos, endian)
                                result = compound_data
                                pos = new_pos
                                break
                            else:
                                print("Invalid compound name length")
                        except Exception as e:
                            print(f"Error reading compound name: {e}")
                            continue
                    else:
                        print("Not enough data for compound name")
                        continue
            
            if not result:
                print("No valid NBT structure found")
                # Try a more aggressive parsing approach
                result = self._parse_aggressive_nbt(data)
            
            return result
            
        except Exception as e:
            print(f"Manual NBT parser error: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _parse_aggressive_nbt(self, data):
        """More aggressive NBT parsing that tries to find valid NBT structures with multiple strategies"""
        try:
            print("Trying aggressive NBT parsing...")
            best_result = {}
            best_count = 0
            # Strategy 1: Try different starting positions
            for start_pos in range(min(20, len(data))):
                result = self._try_parse_from_position(data, start_pos)
                if len(result) > best_count:
                    best_result = result
                    best_count = len(result)
                    print(f"Found {len(result)} keys starting from position {start_pos}")
            # Strategy 2: Try different endianness combinations for specific keys
            if best_count < 50:
                for name_endian in ['>', '<']:
                    for value_endian in ['>', '<']:
                        result = self._try_parse_with_endianness(data, name_endian, value_endian)
                        if len(result) > best_count:
                            best_result = result
                            best_count = len(result)
                            print(f"Found {len(result)} keys with {name_endian}/{value_endian} endianness")
            return best_result
        except Exception as e:
            print(f"Error in aggressive parsing: {e}")
            return {}
    
    def _try_parse_from_position(self, data, start_pos):
        """Try to parse NBT from a specific starting position"""
        result = {}
        pos = start_pos
        while pos < len(data) - 10:
            if data[pos] in [self.TAG_BYTE, self.TAG_SHORT, self.TAG_INT, self.TAG_LONG, self.TAG_FLOAT, self.TAG_DOUBLE, self.TAG_STRING, self.TAG_LIST, self.TAG_COMPOUND, self.TAG_BYTE_ARRAY, self.TAG_INT_ARRAY, self.TAG_LONG_ARRAY]:
                tag_type = data[pos]
                pos += 1
                if pos + 2 <= len(data):
                    try:
                        for endian in ['>', '<']:
                            try:
                                name_length = struct.unpack(f'{endian}H', data[pos:pos+2])[0]
                                if 1 <= name_length <= 100:
                                    pos += 2
                                    if pos + name_length <= len(data):
                                        tag_name = data[pos:pos+name_length].decode('utf-8', errors='replace')
                                        pos += name_length
                                        value, new_pos = self._parse_tag_value_manual(data, pos, tag_type, endian)
                                        if value is not None:
                                            result[tag_name] = value
                                        pos = new_pos
                                        break
                            except Exception:
                                continue
                    except Exception:
                        pos += 1
                        continue
                else:
                    pos += 1
            else:
                pos += 1
        return result
    
    def _try_parse_with_endianness(self, data, name_endian, value_endian):
        result = {}
        pos = 0
        while pos < len(data) - 10:
            if data[pos] in [self.TAG_BYTE, self.TAG_SHORT, self.TAG_INT, self.TAG_LONG, self.TAG_FLOAT, self.TAG_DOUBLE, self.TAG_STRING, self.TAG_LIST, self.TAG_COMPOUND, self.TAG_BYTE_ARRAY, self.TAG_INT_ARRAY, self.TAG_LONG_ARRAY]:
                tag_type = data[pos]
                pos += 1
                if pos + 2 <= len(data):
                    try:
                        name_length = struct.unpack(f'{name_endian}H', data[pos:pos+2])[0]
                        if 1 <= name_length <= 100:
                            pos += 2
                            if pos + name_length <= len(data):
                                tag_name = data[pos:pos+name_length].decode('utf-8', errors='replace')
                                pos += name_length
                                value, new_pos = self._parse_tag_value_manual(data, pos, tag_type, value_endian)
                                if value is not None:
                                    result[tag_name] = value
                                pos = new_pos
                            else:
                                pos += 1
                        else:
                            pos += 1
                    except Exception:
                        pos += 1
                        continue
                else:
                    pos += 1
            else:
                pos += 1
        return result
    

    
    def _parse_compound_manual(self, data, pos, endian='>'):
        """Parse a compound tag and return its contents"""
        result = {}
        
        while pos < len(data):
            tag_type = data[pos]
            pos += 1
            
            if tag_type == self.TAG_END:
                break
            
            # Read tag name
            if pos + 2 <= len(data):
                try:
                    if endian == '>':
                        name_length = struct.unpack('>H', data[pos:pos+2])[0]
                    else:
                        name_length = struct.unpack('<H', data[pos:pos+2])[0]
                    pos += 2
                    
                    if pos + name_length <= len(data):
                        tag_name = data[pos:pos+name_length].decode('utf-8', errors='replace')
                        pos += name_length
                        
                        # Parse tag value based on type
                        value, new_pos = self._parse_tag_value_manual(data, pos, tag_type, endian)
                        result[tag_name] = value
                        pos = new_pos
                    else:
                        print("Invalid tag name length")
                        break
                except Exception as e:
                    print(f"Error reading tag name: {e}")
                    break
            else:
                print("Not enough data for tag name")
                break
        
        return result, pos
    
    def _parse_tag_value_manual(self, data, pos, tag_type, endian='>'):
        """Parse a tag value based on its type"""
        try:
            if tag_type == self.TAG_END:
                return None, pos
            elif tag_type == self.TAG_BYTE:
                if pos + 1 <= len(data):
                    value = struct.unpack('>b', data[pos:pos+1])[0]
                    return value, pos + 1
            elif tag_type == self.TAG_SHORT:
                if pos + 2 <= len(data):
                    if endian == '>':
                        value = struct.unpack('>h', data[pos:pos+2])[0]
                    else:
                        value = struct.unpack('<h', data[pos:pos+2])[0]
                    return value, pos + 2
            elif tag_type == self.TAG_INT:
                if pos + 4 <= len(data):
                    if endian == '>':
                        value = struct.unpack('>i', data[pos:pos+4])[0]
                    else:
                        value = struct.unpack('<i', data[pos:pos+4])[0]
                    return value, pos + 4
            elif tag_type == self.TAG_LONG:
                if pos + 8 <= len(data):
                    # Try both endianness for long values to get the correct one
                    try:
                        if endian == '>':
                            value = struct.unpack('>q', data[pos:pos+8])[0]
                        else:
                            value = struct.unpack('<q', data[pos:pos+8])[0]
                        return value, pos + 8
                    except:
                        # Try alternative endianness if the first one fails
                        try:
                            if endian == '>':
                                value = struct.unpack('<q', data[pos:pos+8])[0]
                            else:
                                value = struct.unpack('>q', data[pos:pos+8])[0]
                            return value, pos + 8
                        except:
                            return None, pos + 8
            elif tag_type == self.TAG_FLOAT:
                if pos + 4 <= len(data):
                    if endian == '>':
                        value = struct.unpack('>f', data[pos:pos+4])[0]
                    else:
                        value = struct.unpack('<f', data[pos:pos+4])[0]
                    return value, pos + 4
            elif tag_type == self.TAG_DOUBLE:
                if pos + 8 <= len(data):
                    if endian == '>':
                        value = struct.unpack('>d', data[pos:pos+8])[0]
                    else:
                        value = struct.unpack('<d', data[pos:pos+8])[0]
                    return value, pos + 8
            elif tag_type == self.TAG_STRING:
                if pos + 2 <= len(data):
                    if endian == '>':
                        str_length = struct.unpack('>H', data[pos:pos+2])[0]
                    else:
                        str_length = struct.unpack('<H', data[pos:pos+2])[0]
                    pos += 2
                    if pos + str_length <= len(data):
                        value = data[pos:pos+str_length].decode('utf-8', errors='replace')
                        return value, pos + str_length
            elif tag_type == self.TAG_LIST:
                if pos + 5 <= len(data):
                    list_type = data[pos]
                    pos += 1
                    if endian == '>':
                        list_length = struct.unpack('>i', data[pos:pos+4])[0]
                    else:
                        list_length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    
                    value = []
                    for _ in range(list_length):
                        item_value, new_pos = self._parse_tag_value_manual(data, pos, list_type, endian)
                        value.append(item_value)
                        pos = new_pos
                    return value, pos
            elif tag_type == self.TAG_COMPOUND:
                compound_data, new_pos = self._parse_compound_manual(data, pos, endian)
                return compound_data, new_pos
            elif tag_type == self.TAG_BYTE_ARRAY:
                if pos + 4 <= len(data):
                    if endian == '>':
                        array_length = struct.unpack('>i', data[pos:pos+4])[0]
                    else:
                        array_length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    if pos + array_length <= len(data):
                        value = list(data[pos:pos+array_length])
                        return value, pos + array_length
            elif tag_type == self.TAG_INT_ARRAY:
                if pos + 4 <= len(data):
                    if endian == '>':
                        array_length = struct.unpack('>i', data[pos:pos+4])[0]
                    else:
                        array_length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    if pos + array_length * 4 <= len(data):
                        if endian == '>':
                            value = list(struct.unpack(f'>{array_length}i', data[pos:pos+array_length*4]))
                        else:
                            value = list(struct.unpack(f'<{array_length}i', data[pos:pos+array_length*4]))
                        return value, pos + array_length * 4
            elif tag_type == self.TAG_LONG_ARRAY:
                if pos + 4 <= len(data):
                    if endian == '>':
                        array_length = struct.unpack('>i', data[pos:pos+4])[0]
                    else:
                        array_length = struct.unpack('<i', data[pos:pos+4])[0]
                    pos += 4
                    if pos + array_length * 8 <= len(data):
                        if endian == '>':
                            value = list(struct.unpack(f'>{array_length}q', data[pos:pos+array_length*8]))
                        else:
                            value = list(struct.unpack(f'<{array_length}q', data[pos:pos+array_length*8]))
                        return value, pos + array_length * 8
            
            # Silently skip unknown tag types
            return None, pos + 1
            
        except Exception as e:
            print(f"Error parsing tag value type {tag_type}: {e}")
            return None, pos + 1
    
    def _organize_compound_structures(self, flat_result):
        """Organize flat keys into proper compound structures - dynamically detect compounds"""
        try:
            organized = {}
            
            # Dynamically detect compound structures based on key patterns
            compound_groups = {}
            
            # Process each key to group related keys
            for key, value in flat_result.items():
                key_str = str(key)
                
                # Detect compound groups based on common patterns
                if key_str.endswith('Speed') or key_str in ['attackmobs', 'attackplayers', 'build', 'doorsandswitches', 'flying', 'instabuild', 'invulnerable', 'lightning', 'mayfly', 'mine', 'op', 'opencontainers', 'teleport']:
                    group_name = 'abilities'
                elif 'experiment' in key_str.lower() or key_str in ['data_driven_biomes', 'gametest', 'jigsaw_structures', 'creator_cameras', 'creator_features', 'villager_trades_rebalance']:
                    group_name = 'experiments'
                elif 'version' in key_str.lower() and isinstance(value, list):
                    # Keep version arrays as-is
                    organized[key_str] = value
                    continue
                else:
                    # Keep as top-level key
                    organized[key_str] = value
                    continue
                
                # Add to compound group
                if group_name not in compound_groups:
                    compound_groups[group_name] = {}
                compound_groups[group_name][key_str] = value
            
            # Add compound groups to organized result
            for group_name, group_data in compound_groups.items():
                if len(group_data) > 0:
                    organized[group_name] = group_data
            
            return organized
            
        except Exception as e:
            print(f"Error organizing compound structures: {e}")
            import traceback
            traceback.print_exc()
            return flat_result
    
    def _try_parse_value_at(self, data, pos):
        """Try to parse a value at a specific position"""
        try:
            if pos >= len(data):
                return None, pos
            
            # Try different value types
            value_types = [
                (1, 'b'),   # byte
                (2, 'h'),   # short
                (4, 'i'),   # int
                (8, 'q'),   # long
                (4, 'f'),   # float
            ]
            
            for size, fmt in value_types:
                if pos + size <= len(data):
                    try:
                        # Try both endianness
                        for endian in ['>', '<']:
                            try:
                                value = struct.unpack(f'{endian}{fmt}', data[pos:pos+size])[0]
                                # Validate reasonable ranges
                                if fmt in ['b', 'h', 'i'] and -1000000 <= value <= 1000000:
                                    return value, pos + size
                                elif fmt == 'q' and -1000000000000 <= value <= 1000000000000:
                                    return value, pos + size
                                elif fmt == 'f' and -1000 <= value <= 1000 and value == value:  # Not NaN
                                    return value, pos + size
                            except:
                                continue
                    except:
                        continue
            
            return None, pos + 1
            
        except Exception:
            return None, pos + 1

    # Legacy methods for backward compatibility
    def _extract_value_by_type(self, data, pos, field_type):
        """Legacy method - kept for compatibility"""
        return self._parse_tag_value(data, pos, field_type)[0]
    
    def _try_parse_compound_at(self, data, pos):
        """Legacy method - kept for compatibility"""
        return self._parse_compound(data, pos)[0]
