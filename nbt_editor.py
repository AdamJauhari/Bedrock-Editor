#!/usr/bin/env python3
"""
NBT Editor - Handles editing and saving NBT/DAT files
"""

import os
import struct
import gzip
import shutil
import json
from typing import Dict, Any, List, Set, Optional, Tuple
from nbt_reader.bedrock_nbt_parser import BedrockNBTParser

# Import nbtlib for proper NBT encoding
try:
    import nbtlib
except ImportError:
    nbtlib = None



class NBTEditor:
    """NBT Editor for editing and saving NBT/DAT files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.original_data = {}
        self.current_data = {}
        self.modified_fields = {}  # field_name -> (original_value, new_value)
        self.parser = BedrockNBTParser(debug=True)
        
    def load_file(self) -> bool:
        """Load the NBT file and store original data"""
        try:
            print(f"📖 Loading NBT file: {self.file_path}")
            
            # Read the file using parser
            table_data = self.parser.read_nbt_file(self.file_path)
            
            # Convert table data back to dictionary format
            self.original_data = self._table_to_dict(table_data)
            self.current_data = self._deep_copy(self.original_data)
            
            print(f"✅ Loaded {len(self.original_data)} root fields")
            return True
            
        except Exception as e:
            print(f"❌ Error loading file: {e}")
            return False
    
    def _table_to_dict(self, table_data: List[tuple]) -> Dict[str, Any]:
        """Convert table data back to dictionary format"""
        result = {}
        
        try:
            for entry in table_data:
                # Handle different tuple lengths
                if len(entry) == 4:
                    field_name, value, type_name, level = entry
                elif len(entry) == 3:
                    field_name, value, type_name = entry
                    level = 0
                else:
                    print(f"⚠️ Unexpected tuple length: {len(entry)}")
                    continue
                
                if level == 0:  # Root level
                    result[field_name] = value
                else:
                    # Handle nested fields
                    parts = field_name.split('.')
                    current = result
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        elif not isinstance(current[part], dict):
                            # If the part exists but is not a dict, convert it to dict
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
            
            return result
            
        except Exception as e:
            print(f"❌ Error in _table_to_dict: {e}")
            print(f"   Table data type: {type(table_data)}")
            print(f"   Table data length: {len(table_data) if table_data else 0}")
            if table_data and len(table_data) > 0:
                print(f"   First entry: {table_data[0]}")
                print(f"   First entry type: {type(table_data[0])}")
            raise
    
    def _deep_copy(self, data: Any) -> Any:
        """Create a deep copy of data"""
        if isinstance(data, dict):
            return {key: self._deep_copy(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._deep_copy(item) for item in data]
        else:
            return data
    
    def _get_field_value(self, data: Dict[str, Any], field_name: str) -> Any:
        """Get value of a field from data dictionary"""
        try:
            parts = field_name.split('.')
            current = data
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            
            return current
            
        except Exception as e:
            print(f"❌ Error getting field {field_name}: {e}")
            return None
    
    def _set_field_value(self, data: Dict[str, Any], field_name: str, value: Any) -> bool:
        """Set value of a field in data dictionary"""
        try:
            parts = field_name.split('.')
            current = data
            
            # Navigate to the parent
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value
            current[parts[-1]] = value
            return True
            
        except Exception as e:
            print(f"❌ Error setting field {field_name}: {e}")
            return False
    
    def _values_equal(self, val1: Any, val2: Any) -> bool:
        """Compare two values for equality, handling different types"""
        try:
            # Handle None values
            if val1 is None and val2 is None:
                return True
            if val1 is None or val2 is None:
                return False
            
            # Handle different types - try to convert for comparison
            if type(val1) != type(val2):
                # Try to convert to same type for comparison
                try:
                    if isinstance(val1, (int, float)) and isinstance(val2, str):
                        # Try to convert string to number
                        if isinstance(val1, int):
                            converted_val2 = int(val2)
                        else:
                            converted_val2 = float(val2)
                        return val1 == converted_val2
                    elif isinstance(val2, (int, float)) and isinstance(val1, str):
                        # Try to convert string to number
                        if isinstance(val2, int):
                            converted_val1 = int(val1)
                        else:
                            converted_val1 = float(val2)
                        return converted_val1 == val2
                    else:
                        # For other type mismatches, compare as strings
                        return str(val1) == str(val2)
                except (ValueError, TypeError):
                    return str(val1) == str(val2)
            
            # Same type comparison
            return val1 == val2
            
        except Exception as e:
            print(f"❌ Error comparing values: {e}")
            return False
    
    def update_field(self, field_name: str, new_value: Any) -> bool:
        """Update a field value and mark it as modified if different"""
        try:
            # Get original value
            original_value = self._get_field_value(self.original_data, field_name)
            
            # Check if value actually changed
            if self._values_equal(original_value, new_value):
                print(f"ℹ️ Field {field_name} unchanged: {original_value}")
                return True
            
            # Update the current data
            if not self._set_field_value(self.current_data, field_name, new_value):
                return False
            
            # Mark as modified with both original and new values
            self.modified_fields[field_name] = (original_value, new_value)
            
            print(f"✅ Updated field: {field_name}")
            print(f"   Original: {original_value} ({type(original_value).__name__})")
            print(f"   New: {new_value} ({type(new_value).__name__})")
            return True
            
        except Exception as e:
            print(f"❌ Error updating field {field_name}: {e}")
            return False
    
    def has_modifications(self) -> bool:
        """Check if there are any modifications"""
        return len(self.modified_fields) > 0
    
    def get_modified_fields(self) -> List[str]:
        """Get list of modified field names"""
        return list(self.modified_fields.keys())
    
    def get_field_value(self, field_name: str) -> Any:
        """Get current value of a field"""
        return self._get_field_value(self.current_data, field_name)
    
    def get_original_field_value(self, field_name: str) -> Any:
        """Get original value of a field"""
        return self._get_field_value(self.original_data, field_name)
    
    def save_file(self, backup: bool = True) -> bool:
        """Save the modified data back to the NBT file"""
        try:
            if not self.has_modifications():
                print("ℹ️ No modifications to save")
                return True
            
            print(f"💾 Saving {len(self.modified_fields)} modified fields...")
            
            # Show what will be saved
            for field_name, (original, new) in self.modified_fields.items():
                print(f"   {field_name}: {original} → {new}")
            
            # Create backup if requested
            if backup:
                backup_path = self.file_path + ".backup"
                shutil.copy2(self.file_path, backup_path)
                print(f"✅ Backup created: {backup_path}")
            
            # Use byte-level modification for reliability
            success = self._save_with_byte_modification()
            
            if success:
                # Update original data to current data
                self.original_data = self._deep_copy(self.current_data)
                self.modified_fields.clear()
                print(f"✅ File saved successfully")
            else:
                print(f"❌ Failed to save file")
            
            return success
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            return False
    
    def _rebuild_nbt_file(self) -> bool:
        """Rebuild the NBT file with current data"""
        try:
            # Try nbtlib first (most reliable)
            if nbtlib is not None:
                return self._rebuild_with_nbtlib()
            
            # Fallback to manual encoding
            print("⚠️ No NBT libraries available, using manual encoding")
            return self._rebuild_nbt_file_fallback()
            
        except Exception as e:
            print(f"❌ Error rebuilding NBT file: {e}")
            return self._rebuild_nbt_file_fallback()
    

    
    def _rebuild_with_nbtlib(self) -> bool:
        """Rebuild NBT file using nbtlib"""
        try:
            # Convert our data to nbtlib format
            nbt_data = self._convert_to_nbtlib_format(self.current_data)
            
            # Create nbtlib compound
            compound = nbtlib.Compound(nbt_data)
            
            # Read original file to get header
            with open(self.file_path, 'rb') as f:
                original_data = f.read()
            
            # Extract header (first 8 bytes for Bedrock)
            header = original_data[:8]
            
            # Create temporary file for nbtlib
            temp_file = self.file_path + ".temp"
            
            # Save with nbtlib (uncompressed for Bedrock)
            nbtlib.File({'': compound}).save(temp_file, gzipped=False)
            
            # Read the NBT data without header
            with open(temp_file, 'rb') as f:
                nbt_content = f.read()
            
            # Remove temp file
            os.remove(temp_file)
            
            # Combine header + NBT data
            result = header + nbt_content
            
            # Write to file
            with open(self.file_path, 'wb') as f:
                f.write(result)
            
            return True
            
        except Exception as e:
            print(f"❌ Error with nbtlib: {e}")
            return False
    
    def _rebuild_nbt_file_fallback(self) -> bool:
        """Fallback method for rebuilding NBT file without nbtlib"""
        try:
            # Read original file to get header
            with open(self.file_path, 'rb') as f:
                original_data = f.read()
            
            # Extract header (first 8 bytes for Bedrock)
            header = original_data[:8]
            
            # Create NBT structure
            nbt_data = bytearray()
            
            # Add NBT root compound
            nbt_data.append(10)  # TAG_Compound
            
            # Add root name (usually empty for level.dat)
            root_name = ""
            name_bytes = root_name.encode('utf-8')
            nbt_data.extend(struct.pack('<h', len(name_bytes)))
            nbt_data.extend(name_bytes)
            
            # Add all fields
            for field_name, value in self.current_data.items():
                nbt_data.extend(self._encode_simple_field(field_name, value))
            
            # Add end tag
            nbt_data.append(0)  # TAG_End
            
            # Combine header + NBT data
            result = header + nbt_data
            
            # Write to file
            with open(self.file_path, 'wb') as f:
                f.write(result)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in fallback NBT rebuild: {e}")
            return False
    

    
    def _convert_to_nbtlib_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert our data format to nbtlib format"""
        if nbtlib is None:
            raise ImportError("nbtlib not available")
            
        result = {}
        
        for key, value in data.items():
            if isinstance(value, bool):
                result[key] = nbtlib.Byte(1 if value else 0)
            elif isinstance(value, int):
                if value in [0, 1]:
                    result[key] = nbtlib.Byte(value)
                elif -2147483648 <= value <= 2147483647:
                    result[key] = nbtlib.Int(value)
                else:
                    result[key] = nbtlib.Long(value)
            elif isinstance(value, float):
                result[key] = nbtlib.Float(value)
            elif isinstance(value, str):
                result[key] = nbtlib.String(value)
            elif isinstance(value, dict):
                result[key] = nbtlib.Compound(self._convert_to_nbtlib_format(value))
            elif isinstance(value, list):
                if value:
                    # Determine type from first element
                    first_item = value[0]
                    if isinstance(first_item, bool):
                        result[key] = nbtlib.List([nbtlib.Byte(1 if item else 0) for item in value])
                    elif isinstance(first_item, int):
                        if any(item in [0, 1] for item in value):
                            result[key] = nbtlib.List([nbtlib.Byte(item) for item in value])
                        else:
                            result[key] = nbtlib.List([nbtlib.Int(item) for item in value])
                    elif isinstance(first_item, float):
                        result[key] = nbtlib.List([nbtlib.Float(item) for item in value])
                    elif isinstance(first_item, str):
                        result[key] = nbtlib.List([nbtlib.String(item) for item in value])
                    else:
                        result[key] = nbtlib.List([nbtlib.String(str(item)) for item in value])
                else:
                    result[key] = nbtlib.List([])
            else:
                result[key] = nbtlib.String(str(value))
        
        return result
    
    def _encode_simple_field(self, field_name: str, value: Any) -> bytes:
        """Encode a field in simplified NBT format"""
        result = bytearray()
        
        try:
            # Add field name
            name_bytes = field_name.encode('utf-8')
            result.extend(struct.pack('<h', len(name_bytes)))
            result.extend(name_bytes)
            
            # Add value based on type
            if isinstance(value, bool):
                result.append(1)  # TAG_Byte
                result.append(1 if value else 0)
            elif isinstance(value, int) and value in [0, 1]:
                # Small integers 0/1 should be stored as TAG_Byte (boolean)
                result.append(1)  # TAG_Byte
                result.append(value)
            elif isinstance(value, int):
                # Check if value fits in 32-bit signed integer
                if -2147483648 <= value <= 2147483647:
                    result.append(3)  # TAG_Int
                    result.extend(struct.pack('<i', value))
                else:
                    # Use TAG_Long for large integers
                    result.append(4)  # TAG_Long
                    result.extend(struct.pack('<q', value))
            elif isinstance(value, float):
                result.append(5)  # TAG_Float
                result.extend(struct.pack('<f', value))
            elif isinstance(value, str):
                result.append(8)  # TAG_String
                value_bytes = value.encode('utf-8')
                result.extend(struct.pack('<h', len(value_bytes)))
                result.extend(value_bytes)
            elif isinstance(value, dict):
                result.append(10)  # TAG_Compound
                for key, val in value.items():
                    result.extend(self._encode_simple_field(key, val))
                result.append(0)  # TAG_End
            elif isinstance(value, list):
                result.append(9)  # TAG_List
                if value:
                    # Determine type from first element
                    first_type = self._get_nbt_type(value[0])
                    result.append(first_type)
                    result.extend(struct.pack('<i', len(value)))
                    for item in value:
                        result.extend(self._encode_simple_value(item, first_type))
                else:
                    result.append(1)  # TAG_Byte as default
                    result.extend(struct.pack('<i', 0))
            else:
                # Default to string
                result.append(8)  # TAG_String
                value_str = str(value)
                value_bytes = value_str.encode('utf-8')
                result.extend(struct.pack('<h', len(value_bytes)))
                result.extend(value_bytes)
            
            return bytes(result)
            
        except Exception as e:
            print(f"❌ Error encoding field {field_name} with value {value}: {e}")
            # Fallback to string encoding
            result = bytearray()
            name_bytes = field_name.encode('utf-8')
            result.extend(struct.pack('<h', len(name_bytes)))
            result.extend(name_bytes)
            result.append(8)  # TAG_String
            value_str = str(value)
            value_bytes = value_str.encode('utf-8')
            result.extend(struct.pack('<h', len(value_bytes)))
            result.extend(value_bytes)
            return bytes(result)
    
    def _encode_simple_value(self, value: Any, nbt_type: int) -> bytes:
        """Encode a value without field name (for lists)"""
        result = bytearray()
        
        try:
            if nbt_type == 1:  # TAG_Byte
                result.extend(struct.pack('<b', 1 if value else 0))
            elif nbt_type == 3:  # TAG_Int
                # Check if value fits in 32-bit signed integer
                if -2147483648 <= value <= 2147483647:
                    result.extend(struct.pack('<i', value))
                else:
                    # Use TAG_Long for large integers
                    result.extend(struct.pack('<q', value))
            elif nbt_type == 4:  # TAG_Long
                result.extend(struct.pack('<q', value))
            elif nbt_type == 5:  # TAG_Float
                result.extend(struct.pack('<f', value))
            elif nbt_type == 8:  # TAG_String
                value_str = str(value)
                value_bytes = value_str.encode('utf-8')
                result.extend(struct.pack('<h', len(value_bytes)))
                result.extend(value_bytes)
            else:
                # Fallback to string
                value_str = str(value)
                value_bytes = value_str.encode('utf-8')
                result.extend(struct.pack('<h', len(value_bytes)))
                result.extend(value_bytes)
            
            return bytes(result)
            
        except Exception as e:
            print(f"❌ Error encoding value {value} with type {nbt_type}: {e}")
            # Fallback to string encoding
            result = bytearray()
            value_str = str(value)
            value_bytes = value_str.encode('utf-8')
            result.extend(struct.pack('<h', len(value_bytes)))
            result.extend(value_bytes)
            return bytes(result)
    
    def _get_nbt_type(self, value: Any) -> int:
        """Get NBT type for a value"""
        if isinstance(value, bool):
            return 1  # TAG_Byte
        elif isinstance(value, int):
            # Small integers 0/1 should be TAG_Byte (boolean)
            if value in [0, 1]:
                return 1  # TAG_Byte
            # Check if value fits in 32-bit signed integer
            elif -2147483648 <= value <= 2147483647:
                return 3  # TAG_Int
            else:
                return 4  # TAG_Long
        elif isinstance(value, float):
            return 5  # TAG_Float
        elif isinstance(value, str):
            return 8  # TAG_String
        elif isinstance(value, dict):
            return 10  # TAG_Compound
        elif isinstance(value, list):
            return 9  # TAG_List
        else:
            return 8  # TAG_String as default

    def _save_with_byte_modification(self) -> bool:
        """Save using byte-level modification for reliability"""
        try:
            # Load the original file as bytes
            with open(self.file_path, 'rb') as f:
                data = bytearray(f.read())
            
            # Extract header and NBT data
            header = data[:8]
            nbt_data = data[8:]
            
            # Apply modifications using byte-level approach
            for field_name, (original, new) in self.modified_fields.items():
                if not self._modify_field_bytes(nbt_data, field_name, new):
                    print(f"❌ Failed to modify {field_name} at byte level")
                    return False
            
            # Combine header and modified NBT data
            result = header + nbt_data
            
            # Write to file
            with open(self.file_path, 'wb') as f:
                f.write(result)
                f.flush()
                os.fsync(f.fileno())  # Ensure data is written to disk
            
            return True
            
        except Exception as e:
            print(f"❌ Error in byte-level modification: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _modify_field_bytes(self, nbt_data: bytearray, field_name: str, new_value: Any) -> bool:
        """Modify a field at the byte level"""
        try:
            # Find the field position and type
            if '.' in field_name:
                # Nested field
                result = self._find_nested_field_bytes(nbt_data, field_name)
            else:
                # Simple field
                result = self._find_field_bytes(nbt_data, field_name)
            
            if result is None:
                print(f"❌ Field {field_name} not found at byte level")
                return False
            
            value_pos, tag_type = result
            
            # Modify the value based on type
            if tag_type == 1:  # TAG_Byte
                if isinstance(new_value, (int, bool)) and 0 <= int(new_value) <= 255:
                    nbt_data[value_pos] = int(new_value)
                    return True
                else:
                    print(f"❌ Value {new_value} out of range for TAG_Byte")
                    return False
            elif tag_type == 3:  # TAG_Int
                if isinstance(new_value, int) and -2147483648 <= new_value <= 2147483647:
                    nbt_data[value_pos:value_pos+4] = struct.pack('<i', new_value)
                    return True
                else:
                    print(f"❌ Value {new_value} out of range for TAG_Int")
                    return False
            else:
                print(f"❌ Unsupported tag type {tag_type} for field {field_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error modifying field {field_name} at byte level: {e}")
            return False
    
    def _find_field_bytes(self, nbt_data: bytearray, field_name: str) -> tuple:
        """Find a field in the NBT data and return its position and type"""
        try:
            pos = 0
            
            # Skip root compound tag
            if pos < len(nbt_data) and nbt_data[pos] == 10:  # TAG_Compound
                pos += 1
                
                # Skip root name
                if pos + 2 <= len(nbt_data):
                    name_len = struct.unpack('<h', nbt_data[pos:pos+2])[0]
                    pos += 2 + name_len
                    
                    # Search for the field
                    while pos < len(nbt_data):
                        if nbt_data[pos] == 0:  # TAG_End
                            break
                        
                        # Read field tag type
                        tag_type = nbt_data[pos]
                        pos += 1
                        
                        # Read field name
                        if pos + 2 <= len(nbt_data):
                            field_name_len = struct.unpack('<h', nbt_data[pos:pos+2])[0]
                            pos += 2
                            
                            if pos + field_name_len <= len(nbt_data):
                                current_field_name = nbt_data[pos:pos+field_name_len].decode('utf-8')
                                pos += field_name_len
                                
                                if current_field_name == field_name:
                                    # Found the field
                                    value_pos = pos
                                    return (value_pos, tag_type)
                                
                                # Skip field value
                                pos = self._skip_value_bytes(nbt_data, pos, tag_type)
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
            
        except Exception as e:
            print(f"❌ Error finding field {field_name} at byte level: {e}")
            return None
    
    def _find_nested_field_bytes(self, nbt_data: bytearray, field_path: str) -> tuple:
        """Find a nested field using dot notation"""
        try:
            path_parts = field_path.split('.')
            
            pos = 0
            
            # Skip root compound tag
            if pos < len(nbt_data) and nbt_data[pos] == 10:  # TAG_Compound
                pos += 1
                
                # Skip root name
                if pos + 2 <= len(nbt_data):
                    name_len = struct.unpack('<h', nbt_data[pos:pos+2])[0]
                    pos += 2 + name_len
                    
                    # Navigate through the path
                    for i, part in enumerate(path_parts):
                        found = False
                        
                        # Search for the current part in the compound
                        while pos < len(nbt_data):
                            if nbt_data[pos] == 0:  # TAG_End
                                break
                            
                            # Read field tag type
                            tag_type = nbt_data[pos]
                            pos += 1
                            
                            # Read field name
                            if pos + 2 <= len(nbt_data):
                                field_name_len = struct.unpack('<h', nbt_data[pos:pos+2])[0]
                                pos += 2
                                
                                if pos + field_name_len <= len(nbt_data):
                                    current_field_name = nbt_data[pos:pos+field_name_len].decode('utf-8')
                                    pos += field_name_len
                                    
                                    if current_field_name == part:
                                        # Found the current part
                                        if i == len(path_parts) - 1:
                                            # This is the target field
                                            value_pos = pos
                                            return (value_pos, tag_type)
                                        else:
                                            # This is a compound, navigate into it
                                            if tag_type == 10:  # TAG_Compound
                                                found = True
                                                break  # Continue to next part
                                            else:
                                                print(f"❌ Error: {part} is not a compound (type: {tag_type})")
                                                return None
                                    
                                    # Skip field value
                                    pos = self._skip_value_bytes(nbt_data, pos, tag_type)
                                else:
                                    break
                            else:
                                break
                        else:
                            break
                        
                        if not found:
                            print(f"❌ Error: Could not find compound {part}")
                            return None
                    
                    print(f"❌ Error: Field path {field_path} not found")
                    return None
                else:
                    print("❌ Error: Not enough data for root name length")
                    return None
            else:
                print("❌ Error: Root tag is not TAG_Compound")
                return None
            
        except Exception as e:
            print(f"❌ Error finding nested field {field_path} at byte level: {e}")
            return None
    
    def _skip_value_bytes(self, nbt_data: bytearray, pos: int, tag_type: int) -> int:
        """Skip a value and return the new position"""
        try:
            if tag_type == 1:  # TAG_Byte
                return pos + 1
            elif tag_type == 2:  # TAG_Short
                return pos + 2
            elif tag_type == 3:  # TAG_Int
                return pos + 4
            elif tag_type == 4:  # TAG_Long
                return pos + 8
            elif tag_type == 5:  # TAG_Float
                return pos + 4
            elif tag_type == 6:  # TAG_Double
                return pos + 8
            elif tag_type == 7:  # TAG_Byte_Array
                if pos + 4 <= len(nbt_data):
                    length = struct.unpack('<i', nbt_data[pos:pos+4])[0]
                    return pos + 4 + length
                return pos
            elif tag_type == 8:  # TAG_String
                if pos + 2 <= len(nbt_data):
                    length = struct.unpack('<h', nbt_data[pos:pos+2])[0]
                    return pos + 2 + length
                return pos
            elif tag_type == 9:  # TAG_List
                if pos + 5 <= len(nbt_data):
                    list_type = nbt_data[pos]
                    length = struct.unpack('<i', nbt_data[pos+1:pos+5])[0]
                    pos += 5
                    for _ in range(length):
                        pos = self._skip_value_bytes(nbt_data, pos, list_type)
                    return pos
                return pos
            elif tag_type == 10:  # TAG_Compound
                # Skip all fields in the compound until we find TAG_End
                while pos < len(nbt_data):
                    if nbt_data[pos] == 0:  # TAG_End
                        return pos + 1  # Skip TAG_End
                    
                    # Skip field tag type
                    pos += 1
                    
                    # Skip field name
                    if pos + 2 <= len(nbt_data):
                        field_name_len = struct.unpack('<h', nbt_data[pos:pos+2])[0]
                        pos += 2 + field_name_len
                        
                        # Skip field value
                        if pos < len(nbt_data):
                            field_type = nbt_data[pos-2-field_name_len-1]  # Get the tag type we skipped
                            pos = self._skip_value_bytes(nbt_data, pos, field_type)
                        else:
                            return pos
                    else:
                        return pos
                return pos
            elif tag_type == 11:  # TAG_Int_Array
                if pos + 4 <= len(nbt_data):
                    length = struct.unpack('<i', nbt_data[pos:pos+4])[0]
                    return pos + 4 + length * 4
                return pos
            elif tag_type == 12:  # TAG_Long_Array
                if pos + 4 <= len(nbt_data):
                    length = struct.unpack('<i', nbt_data[pos:pos+4])[0]
                    return pos + 4 + length * 8
                return pos
            else:
                return pos
        except Exception as e:
            print(f"❌ Error skipping value at byte level: {e}")
            return pos
