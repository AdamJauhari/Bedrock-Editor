#!/usr/bin/env python3
"""
Test script untuk memverifikasi parser level.dat yang sudah ditingkatkan
"""

import os
import sys
import json
from bedrock_parser import BedrockParser
from nbt_utils import convert_to_json_format

def test_parser():
    """Test the improved BedrockParser with a level.dat file"""
    
    # Initialize parser
    parser = BedrockParser()
    
    # Common Minecraft level.dat keys for validation (not hardcoded specific values)
    common_keys = [
        'BiomeOverride', 'CenterMapsToOrigin', 'ConfirmedPlatformLockedContent',
        'Difficulty', 'FlatWorldLayers', 'ForceGameType', 'GameType', 'Generator',
        'HasUncompleteWorldFileOnDisk', 'InventoryVersion', 'IsHardcore',
        'LANBroadcast', 'LANBroadcastIntent', 'LastPlayed', 'LevelName',
        'LimitedWorldOriginX', 'LimitedWorldOriginY', 'LimitedWorldOriginZ',
        'MinimumCompatibleClientVersion', 'MultiplayerGame', 'MultiplayerGameIntent',
        'NetherScale', 'NetworkVersion', 'Platform', 'PlatformBroadcastIntent',
        'PlayerHasDied', 'RandomSeed', 'SpawnV1Villagers', 'SpawnX', 'SpawnY',
        'SpawnZ', 'StorageVersion', 'Time', 'WorldVersion', 'XBLBroadcastIntent',
        'abilities', 'baseGameVersion', 'bonusChestEnabled', 'bonusChestSpawned',
        'cheatsEnabled', 'commandblockoutput', 'commandblocksenabled',
        'commandsEnabled', 'currentTick', 'daylightCycle', 'dodaylightcycle',
        'doentitydrops', 'dofiretick', 'doimmediaterespawn', 'doinsomnia',
        'dolimitedcrafting', 'domobloot', 'domobspawning', 'dotiledrops',
        'doweathercycle', 'drowningdamage', 'editorWorldType', 'eduOffer',
        'educationFeaturesEnabled', 'experiments', 'falldamage', 'firedamage',
        'freezedamage', 'functioncommandlimit', 'hasBeenLoadedInCreative',
        'hasLockedBehaviorPack', 'hasLockedResourcePack', 'immutableWorld',
        'isCreatedInEditor', 'isExportedFromEditor', 'isFromLockedTemplate',
        'isFromWorldTemplate', 'isRandomSeedAllowed', 'isSingleUseWorld',
        'isWorldTemplateOptionLocked', 'keepinventory', 'lastOpenedWithVersion',
        'lightningLevel', 'lightningTime', 'limitedWorldDepth', 'limitedWorldWidth',
        'locatorbar', 'maxcommandchainlength', 'mobgriefing', 'naturalregeneration',
        'permissionsLevel', 'playerPermissionsLevel', 'playerssleepingpercentage',
        'prid', 'projectilescanbreakblocks', 'pvp', 'rainLevel', 'rainTime',
        'randomtickspeed', 'recipesunlock', 'requiresCopiedPackRemovalCheck',
        'respawnblocksexplode', 'sendcommandfeedback', 'serverChunkTickRange',
        'showbordereffect', 'showcoordinates', 'showdaysplayed', 'showdeathmessages',
        'showrecipemessages', 'showtags', 'spawnMobs', 'spawnradius',
        'startWithMapEnabled', 'texturePacksRequired', 'tntexplodes',
        'tntexplosiondropdecay', 'useMsaGamertagsOnly', 'worldStartCount',
        'world_policies'
    ]
    
    # Test with a sample level.dat file if available
    test_file = None
    
    # Look for level.dat in common locations
    possible_paths = [
        "level.dat",  # Current directory
        "test_level.dat",  # Test file
        os.path.expanduser("~/AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang/minecraftWorlds/*/level.dat"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_file = path
            break
        elif '*' in path:
            # Handle glob pattern
            import glob
            matches = glob.glob(path)
            if matches:
                test_file = matches[0]
                break
    
    if not test_file:
        print("❌ No level.dat file found for testing")
        print("Please place a level.dat file in the current directory or specify a path")
        return False
    
    print(f"🧪 Testing parser with: {test_file}")
    
    try:
        # Parse the file
        result = parser.parse_bedrock_level_dat_manual(test_file)
        
        if not result:
            print("❌ Parser returned empty result")
            return False
        
        print(f"✅ Parser successful! Found {len(result)} keys")
        
        # Convert to JSON format
        json_data = convert_to_json_format(result)
        
        # Check for common keys
        found_keys = set(result.keys())
        common_key_set = set(common_keys)
        
        missing_keys = common_key_set - found_keys
        extra_keys = found_keys - common_key_set
        
        print(f"\n📊 Key Analysis:")
        print(f"   Found: {len(found_keys)} keys")
        print(f"   Expected: {len(common_key_set)} keys")
        print(f"   Missing: {len(missing_keys)} keys")
        print(f"   Extra: {len(extra_keys)} keys")
        
        if missing_keys:
            print(f"\n❌ Missing keys: {sorted(missing_keys)}")
        
        if extra_keys:
            print(f"\n➕ Extra keys found: {sorted(extra_keys)}")
        
        # Check specific important keys
        important_keys = ['abilities', 'experiments', 'MinimumCompatibleClientVersion', 'lastOpenedWithVersion']
        for key in important_keys:
            if key in result:
                value = result[key]
                if isinstance(value, dict):
                    print(f"✅ {key}: {len(value)} entries")
                elif isinstance(value, list):
                    print(f"✅ {key}: {len(value)} items - {value}")
                else:
                    print(f"✅ {key}: {value}")
                else:
                print(f"❌ {key}: Missing")
        
        # Save result to JSON file for inspection
        output_file = "parsed_level_dat.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full result saved to: {output_file}")
        
        # Calculate success rate
        success_rate = len(found_keys.intersection(common_key_set)) / len(common_key_set) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 Excellent! Parser is working very well!")
            return True
        elif success_rate >= 70:
            print("👍 Good! Parser is working well with some improvements needed")
            return True
        else:
            print("⚠️  Parser needs improvement")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data():
    """Create a sample level.dat structure for testing"""
    sample_data = {
        "BiomeOverride": "minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:minecraft:",
        "CenterMapsToOrigin": 0,
        "ConfirmedPlatformLockedContent": 0,
        "Difficulty": 3,
        "FlatWorldLayers": "{\"biome_id\":1,\"block_layers\":[{\"block_name\":\"minecraft:bedrock\",\"count\":1},{\"block_name\":\"minecraft:dirt\",\"count\":2},{\"block_name\":\"minecraft:grass_block\",\"count\":1}],\"encoding_version\":6,\"preset_id\":\"ClassicFlat\",\"world_version\":\"version.post_1_18\"}",
        "ForceGameType": 0,
        "GameType": 0,
        "Generator": 1,
        "HasUncompleteWorldFileOnDisk": 0,
        "InventoryVersion": "1.21.81",
        "IsHardcore": 0,
        "LANBroadcast": 0,
        "LANBroadcastIntent": 1,
        "LastPlayed": 7541659355674836992,
        "LevelName": "Survival Season 3 (1)",
        "LimitedWorldOriginX": -8,
        "LimitedWorldOriginY": 32767,
        "LimitedWorldOriginZ": -1,
        "MinimumCompatibleClientVersion": [1, 21, 100, 0, 0],
        "MultiplayerGame": 0,
        "MultiplayerGameIntent": 0,
        "NetherScale": 8,
        "NetworkVersion": 800,
        "Platform": 2,
        "PlatformBroadcastIntent": 2,
        "PlayerHasDied": 1,
        "RandomSeed": -2748597270991879557,
        "SpawnV1Villagers": 0,
        "SpawnX": -8,
        "SpawnY": 32767,
        "SpawnZ": -1,
        "StorageVersion": 10,
        "Time": 62917478430277632,
        "WorldVersion": 1,
        "XBLBroadcastIntent": 3,
        "abilities": {
            "attackmobs": 1,
            "attackplayers": 1,
            "build": 1,
            "doorsandswitches": 1,
            "flySpeed": 0.05000000074505806,
            "flying": 0,
            "instabuild": 0,
            "invulnerable": 0,
            "lightning": 0,
            "mayfly": 0,
            "mine": 1,
            "op": 0,
            "opencontainers": 1,
            "teleport": 0,
            "verticalFlySpeed": 1.0,
            "walkSpeed": 0.10000000149011612
        },
        "baseGameVersion": "*",
        "bonusChestEnabled": 0,
        "bonusChestSpawned": 0,
        "cheatsEnabled": 0,
        "commandblockoutput": 1,
        "commandblocksenabled": 1,
        "commandsEnabled": 0,
        "currentTick": 51438448187277312,
        "daylightCycle": 0,
        "dodaylightcycle": 1,
        "doentitydrops": 1,
        "dofiretick": 1,
        "doimmediaterespawn": 1,
        "doinsomnia": 1,
        "dolimitedcrafting": 0,
        "domobloot": 1,
        "domobspawning": 1,
        "dotiledrops": 1,
        "doweathercycle": 1,
        "drowningdamage": 1,
        "editorWorldType": 0,
        "eduOffer": 0,
        "educationFeaturesEnabled": 0,
        "experiments": {
            "data_driven_biomes": 1,
            "experimental_creator_cameras": 1,
            "experiments_ever_used": 1,
            "gametest": 1,
            "jigsaw_structures": 1,
            "saved_with_toggled_experiments": 1,
            "upcoming_creator_features": 1,
            "villager_trades_rebalance": 1,
            "y_2025_drop_3": 1
        },
        "falldamage": 1,
        "firedamage": 1,
        "freezedamage": 1,
        "functioncommandlimit": 10000,
        "hasBeenLoadedInCreative": 1,
        "hasLockedBehaviorPack": 0,
        "hasLockedResourcePack": 0,
        "immutableWorld": 0,
        "isCreatedInEditor": 0,
        "isExportedFromEditor": 0,
        "isFromLockedTemplate": 0,
        "isFromWorldTemplate": 0,
        "isRandomSeedAllowed": 0,
        "isSingleUseWorld": 0,
        "isWorldTemplateOptionLocked": 0,
        "keepinventory": 0,
        "lastOpenedWithVersion": [1, 21, 101, 1, 0],
        "lightningLevel": 0.0,
        "lightningTime": 44500,
        "limitedWorldDepth": 16,
        "limitedWorldWidth": 16,
        "locatorbar": 1,
        "maxcommandchainlength": 65535,
        "mobgriefing": 1,
        "naturalregeneration": 1,
        "permissionsLevel": 0,
        "playerPermissionsLevel": 1,
        "playerssleepingpercentage": 20,
        "prid": "",
        "projectilescanbreakblocks": 1,
        "pvp": 0,
        "rainLevel": 0.0,
        "rainTime": 56933,
        "randomtickspeed": 1,
        "recipesunlock": 1,
        "requiresCopiedPackRemovalCheck": 0,
        "respawnblocksexplode": 1,
        "sendcommandfeedback": 1,
        "serverChunkTickRange": 6,
        "showbordereffect": 1,
        "showcoordinates": 1,
        "showdaysplayed": 1,
        "showdeathmessages": 1,
        "showrecipemessages": 1,
        "showtags": 1,
        "spawnMobs": 1,
        "spawnradius": 16,
        "startWithMapEnabled": 0,
        "texturePacksRequired": 1,
        "tntexplodes": 1,
        "tntexplosiondropdecay": 0,
        "useMsaGamertagsOnly": 0,
        "worldStartCount": -781684047872,
        "world_policies": {}
    }
    
    # Convert to JSON format
    json_data = convert_to_json_format(sample_data)
    
    # Save sample data
    with open("sample_level_dat.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print("📝 Sample data created: sample_level_dat.json")

if __name__ == "__main__":
    print("🧪 Bedrock Parser Test Suite")
    print("=" * 50)
    
    # Create sample data first
    create_sample_data()
    
    # Test the parser
    success = test_parser()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
