#!/usr/bin/env python3
"""
Raw NBT Reader for Minecraft Bedrock Level.dat
Membaca dan menampilkan data NBT dari file level.dat secara dinamis
"""

import struct
import sys
import os
import platform
from typing import Any, Dict, List, Union, Tuple, Optional


class RawNBTReader:
    """Class untuk membaca file NBT Minecraft Bedrock secara mentah"""
    
    # Tag types untuk NBT format
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
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = None
        self.position = 0
        
    def read_file(self) -> bytes:
        """Membaca file level.dat"""
        try:
            with open(self.file_path, 'rb') as f:
                # Skip header (8 bytes untuk Bedrock Edition)
                f.seek(8)
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def read_byte(self) -> int:
        """Membaca 1 byte"""
        if self.position >= len(self.data):
            raise Exception("Unexpected end of data")
        value = self.data[self.position]
        self.position += 1
        return value
    
    def read_short(self) -> int:
        """Membaca 2 bytes (short) - Little Endian untuk Bedrock"""
        if self.position + 2 > len(self.data):
            raise Exception("Unexpected end of data")
        value = struct.unpack('<h', self.data[self.position:self.position+2])[0]
        self.position += 2
        return value
    
    def read_int(self) -> int:
        """Membaca 4 bytes (int) - Little Endian untuk Bedrock"""
        if self.position + 4 > len(self.data):
            raise Exception("Unexpected end of data")
        value = struct.unpack('<i', self.data[self.position:self.position+4])[0]
        self.position += 4
        return value
    
    def read_long(self) -> int:
        """Membaca 8 bytes (long) - Bedrock uses swapped 32-bit chunks with little endian"""
        if self.position + 8 > len(self.data):
            raise Exception("Unexpected end of data")
        
        # Read 8 bytes and swap the 4-byte chunks, then interpret as little endian
        raw_bytes = self.data[self.position:self.position+8]
        swapped_bytes = raw_bytes[4:8] + raw_bytes[0:4]  # Swap high and low 32-bit parts
        value = struct.unpack('<q', swapped_bytes)[0]
        
        self.position += 8
        return value
    
    def read_float(self) -> float:
        """Membaca 4 bytes (float) - Little Endian untuk Bedrock"""
        if self.position + 4 > len(self.data):
            raise Exception("Unexpected end of data")
        value = struct.unpack('<f', self.data[self.position:self.position+4])[0]
        self.position += 4
        return value
    
    def read_double(self) -> float:
        """Membaca 8 bytes (double) - Little Endian untuk Bedrock"""
        if self.position + 8 > len(self.data):
            raise Exception("Unexpected end of data")
        value = struct.unpack('<d', self.data[self.position:self.position+8])[0]
        self.position += 8
        return value
    
    def read_string(self) -> str:
        """Membaca string dengan panjang variabel"""
        length = self.read_short()
        if self.position + length > len(self.data):
            raise Exception("Unexpected end of data")
        value = self.data[self.position:self.position+length].decode('utf-8', errors='replace')
        self.position += length
        return value
    
    def read_byte_array(self) -> List[int]:
        """Membaca array of bytes"""
        length = self.read_int()
        if self.position + length > len(self.data):
            raise Exception("Unexpected end of data")
        array = list(self.data[self.position:self.position+length])
        self.position += length
        return array
    
    def read_int_array(self) -> List[int]:
        """Membaca array of integers"""
        length = self.read_int()
        array = []
        for _ in range(length):
            array.append(self.read_int())
        return array
    
    def read_long_array(self) -> List[int]:
        """Membaca array of longs"""
        length = self.read_int()
        array = []
        for _ in range(length):
            array.append(self.read_long())
        return array
    
    def read_tag_payload(self, tag_type: int) -> Tuple[Any, int]:
        """Membaca payload berdasarkan tag type, return (value, tag_type)"""
        if tag_type == self.TAG_BYTE:
            byte_value = self.read_byte()
            # Keep as integer 0/1 for easier editing, don't convert to bool
            return (byte_value, tag_type)
        elif tag_type == self.TAG_SHORT:
            return (self.read_short(), tag_type)
        elif tag_type == self.TAG_INT:
            return (self.read_int(), tag_type)
        elif tag_type == self.TAG_LONG:
            return (self.read_long(), tag_type)
        elif tag_type == self.TAG_FLOAT:
            return (self.read_float(), tag_type)
        elif tag_type == self.TAG_DOUBLE:
            return (self.read_double(), tag_type)
        elif tag_type == self.TAG_BYTE_ARRAY:
            return (self.read_byte_array(), tag_type)
        elif tag_type == self.TAG_STRING:
            return (self.read_string(), tag_type)
        elif tag_type == self.TAG_LIST:
            return self.read_list()
        elif tag_type == self.TAG_COMPOUND:
            return (self.read_compound(), tag_type)
        elif tag_type == self.TAG_INT_ARRAY:
            return (self.read_int_array(), tag_type)
        elif tag_type == self.TAG_LONG_ARRAY:
            return (self.read_long_array(), tag_type)
        else:
            raise Exception(f"Unknown tag type: {tag_type}")
    
    def read_list(self) -> Tuple[List[Any], int]:
        """Membaca NBT List"""
        tag_type = self.read_byte()
        length = self.read_int()
        
        items = []
        for _ in range(length):
            value, _ = self.read_tag_payload(tag_type)
            # Simpan dengan informasi tipe untuk list items
            items.append(NBTValue(value, tag_type))
        
        return (items, self.TAG_LIST)
    
    def read_compound(self) -> Dict[str, Any]:
        """Membaca NBT Compound"""
        compound = {}
        
        while True:
            tag_type = self.read_byte()
            if tag_type == self.TAG_END:
                break
            
            tag_name = self.read_string()
            tag_value, value_type = self.read_tag_payload(tag_type)
            # Simpan dengan informasi tipe
            compound[tag_name] = NBTValue(tag_value, value_type)
        
        return compound
    
    def read_nbt(self) -> Dict[str, Any]:
        """Membaca file NBT lengkap"""
        self.data = self.read_file()
        self.position = 0
        
        # Membaca root compound
        tag_type = self.read_byte()
        if tag_type != self.TAG_COMPOUND:
            raise Exception(f"Expected compound tag at root, got {tag_type}")
        
        root_name = self.read_string()
        root_data = self.read_compound()
        
        return {root_name: root_data}

