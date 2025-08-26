#!/usr/bin/env python3
"""
Bedrock NBT Parser - Converts raw NBT data to table format for GUI display
"""

import struct
import gzip
import io
import os
import zlib
from typing import Dict, Any, List, Tuple, Union
from .raw_nbt_reader import RawNBTReader, NBTValue

class BedrockNBTParser:
    """Bedrock NBT Parser that converts raw data to table format"""
    
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
    
    # Type mapping for display - shortened for table format
    TYPE_NAMES = {
        TAG_END: 'END',
        TAG_BYTE: 'B',
        TAG_SHORT: 'S',
        TAG_INT: 'I',
        TAG_LONG: 'L',
        TAG_FLOAT: 'F',
        TAG_DOUBLE: 'D',
        TAG_BYTE_ARRAY: 'BA',
        TAG_STRING: 'S',
        TAG_LIST: 'LIST',
        TAG_COMPOUND: 'COMP',
        TAG_INT_ARRAY: 'IA',
        TAG_LONG_ARRAY: 'LA'
    }
    
    def __init__(self, debug=False):
        self.debug_mode = debug
        self.table_data = []
        self.raw_data = {}
        
    def read_nbt_file(self, file_path: str) -> List[Tuple[str, Any, str]]:
        """Read NBT file and return table format data"""
        try:
            if self.debug_mode:
                print(f"📖 Reading NBT file: {file_path}")
            
            # Use the raw NBT reader to get data
            raw_reader = RawNBTReader(file_path)
            self.raw_data = raw_reader.read_nbt()
            
            # Convert to table format
            self.table_data = self._convert_to_table_format(self.raw_data)
            
            return self.table_data
                    
        except Exception as e:
            if self.debug_mode:
                print(f"❌ Error reading NBT file: {e}")
            raise
    
    def _convert_to_table_format(self, nbt_data: Dict[str, Any], prefix: str = "") -> List[Tuple[str, Any, str, int]]:
        """Convert NBT data to table format: (field_name, value, type, level)"""
        table_data = []
        
        for root_name, root_value in nbt_data.items():
            if isinstance(root_value, dict):
                # Process compound
                for field_name, field_value in root_value.items():
                    full_name = f"{prefix}{field_name}" if prefix else field_name
                    table_data.extend(self._process_field(full_name, field_value, 0))
            else:
                # Direct value
                table_data.extend(self._process_field(root_name, root_value, 0))
        
        return table_data
    
    def _process_field(self, field_name: str, field_value: Any, level: int = 0) -> List[Tuple[str, Any, str, int]]:
        """Process a single field and return table entries with hierarchy level"""
        table_entries = []
        
        if isinstance(field_value, NBTValue):
            # Handle NBTValue objects
            actual_value = field_value.value
            nbt_type = field_value.nbt_type
            type_name = self.TYPE_NAMES.get(nbt_type, f"UNKNOWN_{nbt_type}")
            
            if nbt_type == self.TAG_COMPOUND:
                # Compound type - add parent node first, then process nested fields
                if isinstance(actual_value, dict):
                    # Add parent compound node
                    parent_value = f"{{{len(actual_value)} entries}}"
                    table_entries.append((field_name, parent_value, type_name, level))
                    
                    # Process nested fields with increased level
                    for nested_name, nested_value in actual_value.items():
                        nested_field_name = f"{field_name}.{nested_name}"
                        table_entries.extend(self._process_field(nested_field_name, nested_value, level + 1))
                else:
                    table_entries.append((field_name, str(actual_value), type_name, level))
            
            elif nbt_type == self.TAG_LIST:
                # List type - add parent node first, then process list items
                if isinstance(actual_value, list):
                    # Add parent list node
                    parent_value = f"[{len(actual_value)} entries]"
                    table_entries.append((field_name, parent_value, type_name, level))
                    
                    # Process list items with increased level
                    for i, item in enumerate(actual_value):
                        list_field_name = f"{field_name}[{i}]"
                        table_entries.extend(self._process_field(list_field_name, item, level + 1))
                else:
                    table_entries.append((field_name, str(actual_value), type_name, level))
            
            elif nbt_type == self.TAG_BYTE_ARRAY:
                # Byte array - show as list
                if isinstance(actual_value, list):
                    formatted_value = f"[{len(actual_value)} bytes]"
                    table_entries.append((field_name, formatted_value, type_name, level))
                else:
                    table_entries.append((field_name, str(actual_value), type_name, level))
            
            elif nbt_type == self.TAG_INT_ARRAY:
                # Int array - show as list
                if isinstance(actual_value, list):
                    formatted_value = f"[{len(actual_value)} integers]"
                    table_entries.append((field_name, formatted_value, type_name, level))
                else:
                    table_entries.append((field_name, str(actual_value), type_name, level))
            
            elif nbt_type == self.TAG_LONG_ARRAY:
                # Long array - show as list
                if isinstance(actual_value, list):
                    formatted_value = f"[{len(actual_value)} longs]"
                    table_entries.append((field_name, formatted_value, type_name, level))
                else:
                    table_entries.append((field_name, str(actual_value), type_name, level))
            
            else:
                # Simple types - add directly
                table_entries.append((field_name, actual_value, type_name, level))
        
        elif isinstance(field_value, dict):
            # Dictionary - add parent node first, then process nested fields
            parent_value = f"{{{len(field_value)} entries}}"
            table_entries.append((field_name, parent_value, "COMP", level))
            
            for nested_name, nested_value in field_value.items():
                nested_field_name = f"{field_name}.{nested_name}"
                table_entries.extend(self._process_field(nested_field_name, nested_value, level + 1))
        
        elif isinstance(field_value, list):
            # List - add parent node first, then process list items
            parent_value = f"[{len(field_value)} entries]"
            table_entries.append((field_name, parent_value, "LIST", level))
            
            for i, item in enumerate(field_value):
                list_field_name = f"{field_name}[{i}]"
                table_entries.extend(self._process_field(list_field_name, item, level + 1))
        
        else:
            # Simple value - add directly
            table_entries.append((field_name, field_value, "UNKNOWN", level))
        
        return table_entries
    
    def get_formatted_structure(self) -> List[str]:
        """Get formatted structure strings for display"""
        formatted = []
        for field_name, value, type_name, level in self.table_data:
            # Format the value for display
            if isinstance(value, (list, dict)):
                if isinstance(value, list):
                    formatted_value = f"[{len(value)} items]"
                else:  # dict
                    formatted_value = f"{{{len(value)} items}}"
            elif type_name == 'STRING':
                formatted_value = f'"{value}"'
            else:
                formatted_value = str(value)
            
            # Format output to match required pattern: [field_name: (value, type)]
            formatted.append(f"[{field_name}: ({formatted_value}, {type_name})]")
        
        return formatted

    def get_structure_display(self) -> List[Tuple[str, Any, str, int]]:
        """Get the structure in the required format: (field_name, value, type, level)"""
        return self.table_data
    
    def get_raw_data(self) -> Dict[str, Any]:
        """Get the raw NBT data"""
        return self.raw_data
    
    def get_table_format(self) -> List[Tuple[str, str, Any, int]]:
        """Get data in table format: (type, field_name, value, level)"""
        table_format = []
        for field_name, value, type_name, level in self.table_data:
            table_format.append((type_name, field_name, value, level))
        return table_format
    
    def get_table_display(self) -> str:
        """Get formatted table display string"""
        if not self.table_data:
            return "No data available"
        
        # Fixed column widths for better formatting
        type_width = 6
        name_width = 35
        value_width = 50
        
        # Create header
        header = f"{'Type':<{type_width}} {'Nama':<{name_width}} {'Value':<{value_width}}"
        separator = "-" * len(header)
        
        # Create rows
        rows = []
        for field_name, value, type_name, level in self.table_data:
            # Truncate long values for display
            display_value = str(value)
            if len(display_value) > value_width - 3:
                display_value = display_value[:value_width-6] + "..."
            
            # Truncate long field names
            display_name = field_name
            if len(display_name) > name_width - 3:
                display_name = display_name[:name_width-6] + "..."
            
            row = f"{type_name:<{type_width}} {display_name:<{name_width}} {display_value:<{value_width}}"
            rows.append(row)
        
        # Combine all parts
        return f"{header}\n{separator}\n" + "\n".join(rows)

# Alias for backward compatibility
AccurateBedrockNBTReader = BedrockNBTParser
