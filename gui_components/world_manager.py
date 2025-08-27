"""
World Manager
Handles Minecraft world loading and management
"""

import os
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from resource import MINECRAFT_WORLDS_PATH
from .world_list_components import WorldListComponents
from .styling_components import StylingComponents
from .message_box_components import MessageBoxComponents

class WorldManager:
    """Manages Minecraft world loading and selection"""
    
    def __init__(self, world_list_widget, main_window):
        self.world_list = world_list_widget
        self.main_window = main_window
    
    def load_worlds(self):
        """Load Minecraft worlds from the worlds directory"""
        self.world_list.clear()
        if os.path.exists(MINECRAFT_WORLDS_PATH):
            try:
                for folder in os.listdir(MINECRAFT_WORLDS_PATH):
                    world_path = os.path.join(MINECRAFT_WORLDS_PATH, folder)
                    level_dat = os.path.join(world_path, "level.dat")
                    levelname_txt = os.path.join(world_path, "levelname.txt")
                    icon_path = os.path.join(world_path, "world_icon.png")
                    
                    if not os.path.exists(icon_path):
                        icon_path = os.path.join(world_path, "icon.png")
                    if not os.path.exists(icon_path):
                        icon_path = os.path.join(world_path, "world_icon.jpeg")
                    
                    world_name = folder
                    
                    # Try to get name from levelname.txt
                    if os.path.exists(levelname_txt):
                        try:
                            with open(levelname_txt, "r", encoding="utf-8") as f:
                                txt_name = f.read().strip()
                                if txt_name:
                                    world_name = txt_name
                        except Exception:
                            pass
                    
                    # Create widget custom untuk world
                    item_widget = WorldListComponents.create_world_list_item(world_name, icon_path, world_path)
                    
                    # Tambahkan ke QListWidget
                    item = QListWidgetItem()
                    item.setSizeHint(item_widget.sizeHint())
                    item.setData(Qt.UserRole, {"type": "real", "path": world_path})
                    self.world_list.addItem(item)
                    self.world_list.setItemWidget(item, item_widget)
                    
            except PermissionError:
                print("⚠️ Permission denied accessing Minecraft worlds")
                # Add permission error item
                error_item = QListWidgetItem("🔒 Permission Denied")
                error_item.setData(Qt.UserRole, {"type": "error", "path": "permission"})
                self.world_list.addItem(error_item)
        else:
            print("⚠️ Minecraft worlds path not found")
            # Add not found item
            not_found_item = QListWidgetItem("❌ Worlds Not Found")
            not_found_item.setData(Qt.UserRole, {"type": "error", "path": "not_found"})
            self.world_list.addItem(not_found_item)
    
    def on_world_selected(self, item):
        """Handle world selection"""
        item_data = item.data(Qt.UserRole)
        if not item_data:
            return
            
        item_type = item_data.get("type")
        
        if item_type == "error":
            msg = QMessageBox(self.main_window)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Access Error")
            msg.setText("Cannot access Minecraft worlds.\n\nPlease run as administrator or check file permissions.")
            msg.setStyleSheet(MessageBoxComponents.get_warning_message_box_style())
            msg.exec_()
            return
        
        # Set flag immediately to prevent any itemChanged signals during world loading
        self.main_window.is_programmatic_change = True
        
        # Clear current data and state before loading new world
        self.main_window.clear_current_data()
        
        world_path = item_data.get("path")
        level_dat = os.path.join(world_path, "level.dat")
        
        if os.path.exists(level_dat):
            # Check file size first
            file_size = os.path.getsize(level_dat)
            if file_size < 100:  # File terlalu kecil
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"File level.dat terlalu kecil ({file_size} bytes). File mungkin kosong atau rusak.")
                msg.setStyleSheet(MessageBoxComponents.get_error_message_box_style())
                msg.exec_()
                self.main_window.is_programmatic_change = False
                return
            
            self.main_window.nbt_file = level_dat
            try:
                # Try custom NBT parser first
                print(f"Loading {level_dat} with custom NBT parser...")
                self.main_window.nbt_reader = self.main_window.nbt_reader_class()
                self.main_window.nbt_data = self.main_window.nbt_reader.read_nbt_file(level_dat)
                
                # If custom parser returns empty data, try nbtlib as fallback
                if not self.main_window.nbt_data or len(self.main_window.nbt_data) == 0:
                    print("⚠️ Custom parser returned empty data, trying nbtlib...")
                    import nbtlib
                    
                    # Try uncompressed first (Bedrock Edition)
                    try:
                        nbt_data = nbtlib.load(level_dat, gzipped=False)
                        print("✅ Successfully loaded with nbtlib (uncompressed)")
                    except Exception as e1:
                        print(f"⚠️ Failed to load as uncompressed: {e1}")
                        # Try gzipped (Java Edition)
                        try:
                            nbt_data = nbtlib.load(level_dat, gzipped=True)
                            print("✅ Successfully loaded with nbtlib (gzipped)")
                        except Exception as e2:
                            print(f"❌ Failed to load with nbtlib: {e2}")
                            raise Exception(f"Failed to load with both methods: uncompressed ({e1}), gzipped ({e2})")
                    
                    if hasattr(nbt_data, 'root'):
                        self.main_window.nbt_data = dict(nbt_data.root)
                    else:
                        self.main_window.nbt_data = dict(nbt_data)
                    
                    # Create a simple structure for nbtlib data
                    self.main_window.nbt_reader = None
                    print(f"✅ Successfully loaded with nbtlib: {len(self.main_window.nbt_data)} keys")
                else:
                    print(f"✅ Successfully loaded with custom parser: {len(self.main_window.nbt_data)} keys")
                
                # Clear any previous search results
                self.main_window.search_utils.clear_search()
                
                # Populate tree with NBT structure
                self.main_window.populate_tree(self.main_window.nbt_data)
                
            except Exception as e:
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka level.dat: {e}")
                msg.setStyleSheet(MessageBoxComponents.get_error_message_box_style())
                msg.exec_()
            finally:
                # Always reset flag regardless of success or failure
                self.main_window.is_programmatic_change = False