class NBTValue:
    """Class untuk menyimpan value NBT dengan informasi tipe"""
    
    def __init__(self, value: Any, nbt_type: int):
        self.value = value
        self.nbt_type = nbt_type
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"NBTValue({self.value}, type={self.nbt_type})"

class WorldDetector:
    """Class untuk mendeteksi lokasi world Minecraft Bedrock secara otomatis"""
    
    def __init__(self):
        self.system = platform.system()
    
    def get_minecraft_directories(self) -> List[str]:
        """Mendapatkan direktori Minecraft berdasarkan OS"""
        directories = []
        
        if self.system == "Windows":
            # Windows paths
            appdata = os.environ.get('LOCALAPPDATA', '')
            if appdata:
                directories.extend([
                    os.path.join(appdata, 'Packages', 'Microsoft.MinecraftUWP_8wekyb3d8bbwe', 'LocalState', 'games', 'com.mojang'),
                    os.path.join(appdata, 'Packages', 'Microsoft.MinecraftWindowsBeta_8wekyb3d8bbwe', 'LocalState', 'games', 'com.mojang'),
                    os.path.join(appdata, 'Packages', 'Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe', 'LocalState', 'games', 'com.mojang')
                ])
        
        elif self.system == "Darwin":  # macOS
            home = os.path.expanduser("~")
            directories.extend([
                os.path.join(home, 'Library', 'Application Support', 'mcpelauncher', 'games', 'com.mojang'),
                os.path.join(home, 'Library', 'Containers', 'com.microsoft.minecraftpe', 'Data', 'Library', 'Application Support', 'games', 'com.mojang')
            ])
        
        elif self.system == "Linux":
            home = os.path.expanduser("~")
            directories.extend([
                os.path.join(home, '.local', 'share', 'mcpelauncher', 'games', 'com.mojang'),
                os.path.join(home, 'snap', 'mcpelauncher', 'current', '.local', 'share', 'mcpelauncher', 'games', 'com.mojang'),
                # Android paths if running on Android subsystem
                '/storage/emulated/0/games/com.mojang',
                '/sdcard/games/com.mojang'
            ])
        
        # Tambahkan path lokal untuk development/testing
        current_dir = os.getcwd()
        directories.extend([
            os.path.join(current_dir, 'worlds'),
            os.path.join(current_dir, 'games', 'com.mojang', 'minecraftWorlds'),
            './worlds'
        ])
        
        return [d for d in directories if os.path.exists(d)]
    
    def find_worlds(self) -> List[Dict[str, str]]:
        """Mencari semua world yang tersedia"""
        worlds = []
        minecraft_dirs = self.get_minecraft_directories()
        
        print(f"Mencari world di {len(minecraft_dirs)} direktori...")
        
        for minecraft_dir in minecraft_dirs:
            worlds_dir = os.path.join(minecraft_dir, 'minecraftWorlds')
            if os.path.exists(worlds_dir):
                print(f"Memeriksa: {worlds_dir}")
                
                for world_folder in os.listdir(worlds_dir):
                    world_path = os.path.join(worlds_dir, world_folder)
                    level_dat_path = os.path.join(world_path, 'level.dat')
                    
                    if os.path.isdir(world_path) and os.path.exists(level_dat_path):
                        # Coba baca nama world dari levelname.txt
                        levelname_path = os.path.join(world_path, 'levelname.txt')
                        world_name = world_folder
                        
                        if os.path.exists(levelname_path):
                            try:
                                with open(levelname_path, 'r', encoding='utf-8') as f:
                                    world_name = f.read().strip()
                            except:
                                pass
                        
                        worlds.append({
                            'name': world_name,
                            'folder': world_folder,
                            'path': world_path,
                            'level_dat': level_dat_path
                        })
        
        return worlds

# Alias untuk backward compatibility
AccurateBedrockNBTReader = RawNBTReader
