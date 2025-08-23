import struct
import re

class BedrockParser:
    """Manual parser untuk Bedrock level.dat dengan pattern matching dan NBT parsing"""
    
    def parse_bedrock_level_dat_manual(self, file_path):
        """
        Hybrid parser untuk Bedrock level.dat dengan pattern matching dan NBT parsing
        """
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            print(f"Using hybrid parsing approach for {len(data)} bytes")
            
            result = {}
            
            # Define all known level.dat fields dengan expected types
            level_dat_fields = {
                # String fields
                'BiomeOverride': ('string', r'BiomeOverride'),
                'FlatWorldLayers': ('string', r'FlatWorldLayers'), 
                'InventoryVersion': ('string', r'InventoryVersion'),
                'LevelName': ('string', r'LevelName'),
                'baseGameVersion': ('string', r'baseGameVersion'),
                'prid': ('string', r'prid'),
                
                # Additional fields from the correct structure
                'HasUncompleteWorldFileOnDisk': ('byte', r'HasUncompleteWorldFileOnDisk'),
                'locatorbar': ('byte', r'locatorbar'),
                
                # Byte fields (0 atau 1)
                'CenterMapsToOrigin': ('byte', r'CenterMapsToOrigin'),
                'ConfirmedPlatformLockedContent': ('byte', r'ConfirmedPlatformLockedContent'),
                'ForceGameType': ('byte', r'ForceGameType'),
                'IsHardcore': ('byte', r'IsHardcore'),
                'LANBroadcast': ('byte', r'LANBroadcast'),
                'LANBroadcastIntent': ('byte', r'LANBroadcastIntent'),
                'MultiplayerGame': ('byte', r'MultiplayerGame'),
                'MultiplayerGameIntent': ('byte', r'MultiplayerGameIntent'),
                'PlayerHasDied': ('byte', r'PlayerHasDied'),
                'SpawnV1Villagers': ('byte', r'SpawnV1Villagers'),
                'bonusChestEnabled': ('byte', r'bonusChestEnabled'),
                'bonusChestSpawned': ('byte', r'bonusChestSpawned'),
                'cheatsEnabled': ('byte', r'cheatsEnabled'),
                'commandblockoutput': ('byte', r'commandblockoutput'),
                'commandblocksenabled': ('byte', r'commandblocksenabled'),
                'commandsEnabled': ('byte', r'commandsEnabled'),
                'dodaylightcycle': ('byte', r'dodaylightcycle'),
                'doentitydrops': ('byte', r'doentitydrops'),
                'dofiretick': ('byte', r'dofiretick'),
                'doimmediaterespawn': ('byte', r'doimmediaterespawn'),
                'doinsomnia': ('byte', r'doinsomnia'),
                'dolimitedcrafting': ('byte', r'dolimitedcrafting'),
                'domobloot': ('byte', r'domobloot'),
                'domobspawning': ('byte', r'domobspawning'),
                'dotiledrops': ('byte', r'dotiledrops'),
                'doweathercycle': ('byte', r'doweathercycle'),
                'drowningdamage': ('byte', r'drowningdamage'),
                'educationFeaturesEnabled': ('byte', r'educationFeaturesEnabled'),
                'falldamage': ('byte', r'falldamage'),
                'firedamage': ('byte', r'firedamage'),
                'freezedamage': ('byte', r'freezedamage'),
                'hasBeenLoadedInCreative': ('byte', r'hasBeenLoadedInCreative'),
                'hasLockedBehaviorPack': ('byte', r'hasLockedBehaviorPack'),
                'hasLockedResourcePack': ('byte', r'hasLockedResourcePack'),
                'immutableWorld': ('byte', r'immutableWorld'),
                'isCreatedInEditor': ('byte', r'isCreatedInEditor'),
                'isExportedFromEditor': ('byte', r'isExportedFromEditor'),
                'isFromLockedTemplate': ('byte', r'isFromLockedTemplate'),
                'isFromWorldTemplate': ('byte', r'isFromWorldTemplate'),
                'isRandomSeedAllowed': ('byte', r'isRandomSeedAllowed'),
                'isSingleUseWorld': ('byte', r'isSingleUseWorld'),
                'isWorldTemplateOptionLocked': ('byte', r'isWorldTemplateOptionLocked'),
                'keepinventory': ('byte', r'keepinventory'),
                'mobgriefing': ('byte', r'mobgriefing'),
                'naturalregeneration': ('byte', r'naturalregeneration'),
                'projectilescanbreakblocks': ('byte', r'projectilescanbreakblocks'),
                'pvp': ('byte', r'pvp'),
                'recipesunlock': ('byte', r'recipesunlock'),
                'requiresCopiedPackRemovalCheck': ('byte', r'requiresCopiedPackRemovalCheck'),
                'respawnblocksexplode': ('byte', r'respawnblocksexplode'),
                'sendcommandfeedback': ('byte', r'sendcommandfeedback'),
                'showbordereffect': ('byte', r'showbordereffect'),
                'showcoordinates': ('byte', r'showcoordinates'),
                'showdaysplayed': ('byte', r'showdaysplayed'),
                'showdeathmessages': ('byte', r'showdeathmessages'),
                'showrecipemessages': ('byte', r'showrecipemessages'),
                'showtags': ('byte', r'showtags'),
                'spawnMobs': ('byte', r'spawnMobs'),
                'startWithMapEnabled': ('byte', r'startWithMapEnabled'),
                'texturePacksRequired': ('byte', r'texturePacksRequired'),
                'tntexplodes': ('byte', r'tntexplodes'),
                'tntexplosiondropdecay': ('byte', r'tntexplosiondropdecay'),
                'useMsaGamertagsOnly': ('byte', r'useMsaGamertagsOnly'),
                
                # Integer fields
                'Difficulty': ('int', r'Difficulty'),
                'GameType': ('int', r'GameType'),
                'Generator': ('int', r'Generator'),
                'LimitedWorldOriginX': ('int', r'LimitedWorldOriginX'),
                'LimitedWorldOriginY': ('int', r'LimitedWorldOriginY'),
                'LimitedWorldOriginZ': ('int', r'LimitedWorldOriginZ'),
                'NetherScale': ('int', r'NetherScale'),
                'NetworkVersion': ('int', r'NetworkVersion'),
                'Platform': ('int', r'Platform'),
                'PlatformBroadcastIntent': ('int', r'PlatformBroadcastIntent'),
                'SpawnX': ('int', r'SpawnX'),
                'SpawnY': ('int', r'SpawnY'),
                'SpawnZ': ('int', r'SpawnZ'),
                'StorageVersion': ('int', r'StorageVersion'),
                'WorldVersion': ('int', r'WorldVersion'),
                'XBLBroadcastIntent': ('int', r'XBLBroadcastIntent'),
                'daylightCycle': ('int', r'daylightCycle'),
                'editorWorldType': ('int', r'editorWorldType'),
                'eduOffer': ('int', r'eduOffer'),
                'functioncommandlimit': ('int', r'functioncommandlimit'),
                'lightningTime': ('int', r'lightningTime'),
                'limitedWorldDepth': ('int', r'limitedWorldDepth'),
                'limitedWorldWidth': ('int', r'limitedWorldWidth'),
                'maxcommandchainlength': ('int', r'maxcommandchainlength'),
                'permissionsLevel': ('int', r'permissionsLevel'),
                'playerPermissionsLevel': ('int', r'playerPermissionsLevel'),
                'playerssleepingpercentage': ('int', r'playerssleepingpercentage'),
                'rainTime': ('int', r'rainTime'),
                'randomtickspeed': ('int', r'randomtickspeed'),
                'serverChunkTickRange': ('int', r'serverChunkTickRange'),
                'spawnradius': ('int', r'spawnradius'),
                
                # Long fields  
                'LastPlayed': ('long', r'LastPlayed'),
                'RandomSeed': ('long', r'RandomSeed'),
                'Time': ('long', r'Time'),
                'currentTick': ('long', r'currentTick'),
                'worldStartCount': ('long', r'worldStartCount'),
                
                # Float fields
                'lightningLevel': ('float', r'lightningLevel'),
                'rainLevel': ('float', r'rainLevel'),
            }
            
            # Parse each field
            for field_name, (field_type, pattern) in level_dat_fields.items():
                field_bytes = pattern.encode('utf-8')
                pos = data.find(field_bytes)
                
                if pos > 0:
                    try:
                        value_pos = pos + len(field_bytes)
                        value = self._extract_value_by_type(data, value_pos, field_type)
                        if value is not None:
                            result[field_name] = value
                    except Exception:
                        continue
            
            # Try to parse compound fields (nested structures)
            compound_fields = ['abilities', 'experiments', 'world_policies', 
                             'MinimumCompatibleClientVersion', 'lastOpenedWithVersion']
            
            for compound_name in compound_fields:
                compound_bytes = compound_name.encode('utf-8')
                pos = data.find(compound_bytes)
                if pos > 0:
                    try:
                        # Try to parse as compound after the name
                        value_pos = pos + len(compound_bytes)
                        compound_data = self._try_parse_compound_at(data, value_pos)
                        if compound_data:
                            result[compound_name] = compound_data
                            print(f"✅ Parsed compound: {compound_name}")
                    except Exception as e:
                        print(f"❌ Failed to parse compound {compound_name}: {e}")
                        continue
            
            # Disable problematic auto-detection for now
            # Focus on reliable parsing with known libraries
            print("ℹ️ Using reliable NBT parsing only")
            
            print(f"Hybrid parser extracted {len(result)} fields from level.dat")
            return result
            
        except Exception as e:
            print(f"Hybrid parser failed: {e}")
            return {}
    
    def _extract_value_by_type(self, data, pos, field_type):
        """Extract value dengan tipe yang diharapkan dari posisi data"""
        try:
            if field_type == 'string':
                # Cari string length (berbagai kemungkinan format)
                for offset in [0, 1, 2, 3, 4]:
                    try:
                        if pos + offset + 2 <= len(data):
                            str_len = struct.unpack('<H', data[pos+offset:pos+offset+2])[0]
                            if 1 <= str_len <= 10000:  # Reasonable string length
                                str_start = pos + offset + 2
                                if str_start + str_len <= len(data):
                                    value = data[str_start:str_start+str_len].decode('utf-8', errors='replace')
                                    if len(value.strip()) > 0:  # Non-empty string
                                        return value
                    except:
                        continue
                        
            elif field_type == 'byte':
                # Try different offsets for byte values
                for offset in [0, 1, 2, 3, 4]:
                    if pos + offset < len(data):
                        value = data[pos + offset]
                        if value in [0, 1]:  # Boolean byte values
                            return value
                        
            elif field_type == 'int':
                # Try different offsets for 4-byte integers
                for offset in [0, 1, 2, 3, 4]:
                    if pos + offset + 4 <= len(data):
                        try:
                            value = struct.unpack('<i', data[pos+offset:pos+offset+4])[0]
                            if -2147483648 <= value <= 2147483647:  # Valid int range
                                return value
                        except:
                            continue
                            
            elif field_type == 'long':
                # Try different offsets for 8-byte long values
                for offset in [0, 1, 2, 3, 4, 8, 12]:
                    if pos + offset + 8 <= len(data):
                        try:
                            value = struct.unpack('<q', data[pos+offset:pos+offset+8])[0]
                            return value
                        except:
                            continue
                            
            elif field_type == 'float':
                # Try different offsets for 4-byte float values
                for offset in [0, 1, 2, 3, 4]:
                    if pos + offset + 4 <= len(data):
                        try:
                            value = struct.unpack('<f', data[pos+offset:pos+offset+4])[0]
                            if not (value != value):  # Not NaN
                                return value
                        except:
                            continue
            
            return None
            
        except Exception:
            return None
    
    def _try_parse_compound_at(self, data, pos):
        """Coba parse compound/array data di posisi tertentu"""
        try:
            # Coba parse sebagai list integer (untuk version arrays)
            if pos + 4 <= len(data):
                try:
                    list_len = struct.unpack('<i', data[pos:pos+4])[0]
                    if 1 <= list_len <= 10:  # Reasonable list length for version arrays
                        pos += 4
                        result = []
                        for i in range(list_len):
                            if pos + 4 <= len(data):
                                value = struct.unpack('<i', data[pos:pos+4])[0]
                                result.append(value)
                                pos += 4
                            else:
                                break
                        if len(result) == list_len:
                            return result
                except:
                    pass
            
            # Coba parse sebagai compound dengan fields yang benar
            result_dict = {}
            
            # Look for abilities fields based on correct structure
            abilities_fields = {
                'attackmobs': 'byte',
                'attackplayers': 'byte', 
                'build': 'byte',
                'doorsandswitches': 'byte',
                'flying': 'byte',
                'instabuild': 'byte',
                'invulnerable': 'byte',
                'lightning': 'byte',
                'mayfly': 'byte',
                'mine': 'byte',
                'op': 'byte',
                'opencontainers': 'byte',
                'teleport': 'byte',
                'flySpeed': 'float',
                'walkSpeed': 'float',
                'verticalFlySpeed': 'float'
            }
            
            # Look for experiments fields
            experiments_fields = {
                'data_driven_biomes': 'byte',
                'experiments_ever_used': 'byte',
                'gametest': 'byte',
                'jigsaw_structures': 'byte',
                'saved_with_toggled_experiments': 'byte'
            }
            
            # Search for fields in the compound
            search_range = min(pos + 500, len(data))  # Look in a reasonable range
            
            for field, field_type in abilities_fields.items():
                field_bytes = field.encode('utf-8')
                field_pos = data.find(field_bytes, pos, search_range)
                if field_pos > 0:
                    value_pos = field_pos + len(field_bytes)
                    if field_type == 'byte':
                        # Try to get byte value
                        for offset in [0, 1, 2, 3]:
                            if value_pos + offset < len(data):
                                value = data[value_pos + offset]
                                if value in [0, 1]:
                                    result_dict[field] = value
                                    break
                    elif field_type == 'float':
                        # Try to get float value
                        for offset in [0, 1, 2, 3, 4]:
                            if value_pos + offset + 4 <= len(data):
                                try:
                                    value = struct.unpack('<f', data[value_pos+offset:value_pos+offset+4])[0]
                                    if not (value != value):  # Not NaN
                                        result_dict[field] = value
                                        break
                                except:
                                    continue
            
            # Search for experiments fields
            for field, field_type in experiments_fields.items():
                field_bytes = field.encode('utf-8')
                field_pos = data.find(field_bytes, pos, search_range)
                if field_pos > 0:
                    value_pos = field_pos + len(field_bytes)
                    if field_type == 'byte':
                        for offset in [0, 1, 2, 3]:
                            if value_pos + offset < len(data):
                                value = data[value_pos + offset]
                                if value in [0, 1]:
                                    result_dict[field] = value
                                    break
            
            return result_dict if len(result_dict) > 0 else None
            
        except Exception as e:
            print(f"Error parsing compound: {e}")
            return None
