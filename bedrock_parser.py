import struct
import re
import nbtlib

# Import AMULET_AVAILABLE from package_manager
try:
    from package_manager import AMULET_AVAILABLE, amulet_load
except ImportError:
    AMULET_AVAILABLE = False
    amulet_load = None

class BedrockParser:
    """Advanced parser untuk Bedrock level.dat dengan dynamic key detection"""
    
    def parse_bedrock_level_dat_manual(self, file_path):
        """
        Dynamic parser untuk Bedrock level.dat yang bisa mendeteksi semua key
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            print(f"Using dynamic parsing approach for {len(data)} bytes")
            
            # Coba berbagai metode parsing untuk mendapatkan semua key
            result = {}
            
            # Method 1: Coba dengan amulet-nbt (lebih baik untuk Bedrock)
            if AMULET_AVAILABLE and amulet_load:
                try:
                    print("Trying amulet-nbt parser...")
                    nbt_data = amulet_load(file_path)
                    result = self._convert_amulet_nbt_to_dict(nbt_data)
                    if result and len(result) > 0:
                        print(f"✅ amulet-nbt berhasil: {len(result)} keys detected")
                        return result
                except Exception as e:
                    print(f"❌ amulet-nbt gagal: {e}")
            
            # Method 2: Coba dengan nbtlib (tanpa gzip)
            try:
                print("Trying nbtlib parser...")
                nbt_data = nbtlib.load(file_path)
                result = self._convert_nbtlib_to_dict(nbt_data)
                if result and len(result) > 0:
                    print(f"✅ nbtlib berhasil: {len(result)} keys detected")
                    return result
            except Exception as e:
                print(f"❌ nbtlib gagal: {e}")
            
            # Method 3: Coba dengan nbtlib gzipped
            try:
                print("Trying nbtlib gzipped parser...")
                nbt_data = nbtlib.load(file_path, gzipped=True)
                result = self._convert_nbtlib_to_dict(nbt_data)
                if result and len(result) > 0:
                    print(f"✅ nbtlib gzipped berhasil: {len(result)} keys detected")
                    return result
            except Exception as e:
                print(f"❌ nbtlib gzipped gagal: {e}")
            
            # Method 4: Coba dengan nbtlib tanpa root
            try:
                print("Trying nbtlib without root...")
                nbt_data = nbtlib.load(file_path)
                if hasattr(nbt_data, 'root'):
                    result = self._convert_nbtlib_value(nbt_data.root)
                else:
                    result = self._convert_nbtlib_value(nbt_data)
                if result and len(result) > 0:
                    print(f"✅ nbtlib without root berhasil: {len(result)} keys detected")
                    return result
            except Exception as e:
                print(f"❌ nbtlib without root gagal: {e}")
            
            # Method 4: Manual binary parsing sebagai fallback
            print("Trying manual binary parser...")
            result = self._parse_binary_nbt(data)
            if result and len(result) > 0:
                print(f"✅ Manual parser berhasil: {len(result)} keys detected")
                return result
            
            print("❌ Semua metode parsing gagal")
            return {}
            
        except Exception as e:
            print(f"Dynamic parser failed: {e}")
            return {}
    
    def _convert_amulet_nbt_to_dict(self, nbt_data):
        """Convert amulet-nbt data to Python dict"""
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
        """Convert individual amulet-nbt value"""
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
        """Convert nbtlib data to Python dict"""
        try:
            if hasattr(nbt_data, 'root'):
                return self._convert_nbtlib_value(nbt_data.root)
            else:
                return self._convert_nbtlib_value(nbt_data)
        except Exception as e:
            print(f"Error converting nbtlib: {e}")
            return {}
    
    def _convert_nbtlib_value(self, value):
        """Convert individual nbtlib value"""
        try:
            if hasattr(value, 'items') and callable(getattr(value, 'items')):
                result = {}
                for k, v in value.items():
                    result[str(k)] = self._convert_nbtlib_value(v)
                return result
            elif isinstance(value, (list, tuple)):
                return [self._convert_nbtlib_value(v) for v in value]
            elif hasattr(value, 'value'):
                return self._convert_nbtlib_value(value.value)
            else:
                return value
        except Exception:
            return str(value)
    
    def _parse_binary_nbt(self, data):
        """Manual binary NBT parser sebagai fallback dengan struktur hierarkis"""
        try:
            result = {}
            pos = 0
            
            print(f"Manual parsing {len(data)} bytes...")
            
            # Skip header jika ada
            if len(data) > 4:
                # Coba skip gzip header
                if data[:2] == b'\x1f\x8b':
                    print("Detected gzipped data, skipping...")
                    # Untuk gzipped data, kita perlu gunakan library
                    return {}
                
                # Coba skip NBT header
                if data[:4] in [b'\x0A\x00\x00\x00', b'\x08\x00\x00\x00']:
                    print("Detected NBT header, skipping...")
                    pos = 4
            
            # Parse NBT structure dengan deteksi compound
            while pos < len(data) - 10:  # Minimal length untuk key-value pair
                # Cari string patterns (key names)
                string_pattern = self._find_string_pattern(data, pos)
                if string_pattern:
                    key_name, key_pos = string_pattern
                    pos = key_pos
                    
                    # Coba parse value setelah key
                    value, new_pos = self._parse_value_at(data, pos)
                    if value is not None:
                        # Cek apakah ini adalah compound tag
                        if self._is_compound_start(data, pos):
                            # Parse compound structure
                            compound_data = self._parse_compound_structure(data, pos, key_name)
                            if compound_data:
                                result[key_name] = compound_data
                                print(f"Found compound: {key_name} with {len(compound_data)} entries")
                            else:
                                result[key_name] = value
                        else:
                            result[key_name] = value
                        pos = new_pos
                    else:
                        pos += 1
                else:
                    pos += 1
            
            # Post-process untuk mengelompokkan key yang seharusnya dalam compound
            organized_result = self._organize_compound_keys(result)
            return organized_result
            
        except Exception as e:
            print(f"Binary parser error: {e}")
            return {}
    
    def _find_string_pattern(self, data, start_pos):
        """Find string pattern in binary data"""
        try:
            # Look for printable ASCII strings
            for pos in range(start_pos, min(start_pos + 200, len(data))):
                if data[pos] >= 32 and data[pos] <= 126:  # Printable ASCII
                    # Try to read string length
                    if pos + 2 <= len(data):
                        try:
                            str_len = struct.unpack('<H', data[pos:pos+2])[0]
                            if 1 <= str_len <= 100:  # Reasonable string length
                                str_start = pos + 2
                                if str_start + str_len <= len(data):
                                    key_name = data[str_start:str_start+str_len].decode('utf-8', errors='replace')
                                    if key_name.isprintable() and len(key_name.strip()) > 0:
                                        # Validasi bahwa ini adalah key yang valid
                                        if any(char.isalpha() for char in key_name):
                                            return key_name, str_start + str_len
                        except:
                            continue
                    
                    # Alternative: cari string tanpa length prefix
                    if pos + 1 < len(data):
                        try:
                            # Cari sampai null terminator atau non-printable
                            end_pos = pos
                            while end_pos < len(data) and data[end_pos] >= 32 and data[end_pos] <= 126:
                                end_pos += 1
                            
                            if end_pos > pos + 1:
                                key_name = data[pos:end_pos].decode('utf-8', errors='replace')
                                if len(key_name) >= 2 and any(char.isalpha() for char in key_name):
                                    return key_name, end_pos
                        except:
                            continue
            return None
        except Exception:
            return None
    
    def _parse_value_at(self, data, pos):
        """Parse NBT value at specific position"""
        try:
            if pos >= len(data):
                return None, pos
            
            # Try to detect value type
            byte_val = data[pos]
            
            # Byte value (0 or 1) - most common in Bedrock
            if byte_val in [0, 1]:
                return byte_val, pos + 1
            
            # Try to parse as integer (4 bytes)
            if pos + 4 <= len(data):
                try:
                    int_val = struct.unpack('<i', data[pos:pos+4])[0]
                    # Validasi range yang masuk akal untuk Minecraft
                    if -1000000 <= int_val <= 1000000:
                        return int_val, pos + 4
                except:
                    pass
            
            # Try to parse as long (8 bytes)
            if pos + 8 <= len(data):
                try:
                    long_val = struct.unpack('<q', data[pos:pos+8])[0]
                    # Validasi range yang masuk akal
                    if -1000000000 <= long_val <= 1000000000:
                        return long_val, pos + 8
                except:
                    pass
            
            # Try to parse as float (4 bytes)
            if pos + 4 <= len(data):
                try:
                    float_val = struct.unpack('<f', data[pos:pos+4])[0]
                    if not (float_val != float_val) and -1000 <= float_val <= 1000:  # Not NaN and reasonable range
                        return float_val, pos + 4
                except:
                    pass
            
            # Try to parse as short (2 bytes)
            if pos + 2 <= len(data):
                try:
                    short_val = struct.unpack('<h', data[pos:pos+2])[0]
                    if -32768 <= short_val <= 32767:
                        return short_val, pos + 2
                except:
                    pass
            
            return None, pos + 1
            
        except Exception:
            return None, pos + 1

    def _is_compound_start(self, data, pos):
        """Detect if position starts a compound tag"""
        try:
            if pos + 4 <= len(data):
                # Check for compound tag type (0x0A)
                if data[pos] == 0x0A:
                    return True
                # Check for list tag type (0x09)
                elif data[pos] == 0x09:
                    return True
            return False
        except Exception:
            return False
    
    def _parse_compound_structure(self, data, pos, compound_name):
        """Parse compound structure and find nested keys"""
        try:
            compound_data = {}
            
            # Define known compound structures
            if compound_name == "experiments":
                # Known experiments keys
                experiments_keys = [
                    'data_driven_biomes', 'experiments_ever_used', 'gametest',
                    'jigsaw_structures', 'saved_with_toggled_experiments',
                    'experimental_creator_cameras', 'upcoming_creator_features',
                    'villager_trades_rebalance', 'y_2025_drop_3'
                ]
                
                # Search for these keys in the data after compound start
                search_start = pos + 10  # Skip compound header
                search_end = min(pos + 500, len(data))  # Search in reasonable range
                
                for key in experiments_keys:
                    key_pos = self._find_key_in_range(data, search_start, search_end, key)
                    if key_pos:
                        value, _ = self._parse_value_at(data, key_pos + len(key.encode()))
                        if value is not None:
                            compound_data[key] = value
                
                return compound_data if compound_data else None
                
            elif compound_name == "abilities":
                # Known abilities keys
                abilities_keys = [
                    'attackmobs', 'attackplayers', 'build', 'doorsandswitches',
                    'flying', 'instabuild', 'invulnerable', 'lightning',
                    'mayfly', 'mine', 'op', 'opencontainers', 'teleport',
                    'flySpeed', 'walkSpeed', 'verticalFlySpeed'
                ]
                
                # Search for these keys in the data after compound start
                search_start = pos + 10  # Skip compound header
                search_end = min(pos + 500, len(data))  # Search in reasonable range
                
                for key in abilities_keys:
                    key_pos = self._find_key_in_range(data, search_start, search_end, key)
                    if key_pos:
                        value, _ = self._parse_value_at(data, key_pos + len(key.encode()))
                        if value is not None:
                            compound_data[key] = value
                
                return compound_data if compound_data else None
            
            return None
            
        except Exception as e:
            print(f"Error parsing compound {compound_name}: {e}")
            return None
    
    def _find_key_in_range(self, data, start_pos, end_pos, key_name):
        """Find a specific key within a data range"""
        try:
            key_bytes = key_name.encode('utf-8')
            for pos in range(start_pos, end_pos - len(key_bytes)):
                if data[pos:pos+len(key_bytes)] == key_bytes:
                    return pos
            return None
        except Exception:
            return None
    
    def _organize_compound_keys(self, flat_result):
        """Organize flat keys into proper compound structure"""
        try:
            organized = {}
            
            # Define compound mappings
            experiments_keys = [
                'data_driven_biomes', 'experiments_ever_used', 'gametest',
                'jigsaw_structures', 'saved_with_toggled_experiments',
                'experimental_creator_cameras', 'upcoming_creator_features',
                'villager_trades_rebalance', 'y_2025_drop_3'
            ]
            
            abilities_keys = [
                'attackmobs', 'attackplayers', 'build', 'doorsandswitches',
                'flying', 'instabuild', 'invulnerable', 'lightning',
                'mayfly', 'mine', 'op', 'opencontainers', 'teleport',
                'flySpeed', 'walkSpeed', 'verticalFlySpeed'
            ]
            
            # Process each key
            for key, value in flat_result.items():
                if str(key) in experiments_keys:
                    # Add to experiments compound
                    if 'experiments' not in organized:
                        organized['experiments'] = {}
                    elif not isinstance(organized['experiments'], dict):
                        # Convert existing value to dict if needed
                        organized['experiments'] = {}
                    organized['experiments'][str(key)] = value
                elif str(key) in abilities_keys:
                    # Add to abilities compound
                    if 'abilities' not in organized:
                        organized['abilities'] = {}
                    elif not isinstance(organized['abilities'], dict):
                        # Convert existing value to dict if needed
                        organized['abilities'] = {}
                    organized['abilities'][str(key)] = value
                elif str(key) == 'experiments' and isinstance(value, (int, float)):
                    # Skip the experiments marker key (it's just a flag)
                    pass
                elif str(key) == 'abilities' and isinstance(value, (int, float)):
                    # Skip the abilities marker key (it's just a flag)
                    pass
                else:
                    # Keep as top-level key
                    organized[str(key)] = value
            
            return organized
            
        except Exception as e:
            print(f"Error organizing compound keys: {e}")
            import traceback
            traceback.print_exc()
            return flat_result

    # Legacy methods for backward compatibility
    def _extract_value_by_type(self, data, pos, field_type):
        """Legacy method - kept for compatibility"""
        return self._parse_value_at(data, pos)[0]
    
    def _try_parse_compound_at(self, data, pos):
        """Legacy method - kept for compatibility"""
        return self._parse_binary_nbt(data[pos:pos+500])
