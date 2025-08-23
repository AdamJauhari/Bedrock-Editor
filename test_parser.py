#!/usr/bin/env python3
"""
Test script untuk memverifikasi dynamic parser
"""

import os
from bedrock_parser import BedrockParser
from minecraft_paths import MINECRAFT_WORLDS_PATH

def test_parser():
    """Test dynamic parser dengan file level.dat yang ada"""
    parser = BedrockParser()
    
    print("🔍 Testing Dynamic NBT Parser...")
    print(f"📁 Minecraft worlds path: {MINECRAFT_WORLDS_PATH}")
    
    if not os.path.exists(MINECRAFT_WORLDS_PATH):
        print("❌ Minecraft worlds path tidak ditemukan")
        return
    
    # Cari world pertama yang ada
    worlds = os.listdir(MINECRAFT_WORLDS_PATH)
    if not worlds:
        print("❌ Tidak ada world yang ditemukan")
        return
    
    test_world = worlds[0]
    world_path = os.path.join(MINECRAFT_WORLDS_PATH, test_world)
    level_dat = os.path.join(world_path, "level.dat")
    
    print(f"🎮 Testing dengan world: {test_world}")
    print(f"📄 File: {level_dat}")
    
    if not os.path.exists(level_dat):
        print("❌ level.dat tidak ditemukan")
        return
    
    # Test parser
    try:
        print("\n🚀 Memulai parsing...")
        result = parser.parse_bedrock_level_dat_manual(level_dat)
        
        if result and len(result) > 0:
            print(f"\n✅ Parser berhasil! Ditemukan {len(result)} keys:")
            print("=" * 50)
            
            # Tampilkan semua keys yang ditemukan
            for i, (key, value) in enumerate(result.items(), 1):
                if isinstance(value, dict):
                    print(f"{i:2d}. {key}: {len(value)} entries")
                elif isinstance(value, list):
                    print(f"{i:2d}. {key}: {len(value)} items")
                else:
                    print(f"{i:2d}. {key}: {value}")
            
            print("=" * 50)
            print(f"📊 Total keys detected: {len(result)}")
            
            # Cek apakah ada key baru yang biasanya tidak terdeteksi
            new_keys = ['experiments', 'abilities', 'world_policies', 'MinimumCompatibleClientVersion']
            found_new = [key for key in new_keys if key in result]
            if found_new:
                print(f"🎉 Key baru yang terdeteksi: {found_new}")
            else:
                print("ℹ️ Tidak ada key baru yang terdeteksi dalam test ini")
                
        else:
            print("❌ Parser gagal - tidak ada data yang ditemukan")
            
    except Exception as e:
        print(f"❌ Error saat parsing: {e}")

if __name__ == "__main__":
    test_parser()
