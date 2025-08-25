import struct
import re
import nbtlib
import gzip
import io
import os

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
        """Parse Bedrock level.dat file with manual approach and enhanced debugging"""
        try:
            print(f"Parsing {os.path.getsize(file_path)} bytes from {file_path}")
            
            # Try nbtlib parser first
            print("Trying nbtlib parser (gzipped=False)...")
            try:
                nbt_data = nbtlib.load(file_path, gzipped=False)
                print(f"nbtlib loaded data type: {type(nbt_data)}")
                print(f"nbtlib data attributes: {[attr for attr in dir(nbt_data) if not attr.startswith('_')]}")
                
                # Try direct access to nbtlib data
                print("Trying direct nbtlib access...")
                if hasattr(nbt_data, 'root_name'):
                    print(f"Root name: {nbt_data.root_name}")
                
                # Try to access data directly
                try:
                    # Convert nbtlib data to dict directly
                    result = dict(nbt_data)
                    print(f"Direct dict conversion result: {len(result)} keys")
                    if result and len(result) > 0:
                        print(f"✅ Direct nbtlib access successful: {len(result)} keys detected")
                        # 🔧 Update detected patterns from actual data
                        self.update_detected_patterns(result)
                        return result
                except Exception as direct_error:
                    print(f"Direct access failed: {direct_error}")
                
                # Convert nbtlib data to Python dict
                result = self._convert_nbtlib_data(nbt_data)
                print(f"Converted result type: {type(result)}")
                print(f"Converted result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                if result and isinstance(result, dict) and len(result) > 0:
                    print(f"✅ nbtlib (gzipped=False) successful: {len(result)} keys detected")
                    # 🔧 Update detected patterns from actual data
                    self.update_detected_patterns(result)
                    return result
                else:
                    print("⚠️  nbtlib returned empty result, trying next method")
                    
            except Exception as e:
                print(f"❌ nbtlib (gzipped=False) failed: {e}")
            
            # Try nbtlib parser with gzipped=True
            print("Trying nbtlib parser (gzipped=True)...")
            try:
                nbt_data = nbtlib.load(file_path, gzipped=True)
                result = self._convert_nbtlib_data(nbt_data)
                
                if result and isinstance(result, dict) and len(result) > 0:
                    print(f"✅ nbtlib (gzipped=True) successful: {len(result)} keys detected")
                    # 🔧 Update detected patterns from actual data
                    self.update_detected_patterns(result)
                    return result
                else:
                    print("⚠️  nbtlib (gzipped=True) returned empty result")
                    
            except Exception as e:
                print(f"❌ nbtlib (gzipped=True) failed: {e}")
            

            
            # Try manual NBT parser as fallback
            print("Trying manual NBT parser...")
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                result = self._parse_nbt_manual(data)
                if result and isinstance(result, dict) and len(result) > 0:
                    print(f"✅ Manual NBT parser successful: {len(result)} keys detected")
                    # 🔧 Update detected patterns from actual data
                    self.update_detected_patterns(result)
                    return result
                else:
                    print("⚠️  Manual NBT parser returned empty result")
            except Exception as e:
                print(f"❌ Manual NBT parser failed: {e}")
            
            print("❌ All parsers failed to return valid data")
            return {}
            
        except Exception as e:
            print(f"❌ Manual parsing failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    

    
    def _convert_nbtlib_data(self, nbt_data):
        """Convert nbtlib data to Python dict with enhanced debugging"""
        try:
            print(f"Converting nbtlib data: {type(nbt_data)}")
            
            # Check if nbt_data has root data
            if hasattr(nbt_data, 'root'):
                print(f"Data has root attribute, converting root")
                result = self._convert_nbtlib_value(nbt_data.root)
                print(f"Converted root result type: {type(result)}")
                print(f"Converted root result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return result
            elif hasattr(nbt_data, 'items'):
                print(f"Data has items method, converting directly")
                items_list = list(nbt_data.items())
                print(f"Items list length: {len(items_list)}")
                if len(items_list) == 0:
                    # Try to access root if items is empty
                    if hasattr(nbt_data, 'root'):
                        print(f"Items empty, trying root attribute")
                        result = self._convert_nbtlib_value(nbt_data.root)
                        print(f"Converted root result type: {type(result)}")
                        print(f"Converted root result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                        return result
                    else:
                        print(f"No root attribute found, returning empty dict")
                        return {}
                result = self._convert_nbtlib_value(nbt_data)
                print(f"Converted items result type: {type(result)}")
                print(f"Converted items result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return result
            else:
                print(f"No root or items found, trying direct conversion")
                result = self._convert_nbtlib_value(nbt_data)
                print(f"Converted direct result type: {type(result)}")
                print(f"Converted direct result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return result
        except Exception as e:
            print(f"Error converting nbtlib: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _convert_nbtlib_value(self, value):
        """Convert individual nbtlib value with proper type preservation"""
        try:
            print(f"Converting value: {type(value)} - {value}")
            
            # Handle NBT tag objects (nbtlib.tag.*)
            if hasattr(value, 'tag_id'):
                # Check if this is a compound tag (dictionary-like)
                if hasattr(value, 'items') and callable(getattr(value, 'items')):
                    print(f"Converting NBT compound tag with {len(list(value.items()))} items")
                    result = {}
                    for k, v in value.items():
                        print(f"Converting compound key: {k} -> {type(v)}")
                        result[str(k)] = self._convert_nbtlib_value(v)
                    return result
                # Check if this is a list tag
                elif isinstance(value, (list, tuple)) or (hasattr(value, '__iter__') and hasattr(value, '__len__')):
                    print(f"Converting NBT list tag with {len(value)} items")
                    # Check if this is actually a string that was converted to list of characters
                    if len(value) > 0 and all(isinstance(item, str) and len(item) == 1 for item in value):
                        # This is likely a string converted to list of characters
                        reconstructed_string = ''.join(value)
                        print(f"Reconstructed string from NBT list: {reconstructed_string}")
                        return reconstructed_string
                    elif len(value) == 0:
                        # Empty list - could be empty string
                        print("Empty NBT list detected, returning empty string")
                        return ""
                    return [self._convert_nbtlib_value(v) for v in value]
                # Extract actual value from primitive NBT tag
                elif hasattr(value, 'value'):
                    actual_value = value.value
                    print(f"Extracted NBT tag value: {actual_value}")
                    return actual_value
                elif hasattr(value, 'py_data'):
                    actual_value = value.py_data
                    print(f"Extracted NBT tag py_data: {actual_value}")
                    return actual_value
                elif hasattr(value, 'py_int'):
                    actual_value = value.py_int
                    print(f"Extracted NBT tag py_int: {actual_value}")
                    return actual_value
                elif hasattr(value, 'py_float'):
                    actual_value = value.py_float
                    print(f"Extracted NBT tag py_float: {actual_value}")
                    return actual_value
                elif hasattr(value, 'py_str'):
                    actual_value = value.py_str
                    print(f"Extracted NBT tag py_str: {actual_value}")
                    return actual_value
                elif hasattr(value, 'py_bool'):
                    actual_value = value.py_bool
                    print(f"Extracted NBT tag py_bool: {actual_value}")
                    return actual_value
                else:
                    # Fallback: try to convert to string and extract value
                    str_value = str(value)
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
            
            # Handle dict-like objects
            if hasattr(value, 'items') and callable(getattr(value, 'items')):
                print(f"Converting dict-like object with {len(list(value.items()))} items")
                result = {}
                for k, v in value.items():
                    print(f"Converting key: {k} -> {type(v)}")
                    result[str(k)] = self._convert_nbtlib_value(v)
                return result
            # Handle strings FIRST - return as-is, don't convert to list!
            elif isinstance(value, str):
                print(f"Converting string: {value}")
                return value
            # Handle lists and tuples - but NOT strings!
            elif isinstance(value, (list, tuple)):
                print(f"Converting list/tuple with {len(value)} items")
                # Check if this is actually a string that was converted to list of characters
                if len(value) > 0 and all(isinstance(item, str) and len(item) == 1 for item in value):
                    # This is likely a string converted to list of characters
                    reconstructed_string = ''.join(value)
                    print(f"Reconstructed string from list: {reconstructed_string}")
                    return reconstructed_string
                elif len(value) == 0:
                    # Empty list - could be empty string
                    print("Empty list detected, returning empty string")
                    return ""
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
    
    def save_nbt_data_manual_with_type_info(self, data, file_path, type_info=None, debug_type_detection=False):
        """Save NBT data using manual writer with preserved type information"""
        try:
            print(f"💾 Manual saving to: {file_path} with type preservation")
            
            # Enable debug mode if requested
            self._debug_type_detection = debug_type_detection
            
            # Store type info for use in writing
            self._preserved_type_info = type_info or {}
            
            # Create binary data with type preservation
            binary_data = self._write_nbt_compound_with_type_preservation(data)
            
            # Write to file
            with open(file_path, 'wb') as f:
                f.write(binary_data)
            
            print(f"✅ Manual save successful: {len(binary_data)} bytes written")
            return True
            
        except Exception as e:
            print(f"❌ Manual save failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_nbt_data_manual(self, data, file_path, debug_type_detection=False):
        """Save NBT data using manual writer with automatic type detection"""
        try:
            print(f"💾 Manual saving to: {file_path}")
            
            # Enable debug mode if requested
            self._debug_type_detection = debug_type_detection
            
            # Create binary data with automatic type detection
            binary_data = self._write_nbt_compound_with_types(data)
            
            # Write to file
            with open(file_path, 'wb') as f:
                f.write(binary_data)
            
            print(f"✅ Manual save successful: {len(binary_data)} bytes written")
            return True
            
        except Exception as e:
            print(f"❌ Manual save failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _write_nbt_compound_with_type_preservation(self, data):
        """Write NBT compound to binary data with type preservation"""
        try:
            # Start with compound tag
            result = bytearray()
            result.append(self.TAG_COMPOUND)  # Compound tag
            
            # Write empty name (root compound)
            result.extend(struct.pack('>H', 0))  # Name length = 0
            
            # Write compound contents with type preservation
            compound_data = self._write_compound_contents_with_type_preservation(data)
            result.extend(compound_data)
            
            # Add end tag
            result.append(self.TAG_END)
            
            return bytes(result)
            
        except Exception as e:
            print(f"❌ Error writing NBT compound: {e}")
            raise
    
    def _write_nbt_compound_with_types(self, data):
        """Write NBT compound to binary data with proper type detection"""
        try:
            # Start with compound tag
            result = bytearray()
            result.append(self.TAG_COMPOUND)  # Compound tag
            
            # Write empty name (root compound)
            result.extend(struct.pack('>H', 0))  # Name length = 0
            
            # Write compound contents with proper type detection
            compound_data = self._write_compound_contents_with_types(data)
            result.extend(compound_data)
            
            # Add end tag
            result.append(self.TAG_END)
            
            return bytes(result)
            
        except Exception as e:
            print(f"❌ Error writing NBT compound: {e}")
            raise
    
    def _write_nbt_compound(self, data):
        """Write NBT compound to binary data"""
        try:
            # Start with compound tag
            result = bytearray()
            result.append(self.TAG_COMPOUND)  # Compound tag
            
            # Write empty name (root compound)
            result.extend(struct.pack('>H', 0))  # Name length = 0
            
            # Write compound contents
            compound_data = self._write_compound_contents(data)
            result.extend(compound_data)
            
            # Add end tag
            result.append(self.TAG_END)
            
            return bytes(result)
            
        except Exception as e:
            print(f"❌ Error writing NBT compound: {e}")
            raise
    
    def _write_compound_contents_with_type_preservation(self, data):
        """Write compound contents with type preservation"""
        result = bytearray()
        
        for key, value in data.items():
            try:
                # Use preserved type info if available
                tag_type = self._get_tag_type_with_preservation(key, value)
                
                # Debug info for type detection
                if hasattr(self, '_debug_type_detection') and self._debug_type_detection:
                    print(f"🔧 Type-preserved '{key}' ({value}) as type {tag_type}")
                
                result.append(tag_type)
                
                # Write key name
                key_bytes = key.encode('utf-8')
                result.extend(struct.pack('>H', len(key_bytes)))
                result.extend(key_bytes)
                
                # Write value
                value_data = self._write_tag_value_with_preservation(value, tag_type, key)
                result.extend(value_data)
                
            except Exception as e:
                print(f"❌ Error writing key '{key}' with value {value}: {e}")
                print(f"❌ Key type: {type(key)}, Value type: {type(value)}")
                raise
        
        return bytes(result)
    
    def _write_compound_contents_with_types(self, data):
        """Write compound contents with automatic type detection"""
        result = bytearray()
        
        for key, value in data.items():
            try:
                # Auto-detect tag type
                tag_type = self._get_tag_type_improved(key, value)
                
                # Debug info for type detection
                if hasattr(self, '_debug_type_detection') and self._debug_type_detection:
                    print(f"🔍 Auto-detected '{key}' ({value}) as type {tag_type}")
                
                result.append(tag_type)
                
                # Write key name
                key_bytes = key.encode('utf-8')
                result.extend(struct.pack('>H', len(key_bytes)))
                result.extend(key_bytes)
                
                # Write value
                value_data = self._write_tag_value(value, tag_type)
                result.extend(value_data)
                
            except Exception as e:
                print(f"❌ Error writing key '{key}' with value {value}: {e}")
                print(f"❌ Key type: {type(key)}, Value type: {type(value)}")
                raise
        
        return bytes(result)
    
    def _write_compound_contents(self, data):
        """Write compound contents"""
        result = bytearray()
        
        for key, value in data.items():
            # Write tag type
            tag_type = self._get_tag_type(value)
            result.append(tag_type)
            
            # Write key name
            key_bytes = key.encode('utf-8')
            result.extend(struct.pack('>H', len(key_bytes)))
            result.extend(key_bytes)
            
            # Write value
            value_data = self._write_tag_value(value, tag_type)
            result.extend(value_data)
        
        return bytes(result)
    
    def _get_tag_type_improved(self, key, value):
        """Get NBT tag type with automatic detection based on value and key patterns"""
        
        # Check for specific key overrides first
        specific_type = self._get_specific_key_type(key)
        if specific_type is not None:
            return specific_type
        
        # Auto-detect boolean based on value and key patterns
        if self._is_boolean_value(key, value):
            return self.TAG_BYTE
        
        # Auto-detect string based on value type
        if isinstance(value, str):
            return self.TAG_STRING
        
        # Auto-detect float based on value type and key patterns
        if self._is_float_value(key, value):
            return self.TAG_FLOAT
        
        # Auto-detect integer/long based on value type and range
        if isinstance(value, int):
            if abs(value) > 2147483647:
                return self.TAG_LONG
            else:
                return self.TAG_INT
        
        # Auto-detect other types
        if isinstance(value, bool):
            return self.TAG_BYTE
        elif isinstance(value, list):
            return self.TAG_LIST
        elif isinstance(value, dict):
            return self.TAG_COMPOUND
        else:
            return self.TAG_STRING  # Default to string
    
    def _is_boolean_value(self, key, value):
        """Auto-detect if value should be boolean based on patterns"""
        # Check if value is 0 or 1 (common boolean values)
        if isinstance(value, int) and value in [0, 1]:
            # Check key patterns that suggest boolean
            key_lower = key.lower()
            
            # Exclude keys that should NOT be boolean
            non_boolean_exclusions = [
                'worldversion', 'editorworldtype', 'eduoffer', 'permissionlevel', 
                'playerpermissionlevel', 'randomtickspeed', 'lastplayed', 'currenttick',
                'lanbroadcastintent', 'randomseed', 'time'
            ]
            
            # Check exclusions first
            for exclusion in non_boolean_exclusions:
                if exclusion in key_lower:
                    return False
            
            boolean_patterns = [
                'enabled', 'disabled', 'on', 'off', 'true', 'false',
                'allow', 'deny', 'show', 'hide', 'enable', 'disable',
                'active', 'inactive', 'visible', 'invisible',
                'do', 'dont', 'can', 'cannot', 'has', 'is', 'are'
            ]
            
            # Check if key contains boolean patterns
            for pattern in boolean_patterns:
                if pattern in key_lower:
                    return True
            
            # Check if key starts with common boolean prefixes
            boolean_prefixes = ['is', 'has', 'can', 'do', 'show', 'allow']
            for prefix in boolean_prefixes:
                if key_lower.startswith(prefix):
                    return True
        
        return False
    
    def _get_tag_type_with_preservation(self, key, value):
        """Get NBT tag type with type preservation and nested key support"""
        # Check if we have preserved type info for this key
        if hasattr(self, '_preserved_type_info') and key in self._preserved_type_info:
            type_info = self._preserved_type_info[key]
            original_type = type_info['original_type']
            is_nested = type_info.get('is_nested', False)
            is_experiment = type_info.get('is_experiment', False)
            is_initial_load = type_info.get('is_initial_load', True)  # Default to True for safety
            was_edited = type_info.get('was_edited', False)
            
            print(f"🔧 Using preserved type for '{key}': {original_type} (nested: {is_nested}, experiment: {is_experiment}, initial_load: {is_initial_load}, edited: {was_edited})")
            
            # For initial load keys (not edited), ALWAYS preserve original type
            if is_initial_load and not was_edited:
                print(f"🔒 Preserving original type for unedited key '{key}': {original_type}")
                if original_type == bool:
                    return self.TAG_BYTE
                elif original_type == int:
                    if isinstance(value, int) and abs(value) > 2147483647:
                        return self.TAG_LONG
                    else:
                        return self.TAG_INT
                elif original_type == float:
                    return self.TAG_FLOAT
                elif original_type == str:
                    return self.TAG_STRING
                elif original_type == list:
                    return self.TAG_LIST
                elif original_type == dict:
                    return self.TAG_COMPOUND
            
            # For edited keys, use type preservation with minimal auto-detection
            if original_type == bool:
                return self.TAG_BYTE
            elif original_type == int:
                # Preserve original int type without auto-detection override
                # Only use auto-detection if the value was actually changed
                if isinstance(value, int) and abs(value) > 2147483647:
                    return self.TAG_LONG
                else:
                    return self.TAG_INT
            elif original_type == float:
                return self.TAG_FLOAT
            elif original_type == str:
                return self.TAG_STRING
            elif original_type == list:
                return self.TAG_LIST
            elif original_type == dict:
                return self.TAG_COMPOUND
        
        # Check for nested keys (for experiments dictionary)
        if hasattr(self, '_preserved_type_info'):
            for stored_key, type_info in self._preserved_type_info.items():
                if stored_key.startswith(key + '.') or key.startswith(stored_key + '.'):
                    original_type = type_info['original_type']
                    is_experiment = type_info.get('is_experiment', False)
                    is_initial_load = type_info.get('is_initial_load', True)
                    was_edited = type_info.get('was_edited', False)
                    
                    print(f"🔧 Using nested preserved type for '{key}': {original_type} (experiment: {is_experiment}, initial_load: {is_initial_load}, edited: {was_edited})")
                    
                    # For initial load keys, preserve original type
                    if is_initial_load and not was_edited:
                        print(f"🔒 Preserving original type for unedited nested key '{key}': {original_type}")
                        if original_type == bool:
                            return self.TAG_BYTE
                        elif original_type == int:
                            if isinstance(value, int) and abs(value) > 2147483647:
                                return self.TAG_LONG
                            else:
                                return self.TAG_INT
                        elif original_type == float:
                            return self.TAG_FLOAT
                        elif original_type == str:
                            return self.TAG_STRING
                        elif original_type == list:
                            return self.TAG_LIST
                        elif original_type == dict:
                            return self.TAG_COMPOUND
                    
                    # For edited keys, use type preservation
                    if original_type == bool:
                        return self.TAG_BYTE
                    elif original_type == int:
                        # Preserve original int type without auto-detection
                        if isinstance(value, int) and abs(value) > 2147483647:
                            return self.TAG_LONG
                        else:
                            return self.TAG_INT
                    elif original_type == float:
                        return self.TAG_FLOAT
                    elif original_type == str:
                        return self.TAG_STRING
                    elif original_type == list:
                        return self.TAG_LIST
                    elif original_type == dict:
                        return self.TAG_COMPOUND
        
        # For keys without preserved type info, use conservative auto detection
        # that doesn't change existing types unnecessarily
        return self._get_tag_type_conservative(key, value)
    
    def _get_tag_type_conservative(self, key, value):
        """Conservative type detection that preserves existing types when possible"""
        # Check for specific key overrides first
        specific_type = self._get_specific_key_type(key)
        if specific_type is not None:
            return specific_type
        
        # If value is already a specific type, preserve it
        if isinstance(value, bool):
            return self.TAG_BYTE
        elif isinstance(value, int):
            # Check if this should be a boolean based on value and key patterns
            if value in [0, 1] and self._is_boolean_key_pattern(key):
                return self.TAG_BYTE
            elif abs(value) > 2147483647:
                return self.TAG_LONG
            else:
                return self.TAG_INT
        elif isinstance(value, float):
            return self.TAG_FLOAT
        elif isinstance(value, str):
            return self.TAG_STRING
        elif isinstance(value, list):
            return self.TAG_LIST
        elif isinstance(value, dict):
            return self.TAG_COMPOUND
        else:
            return self.TAG_STRING  # Default to string
    
    def _get_specific_key_type(self, key):
        """Get specific tag type for known keys that have fixed types"""
        key_lower = key.lower()
        
        # Boolean keys (TAG_BYTE)
        boolean_keys = {
            'forcegametype', 'playerhasdied', 'locatorbar'
        }
        
        # Integer keys (TAG_INT)
        integer_keys = {
            'worldversion', 'editorworldtype', 'eduoffer', 'permissionlevel', 
            'playerpermissionlevel', 'randomtickspeed', 'lanbroadcastintent'
        }
        
        # Long keys (TAG_LONG)
        long_keys = {
            'lastplayed', 'currenttick', 'randomseed', 'time'
        }
        
        # Check for exact matches
        if key_lower in boolean_keys:
            return self.TAG_BYTE
        elif key_lower in integer_keys:
            return self.TAG_INT
        elif key_lower in long_keys:
            return self.TAG_LONG
        
        # Check for partial matches (case-insensitive)
        for boolean_key in boolean_keys:
            if boolean_key in key_lower or key_lower in boolean_key:
                return self.TAG_BYTE
        
        for integer_key in integer_keys:
            if integer_key in key_lower or key_lower in integer_key:
                return self.TAG_INT
        
        for long_key in long_keys:
            if long_key in key_lower or key_lower in long_key:
                return self.TAG_LONG
        
        return None
    
    def _detect_boolean_patterns_from_data(self, data):
        """Automatically detect boolean patterns from actual NBT data structure"""
        boolean_patterns = set()
        non_boolean_patterns = set()
        
        def analyze_value(key, value):
            """Analyze a single key-value pair to detect boolean patterns"""
            key_lower = key.lower()
            
            # Check if value is boolean (0b/1b) or native bool
            is_boolean_value = False
            if isinstance(value, bool):
                is_boolean_value = True
            elif isinstance(value, int) and value in [0, 1]:
                # Could be boolean, need to check context
                is_boolean_value = True
            
            if is_boolean_value:
                # Extract pattern from key name
                words = key_lower.replace('_', ' ').replace('-', ' ').split()
                for word in words:
                    if len(word) > 2:  # Only consider words with more than 2 characters
                        boolean_patterns.add(word)
            else:
                # This is NOT a boolean value, so these patterns should NOT be treated as boolean
                words = key_lower.replace('_', ' ').replace('-', ' ').split()
                for word in words:
                    if len(word) > 2:
                        non_boolean_patterns.add(word)
        
        def traverse_data(data, parent_key=""):
            """Recursively traverse data structure to analyze all key-value pairs"""
            if isinstance(data, dict):
                for key, value in data.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key
                    analyze_value(key, value)
                    
                    # Recursively analyze nested structures
                    if isinstance(value, (dict, list)):
                        traverse_data(value, full_key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    list_key = f"{parent_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        traverse_data(item, list_key)
        
        # Analyze the provided data
        traverse_data(data)
        
        # Remove patterns that appear in both boolean and non-boolean contexts
        conflicting_patterns = boolean_patterns.intersection(non_boolean_patterns)
        boolean_patterns = boolean_patterns - conflicting_patterns
        
        print(f"🔍 Auto-detected {len(boolean_patterns)} boolean patterns: {sorted(list(boolean_patterns))}")
        print(f"🔍 Excluded {len(conflicting_patterns)} conflicting patterns: {sorted(list(conflicting_patterns))}")
        return list(boolean_patterns)
    
    def _detect_float_patterns_from_data(self, data):
        """Automatically detect float patterns from actual NBT data structure"""
        float_patterns = set()
        
        def analyze_value(key, value):
            """Analyze a single key-value pair to detect float patterns"""
            # Check if value is float
            if isinstance(value, float):
                key_lower = key.lower()
                
                # Extract individual words from key for pattern detection
                words = key_lower.replace('_', ' ').replace('-', ' ').split()
                for word in words:
                    if len(word) > 2:  # Only consider words with more than 2 characters
                        float_patterns.add(word)
        
        def traverse_data(data, parent_key=""):
            """Recursively traverse data structure to analyze all key-value pairs"""
            if isinstance(data, dict):
                for key, value in data.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key
                    analyze_value(key, value)
                    
                    # Recursively analyze nested structures
                    if isinstance(value, (dict, list)):
                        traverse_data(value, full_key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    list_key = f"{parent_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        traverse_data(item, list_key)
        
        # Analyze the provided data
        traverse_data(data)
        
        print(f"🔍 Auto-detected {len(float_patterns)} float patterns: {sorted(list(float_patterns))}")
        return list(float_patterns)
    
    def _detect_version_patterns_from_data(self, data):
        """Automatically detect version-related patterns from actual NBT data structure"""
        version_patterns = set()
        
        def analyze_value(key, value):
            """Analyze a single key-value pair to detect version patterns"""
            key_lower = key.lower()
            
            # Check if key contains version-related words
            version_words = ['version', 'ver', 'v_', 'v-', 'build', 'release', 'patch']
            for word in version_words:
                if word in key_lower:
                    version_patterns.add(word)
            
            # Check if value is a list that might be a version array
            if isinstance(value, list) and len(value) > 0:
                # If all elements are integers, it might be a version array
                if all(isinstance(item, int) for item in value):
                    version_patterns.add('version_array')
        
        def traverse_data(data, parent_key=""):
            """Recursively traverse data structure to analyze all key-value pairs"""
            if isinstance(data, dict):
                for key, value in data.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key
                    analyze_value(key, value)
                    
                    # Recursively analyze nested structures
                    if isinstance(value, (dict, list)):
                        traverse_data(value, full_key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    list_key = f"{parent_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        traverse_data(item, list_key)
        
        # Analyze the provided data
        traverse_data(data)
        
        print(f"🔍 Auto-detected {len(version_patterns)} version patterns: {sorted(list(version_patterns))}")
        return list(version_patterns)
    
    def _detect_experiment_keys_from_data(self, data):
        """Automatically detect experiment keys from actual NBT data structure"""
        experiment_keys = set()
        
        def find_experiments_section(data, parent_key=""):
            """Find the experiments section and extract all keys"""
            if isinstance(data, dict):
                for key, value in data.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key
                    
                    # Check if this is the experiments section
                    if key.lower() == 'experiments' and isinstance(value, dict):
                        print(f"🔍 Found experiments section: {full_key}")
                        # Extract all keys from experiments section
                        for exp_key in value.keys():
                            experiment_keys.add(exp_key)
                            print(f"🔍 Detected experiment key: {exp_key}")
                    
                    # Recursively search nested structures
                    if isinstance(value, (dict, list)):
                        find_experiments_section(value, full_key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    list_key = f"{parent_key}[{i}]"
                    if isinstance(item, (dict, list)):
                        find_experiments_section(item, list_key)
        
        # Search for experiments section
        find_experiments_section(data)
        
        print(f"🔍 Auto-detected {len(experiment_keys)} experiment keys: {sorted(list(experiment_keys))}")
        return list(experiment_keys)
    
    def _is_boolean_key_pattern(self, key):
        """Check if a key suggests a boolean value using auto-detected patterns"""
        if not hasattr(self, '_detected_boolean_patterns'):
            # Initialize with empty list if not yet detected
            self._detected_boolean_patterns = []
        
        key_lower = key.lower()
        
        # 🔧 Specific exclusions for keys that should NOT be boolean
        non_boolean_exclusions = [
            'gametype', 'generator', 'randomseed', 'lightninglevel', 'rainlevel',
            'difficulty', 'lastplayed', 'storageversion', 'worldversion', 'networkversion',
            'platform', 'netherscale', 'time', 'currenttick', 'lightningtime', 'raintime',
            'limitedworlddepth', 'limitedworldwidth', 'maxcommandchainlength', 'permissionslevel',
            'playerpermissionslevel', 'playerssleepingpercentage', 'randomtickspeed',
            'serverchunktickrange', 'spawnradius', 'worldstartcount', 'functioncommandlimit',
            'editorworldtype', 'eduoffer', 'limitedworldoriginx', 'limitedworldoriginy',
            'limitedworldoriginz', 'spawnx', 'spawny', 'spawnz', 'platformbroadcastintent',
            'xblbroadcastintent', 'daylightcycle', 'permissionlevel', 'playerpermissionlevel',
            'lanbroadcastintent'
        ]
        
        # Check exclusions first
        for exclusion in non_boolean_exclusions:
            if exclusion in key_lower:
                return False
        
        # Check if key contains detected boolean patterns
        for pattern in self._detected_boolean_patterns:
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
    
    def _is_float_key_pattern(self, key):
        """Check if a key suggests a float value using auto-detected patterns"""
        if not hasattr(self, '_detected_float_patterns'):
            # Initialize with empty list if not yet detected
            self._detected_float_patterns = []
        
        key_lower = key.lower()
        
        # Check if key contains detected float patterns
        for pattern in self._detected_float_patterns:
            if pattern in key_lower:
                return True
        
        return False
    
    def _is_version_key_pattern(self, key):
        """Check if a key suggests a version value using auto-detected patterns"""
        if not hasattr(self, '_detected_version_patterns'):
            # Initialize with empty list if not yet detected
            self._detected_version_patterns = []
        
        key_lower = key.lower()
        
        # Check if key contains detected version patterns
        for pattern in self._detected_version_patterns:
            if pattern in key_lower:
                return True
        
        return False
    
    def _is_experiment_key(self, key):
        """Check if a key is an experiment key using auto-detected patterns"""
        if not hasattr(self, '_detected_experiment_keys'):
            # Initialize with common experiment keys if not yet detected
            self._detected_experiment_keys = []
        
        # Check if key is in detected experiment keys
        is_experiment = key in self._detected_experiment_keys
        
        # Also check if key contains 'experiment' in the name
        if not is_experiment and 'experiment' in key.lower():
            is_experiment = True
        
        return is_experiment
    
    def update_detected_patterns(self, data):
        """Update detected patterns from actual data structure"""
        print("🔍 Updating detected patterns from data structure...")
        
        # Detect boolean patterns
        self._detected_boolean_patterns = self._detect_boolean_patterns_from_data(data)
        
        # Detect float patterns
        self._detected_float_patterns = self._detect_float_patterns_from_data(data)
        
        # Detect version patterns
        self._detected_version_patterns = self._detect_version_patterns_from_data(data)
        
        # Detect experiment keys
        self._detected_experiment_keys = self._detect_experiment_keys_from_data(data)
        
        print(f"✅ Updated patterns: {len(self._detected_boolean_patterns)} boolean, {len(self._detected_float_patterns)} float, {len(self._detected_version_patterns)} version, {len(self._detected_experiment_keys)} experiment keys")
        
        # Debug: show detected experiment keys
        if self._detected_experiment_keys:
            print(f"🔍 Detected experiment keys: {self._detected_experiment_keys}")
    
    def _is_float_value(self, key, value):
        """Auto-detect if value should be float based on patterns"""
        # If value is already float, use it
        if isinstance(value, float):
            return True
        
        # If value is int, check if it should be float based on key patterns
        if isinstance(value, int):
            return self._is_float_key_pattern(key)
        
        return False
    
    def _get_tag_type(self, value):
        """Get NBT tag type for value"""
        if isinstance(value, bool):
            return self.TAG_BYTE
        elif isinstance(value, int):
            # Check if it's actually a boolean (0 or 1)
            if value in [0, 1]:
                return self.TAG_BYTE
            elif abs(value) > 2147483647:
                return self.TAG_LONG
            else:
                return self.TAG_INT
        elif isinstance(value, float):
            return self.TAG_FLOAT
        elif isinstance(value, str):
            return self.TAG_STRING
        elif isinstance(value, list):
            return self.TAG_LIST
        elif isinstance(value, dict):
            return self.TAG_COMPOUND
        else:
            return self.TAG_STRING  # Default to string
    
    def _write_tag_value(self, value, tag_type):
        """Write tag value based on type"""
        result = bytearray()
        
        try:
            if tag_type == self.TAG_BYTE:
                result.extend(struct.pack('>b', int(value)))
            elif tag_type == self.TAG_SHORT:
                result.extend(struct.pack('>h', int(value)))
            elif tag_type == self.TAG_INT:
                # Check if value is within int range
                int_value = int(value)
                if abs(int_value) > 2147483647:
                    # Value is too large for int, use long instead
                    print(f"⚠️ Value {int_value} too large for int, using long")
                    result.extend(struct.pack('>q', int_value))
                else:
                    result.extend(struct.pack('>i', int_value))
            elif tag_type == self.TAG_LONG:
                result.extend(struct.pack('>q', int(value)))
            elif tag_type == self.TAG_FLOAT:
                result.extend(struct.pack('>f', float(value)))
            elif tag_type == self.TAG_DOUBLE:
                result.extend(struct.pack('>d', float(value)))
            elif tag_type == self.TAG_STRING:
                value_bytes = str(value).encode('utf-8')
                result.extend(struct.pack('>H', len(value_bytes)))
                result.extend(value_bytes)
            elif tag_type == self.TAG_LIST:
                result.extend(self._write_list(value))
            elif tag_type == self.TAG_COMPOUND:
                result.extend(self._write_compound_contents(value))
                result.append(self.TAG_END)
            elif tag_type == self.TAG_BYTE_ARRAY:
                if isinstance(value, list):
                    result.extend(struct.pack('>i', len(value)))
                    for item in value:
                        result.extend(struct.pack('>b', int(item)))
                else:
                    result.extend(struct.pack('>i', 0))
            elif tag_type == self.TAG_INT_ARRAY:
                if isinstance(value, list):
                    result.extend(struct.pack('>i', len(value)))
                    for item in value:
                        result.extend(struct.pack('>i', int(item)))
                else:
                    result.extend(struct.pack('>i', 0))
            elif tag_type == self.TAG_LONG_ARRAY:
                if isinstance(value, list):
                    result.extend(struct.pack('>i', len(value)))
                    for item in value:
                        result.extend(struct.pack('>q', int(item)))
                else:
                    result.extend(struct.pack('>i', 0))
            else:
                # Default to string
                value_bytes = str(value).encode('utf-8')
                result.extend(struct.pack('>H', len(value_bytes)))
                result.extend(value_bytes)
            
            return bytes(result)
            
        except Exception as e:
            print(f"❌ Error writing tag value {value} (type {tag_type}): {e}")
            print(f"❌ Value type: {type(value)}")
            raise
    
    def _write_list(self, value_list):
        """Write list tag"""
        result = bytearray()
        
        if not value_list:
            # Empty list
            result.append(self.TAG_END)  # List type
            result.extend(struct.pack('>i', 0))  # List length
        else:
            # Get type from first element with type preservation
            if hasattr(self, '_preserved_type_info'):
                # Try to find type info for list elements
                list_type = None
                for key, type_info in self._preserved_type_info.items():
                    if key.endswith('[0]') or key.endswith('[1]'):  # List element keys
                        list_type = self._get_tag_type_with_preservation(key, value_list[0])
                        break
                
                if list_type is None:
                    # Fallback to conservative type detection
                    list_type = self._get_tag_type_conservative('list_element', value_list[0])
            else:
                # No type info available, use conservative detection
                list_type = self._get_tag_type_conservative('list_element', value_list[0])
            
            result.append(list_type)
            result.extend(struct.pack('>i', len(value_list)))
            
            # Write list items
            for i, item in enumerate(value_list):
                item_data = self._write_tag_value(item, list_type)
                result.extend(item_data)
        
        return bytes(result)
    
    def _write_tag_value_with_preservation(self, value, tag_type, parent_key=""):
        """Write tag value with type preservation for nested structures"""
        result = bytearray()
        
        try:
            if tag_type == self.TAG_BYTE:
                result.extend(struct.pack('>b', int(value)))
            elif tag_type == self.TAG_SHORT:
                result.extend(struct.pack('>h', int(value)))
            elif tag_type == self.TAG_INT:
                # Check if value is within int range
                int_value = int(value)
                if abs(int_value) > 2147483647:
                    # Value is too large for int, use long instead
                    print(f"⚠️ Value {int_value} too large for int, using long")
                    result.extend(struct.pack('>q', int_value))
                else:
                    result.extend(struct.pack('>i', int_value))
            elif tag_type == self.TAG_LONG:
                result.extend(struct.pack('>q', int(value)))
            elif tag_type == self.TAG_FLOAT:
                result.extend(struct.pack('>f', float(value)))
            elif tag_type == self.TAG_DOUBLE:
                result.extend(struct.pack('>d', float(value)))
            elif tag_type == self.TAG_STRING:
                value_bytes = str(value).encode('utf-8')
                result.extend(struct.pack('>H', len(value_bytes)))
                result.extend(value_bytes)
            elif tag_type == self.TAG_LIST:
                result.extend(self._write_list_with_preservation(value, parent_key))
            elif tag_type == self.TAG_COMPOUND:
                result.extend(self._write_compound_contents_with_type_preservation(value))
                result.append(self.TAG_END)
            elif tag_type == self.TAG_BYTE_ARRAY:
                if isinstance(value, list):
                    result.extend(struct.pack('>i', len(value)))
                    for item in value:
                        result.extend(struct.pack('>b', int(item)))
                else:
                    result.extend(struct.pack('>i', 0))
            elif tag_type == self.TAG_INT_ARRAY:
                if isinstance(value, list):
                    result.extend(struct.pack('>i', len(value)))
                    for item in value:
                        result.extend(struct.pack('>i', int(item)))
                else:
                    result.extend(struct.pack('>i', 0))
            elif tag_type == self.TAG_LONG_ARRAY:
                if isinstance(value, list):
                    result.extend(struct.pack('>i', len(value)))
                    for item in value:
                        result.extend(struct.pack('>q', int(item)))
                else:
                    result.extend(struct.pack('>i', 0))
            else:
                # Default to string
                value_bytes = str(value).encode('utf-8')
                result.extend(struct.pack('>H', len(value_bytes)))
                result.extend(value_bytes)
            
            return bytes(result)
            
        except Exception as e:
            print(f"❌ Error writing tag value {value} (type {tag_type}): {e}")
            print(f"❌ Value type: {type(value)}")
            raise
    
    def _write_list_with_preservation(self, value_list, parent_key=""):
        """Write list tag with type preservation for list elements"""
        result = bytearray()
        
        if not value_list:
            # Empty list
            result.append(self.TAG_END)  # List type
            result.extend(struct.pack('>i', 0))  # List length
        else:
            # Get type from first element with type preservation
            if hasattr(self, '_preserved_type_info'):
                # Try to find type info for list elements
                list_type = None
                
                # Check for list element keys in type info
                for key, type_info in self._preserved_type_info.items():
                    if key.startswith('[') and key.endswith(']'):
                        # This is a list element key
                        list_type = self._get_tag_type_with_preservation(key, value_list[0])
                        break
                
                if list_type is None:
                    # Fallback to conservative type detection
                    list_type = self._get_tag_type_conservative('list_element', value_list[0])
            else:
                # No type info available, use conservative detection
                list_type = self._get_tag_type_conservative('list_element', value_list[0])
            
            result.append(list_type)
            result.extend(struct.pack('>i', len(value_list)))
            
            # Write list items
            for i, item in enumerate(value_list):
                item_data = self._write_tag_value_with_preservation(item, list_type, f"{parent_key}[{i}]")
                result.extend(item_data)
        
        return bytes(result)
    



