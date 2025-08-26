#!/usr/bin/env python3
"""
Bedrock NBT/DAT Editor - No Admin Version
Runs without requiring administrator privileges for development and testing
"""

import sys
import os
import shutil
import json

# Import our separated modules
from package_manager import *
from minecraft_paths import MINECRAFT_WORLDS_PATH
from nbt_reader.bedrock_nbt_parser import BedrockNBTParser as NBTReader
from search_utils import SearchUtils
from gui_components import GUIComponents

# Additional imports needed for the main app
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QHeaderView,
    QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor, QPainter, QFont

class CustomBranchDelegate(QStyledItemDelegate):
    """Custom delegate to draw arrow symbols for tree branches"""
    
    def paint(self, painter, option, index):
        # Call parent paint method first
        super().paint(painter, option, index)
        
        # Only paint for the first column (type column)
        if index.column() == 0:
            tree_widget = self.parent()
            if tree_widget:
                item = tree_widget.itemFromIndex(index)
                if item and item.childCount() > 0:
                    # Draw arrow symbol
                    painter.save()
                    painter.setPen(QColor("#00bfff"))
                    font = QFont("Segoe UI", 12, QFont.Bold)
                    painter.setFont(font)
                    
                    # Position for arrow - move to the left to avoid collision with type
                    rect = option.rect
                    x = rect.x() - 20  # Move further left to avoid type column
                    y = rect.y() + rect.height() // 2 + 4
                    
                    # Draw arrow based on expanded state
                    if item.isExpanded():
                        painter.drawText(x, y, "▼")
                    else:
                        painter.drawText(x, y, "▶")
                    
                    painter.restore()

class NBTEditorNoAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Skip admin privileges check
        print("🔧 Running in No-Admin Mode (Development/Testing)")
        print("⚠️ Some features may be limited without administrator access")
        
        self.setWindowTitle("Bedrock NBT/DAT Editor - No Admin Mode")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.png"))
        self.nbt_file = None
        self.nbt_data = None
        self.nbt_reader = None
        self.search_results = []
        
        # Timer for search debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_live_search)
        
        # Flag to prevent itemChanged signal during search/programmatic changes
        self.is_programmatic_change = False
        
        self.init_ui()
        
        # Initialize search utilities after UI is created
        self.search_utils = SearchUtils(self.tree, self.search_input, self.search_status, self.search_timer, self)
        
        # Connect search input to search utils
        self.search_input.textChanged.connect(self.search_utils.on_search_text_changed)
        
        # Load worlds (will show limited access message)
        self.load_worlds()
        
        # Connect world selection
        self.world_list.itemClicked.connect(self.on_world_selected)
        
        # Connect table item editing
        self.tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        self.tree.itemChanged.connect(self.on_item_changed)
        
        print("✅ NBT Editor (No Admin) initialized successfully")

    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout()
        
        # Left panel for world list
        left_panel = QVBoxLayout()
        
        # World list label
        world_label = QLabel("Minecraft Worlds:")
        world_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff; margin-bottom: 10px;")
        left_panel.addWidget(world_label)
        
        # Admin mode warning
        admin_warning = QLabel("⚠️ No Admin Mode - Limited Access")
        admin_warning.setStyleSheet("""
            color: #ff9500;
            font-size: 12px;
            font-weight: bold;
            padding: 8px;
            background-color: rgba(255, 149, 0, 0.1);
            border: 1px solid rgba(255, 149, 0, 0.3);
            border-radius: 6px;
            margin-bottom: 10px;
        """)
        left_panel.addWidget(admin_warning)
        
        # World list widget
        self.world_list = QListWidget()
        self.world_list.setMaximumWidth(300)
        self.world_list.setMinimumWidth(250)
        self.world_list.setStyleSheet(GUIComponents.get_world_list_style())
        left_panel.addWidget(self.world_list)
        
        # Add left panel to main layout with stretch factor
        main_layout.addLayout(left_panel, 1)  # 1 = minimum space
        
        # Center panel for tree view
        center_layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #ffffff; margin-right: 10px;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search NBT data...")
        self.search_input.setStyleSheet(GUIComponents.get_search_input_style())
        search_layout.addWidget(self.search_input)
        
        self.search_status = QLabel("")
        self.search_status.setStyleSheet("color: #888888; margin-left: 10px;")
        search_layout.addWidget(self.search_status)
        
        center_layout.addLayout(search_layout)
        
        # Tree widget for NBT data
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Type", "Nama", "Value"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet(GUIComponents.get_tree_widget_style())
        
        # Set column widths with stretch factors for responsive layout
        self.tree.setColumnWidth(0, 80)   # Type column (fixed width)
        self.tree.setColumnWidth(1, 300)  # Nama column (initial width)
        self.tree.setColumnWidth(2, 400)  # Value column (initial width)
        
        # Set stretch factors for responsive columns
        self.tree.header().setStretchLastSection(True)  # Value column stretches
        self.tree.header().setSectionResizeMode(0, QHeaderView.Fixed)  # Type fixed
        self.tree.header().setSectionResizeMode(1, QHeaderView.Interactive)  # Nama interactive
        self.tree.header().setSectionResizeMode(2, QHeaderView.Stretch)  # Value stretches
        
        # Set tree properties
        self.tree.setSelectionBehavior(QTreeWidget.SelectRows)
        self.tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        
        # Set custom delegate for branch indicators
        self.tree.setItemDelegateForColumn(0, CustomBranchDelegate(self.tree))
        
        center_layout.addWidget(self.tree)
        main_layout.addLayout(center_layout, 4)  # 4 = most space for table
        
        # Right panel for actions
        right_panel = QVBoxLayout()
        
        # Action buttons
        open_button = QPushButton("Open File")
        open_button.clicked.connect(self.open_file)
        open_button.setStyleSheet(GUIComponents.get_button_style())
        right_panel.addWidget(open_button)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_file)
        save_button.setStyleSheet(GUIComponents.get_button_style())
        right_panel.addWidget(save_button)
        
        export_button = QPushButton("Export JSON")
        export_button.clicked.connect(self.export_to_json)
        export_button.setStyleSheet(GUIComponents.get_button_style())
        right_panel.addWidget(export_button)
        
        # Demo data button for testing
        demo_button = QPushButton("Load Demo Data")
        demo_button.clicked.connect(self.load_demo_data)
        demo_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9500;
                color: white;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 2px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6850e;
            }
            QPushButton:pressed {
                background-color: #cc7700;
            }
        """)
        right_panel.addWidget(demo_button)
        
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 1)  # 1 = minimum space for buttons
        
        central_widget.setLayout(main_layout)
        self.setStyleSheet("background-color: #181a20;")

    def clear_current_data(self):
        """Clear current data and reset state"""
        try:
            print("🧹 Clearing current data and state...")
            
            # Clear tree widget
            self.tree.clear()
            
            # Clear search results
            if hasattr(self, 'search_utils'):
                self.search_utils.clear_search()
            
            # Reset data references
            self.nbt_data = None
            self.nbt_file = None
            self.nbt_reader = None
            
            # Reset window title
            self.setWindowTitle("Bedrock NBT/DAT Editor - No Admin Mode")
            
            # Clear any pending operations
            if hasattr(self, 'search_timer') and self.search_timer.isActive():
                self.search_timer.stop()
            
            print("✅ Current data cleared successfully")
            
        except Exception as e:
            print(f"❌ Error clearing current data: {e}")

    def load_worlds(self):
        """Load Minecraft worlds from the worlds directory"""
        self.world_list.clear()
        
        # Add demo world for testing
        demo_item = QListWidgetItem("🌍 Demo World (Testing)")
        demo_item.setData(Qt.UserRole, {"type": "demo", "path": "demo"})
        self.world_list.addItem(demo_item)
        
        # Try to load real worlds if accessible
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
                    item_widget = GUIComponents.create_world_list_item(world_name, icon_path, world_path)
                    
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

    def load_demo_data(self):
        """Load demo data for testing without admin access"""
        print("🎮 Loading demo data for testing...")
        
        # Create demo NBT data
        demo_data = {
            "LevelName": "Demo World",
            "GameType": 0,
            "Generator": 1,
            "LastPlayed": 1234567890,
            "SizeOnDisk": 1024000,
            "RandomSeed": 12345,
            "SpawnX": 0,
            "SpawnY": 64,
            "SpawnZ": 0,
            "Time": 1000,
            "DayTime": 6000,
            "GameRules": {
                "doFireTick": True,
                "doMobSpawning": True,
                "doTileDrops": True,
                "keepInventory": False,
                "naturalRegeneration": True
            },
            "abilities": {
                "flying": False,
                "instabuild": False,
                "invulnerable": False,
                "mayfly": False,
                "walking": True
            }
        }
        
        self.nbt_data = demo_data
        self.nbt_file = "demo_data.json"
        self.nbt_reader = None  # Use nbtlib fallback
        
        # Clear any previous search results
        self.search_utils.clear_search()
        
        # Populate tree with demo data
        self.populate_tree(self.nbt_data)
        
        # Update window title
        self.setWindowTitle("Bedrock NBT/DAT Editor - No Admin Mode - Demo Data")
        
        print("✅ Demo data loaded successfully")

    def on_world_selected(self, item):
        """Handle world selection"""
        item_data = item.data(Qt.UserRole)
        if not item_data:
            return
            
        item_type = item_data.get("type")
        
        if item_type == "demo":
            self.load_demo_data()
            return
        elif item_type == "error":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Access Denied")
            msg.setText("Cannot access Minecraft worlds without administrator privileges.\n\nUse 'Load Demo Data' button for testing.")
            msg.setStyleSheet(GUIComponents.get_warning_message_box_style())
            msg.exec_()
            return
        
        # Set flag immediately to prevent any itemChanged signals during world loading
        self.is_programmatic_change = True
        
        # Clear current data and state before loading new world
        self.clear_current_data()
        
        world_path = item_data.get("path")
        level_dat = os.path.join(world_path, "level.dat")
        
        if os.path.exists(level_dat):
            # Check file size first
            file_size = os.path.getsize(level_dat)
            if file_size < 100:  # File terlalu kecil
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"File level.dat terlalu kecil ({file_size} bytes). File mungkin kosong atau rusak.")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
                self.is_programmatic_change = False
                return
            
            self.nbt_file = level_dat
            try:
                # Try custom NBT parser first
                print(f"Loading {level_dat} with custom NBT parser...")
                self.nbt_reader = NBTReader()
                self.nbt_data = self.nbt_reader.read_nbt_file(level_dat)
                
                # If custom parser returns empty data, try nbtlib as fallback
                if not self.nbt_data or len(self.nbt_data) == 0:
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
                        self.nbt_data = dict(nbt_data.root)
                    else:
                        self.nbt_data = dict(nbt_data)
                    
                    # Create a simple structure for nbtlib data
                    self.nbt_reader = None
                    print(f"✅ Successfully loaded with nbtlib: {len(self.nbt_data)} keys")
                else:
                    print(f"✅ Successfully loaded with custom parser: {len(self.nbt_data)} keys")
                
                # Clear any previous search results
                self.search_utils.clear_search()
                
                # Populate tree with NBT structure
                self.populate_tree(self.nbt_data)
                
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka level.dat: {e}")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
            finally:
                # Always reset flag regardless of success or failure
                self.is_programmatic_change = False

    def open_file(self):
        """Open NBT file manually"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Buka File NBT/DAT", "", "NBT/DAT Files (*.nbt *.dat);;JSON Files (*.json);;All Files (*)")
        if file_path:
            # Set flag immediately to prevent any itemChanged signals during file loading
            self.is_programmatic_change = True
            
            # Clear current data and state before loading new file
            self.clear_current_data()
            
            self.nbt_file = file_path
            try:
                # Check if it's a JSON file
                if file_path.lower().endswith('.json'):
                    print(f"Loading JSON file: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.nbt_data = json.load(f)
                    self.nbt_reader = None
                    print(f"✅ Successfully loaded JSON: {len(self.nbt_data)} keys")
                else:
                    # Try custom NBT parser first
                    print(f"Loading {file_path} with custom NBT parser...")
                    self.nbt_reader = NBTReader()
                    self.nbt_data = self.nbt_reader.read_nbt_file(file_path)
                    
                    # If custom parser returns empty data, try nbtlib as fallback
                    if not self.nbt_data or len(self.nbt_data) == 0:
                        print("⚠️ Custom parser returned empty data, trying nbtlib...")
                        import nbtlib
                        
                        # Try uncompressed first (Bedrock Edition)
                        try:
                            nbt_data = nbtlib.load(file_path, gzipped=False)
                            print("✅ Successfully loaded with nbtlib (uncompressed)")
                        except Exception as e1:
                            print(f"⚠️ Failed to load as uncompressed: {e1}")
                            # Try gzipped (Java Edition)
                            try:
                                nbt_data = nbtlib.load(file_path, gzipped=True)
                                print("✅ Successfully loaded with nbtlib (gzipped)")
                            except Exception as e2:
                                print(f"❌ Failed to load with nbtlib: {e2}")
                                raise Exception(f"Failed to load with both methods: uncompressed ({e1}), gzipped ({e2})")
                        
                        if hasattr(nbt_data, 'root'):
                            self.nbt_data = dict(nbt_data.root)
                        else:
                            self.nbt_data = dict(nbt_data)
                        
                        # Create a simple structure for nbtlib data
                        self.nbt_reader = None
                        print(f"✅ Successfully loaded with nbtlib: {len(self.nbt_data)} keys")
                    else:
                        print(f"✅ Successfully loaded with custom parser: {len(self.nbt_data)} keys")
                
                # Clear any previous search results
                self.search_utils.clear_search()
                
                # Populate tree with NBT structure
                self.populate_tree(self.nbt_data)
                
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka file: {e}")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
            finally:
                # Always reset flag regardless of success or failure
                self.is_programmatic_change = False

    def save_file(self):
        """Save current data to file"""
        if self.nbt_file and self.nbt_data:
            try:
                print(f"💾 Saving file: {self.nbt_file}")
                
                # Save as JSON for now (simplified approach)
                if self.nbt_file.endswith('.json'):
                    save_path = self.nbt_file
                else:
                    save_path = self.nbt_file.replace('.dat', '.json').replace('.nbt', '.json')
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(self.nbt_data, f, indent=2, ensure_ascii=False)
                print(f"✅ Saved as JSON: {save_path}")
                
                # Success message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Sukses")
                msg.setText(f"Data disimpan sebagai JSON:\n{save_path}")
                msg.setStyleSheet(GUIComponents.get_message_box_style())
                msg.exec_()
                    
            except Exception as e:
                print(f"❌ Save error: {e}")
                import traceback
                traceback.print_exc()
                
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal menyimpan file: {e}")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Peringatan")
            msg.setText("Tidak ada file yang terbuka untuk disimpan!")
            msg.setStyleSheet(GUIComponents.get_warning_message_box_style())
            msg.exec_()

    def get_type_color(self, type_name):
        """Get color for different NBT types"""
        colors = {
            'B': '#FF0000',    # Bright Red for Boolean/Byte
            'I': '#00FF00',    # Bright Green for Integer
            'L': '#0000FF',    # Bright Blue for Long
            'F': '#FFFF00',    # Bright Yellow for Float
            'D': '#FF00FF',    # Magenta for Double
            'S': '#00FFFF',    # Cyan for String
            'COMP': '#FFA500', # Orange for Compound
            'LIST': '#800080', # Purple for List
            'BA': '#FF4500',   # Orange Red for Byte Array
            'IA': '#4169E1',   # Royal Blue for Int Array
            'LA': '#8A2BE2',   # Blue Violet for Long Array
        }
        color = colors.get(type_name, '#FFFFFF')  # White for unknown types
        return color

    def populate_tree(self, nbt_node, parent_item=None):
        """Populate tree widget with NBT data using hierarchical structure"""
        try:
            # Clear existing data
            self.tree.clear()
            
            # Use NBT reader structure if available
            if hasattr(self, 'nbt_reader') and self.nbt_reader:
                # Get structure from NBT reader
                structure = self.nbt_reader.get_structure_display()
                
                # Create hierarchical tree structure
                self._build_tree_hierarchy(structure, self.tree.invisibleRootItem())
                        
            else:
                # Fallback to original method if no NBT reader (using nbtlib data)
                print("⚠️ Using nbtlib data format")
                if isinstance(nbt_node, dict):
                    items = sorted(nbt_node.items())
                    self._build_tree_from_dict(items, self.tree.invisibleRootItem())
                
        except Exception as e:
            print(f"❌ Error populating tree: {e}")
            import traceback
            traceback.print_exc()

    def _build_tree_hierarchy(self, structure, parent_item):
        """Build hierarchical tree from NBT structure"""
        # Group items by their parent-child relationships
        parent_items = {}
        root_items = []
        
        # First pass: create all items
        for field_name, value, type_name, level in structure:
            # Create tree item
            tree_item = QTreeWidgetItem()
            tree_item.setText(0, type_name)  # Type column
            tree_item.setText(1, field_name)  # Name column
            tree_item.setText(2, str(value))  # Value column
            
            # Apply color to type column
            type_color = self.get_type_color(type_name)
            tree_item.setForeground(0, QColor(type_color))
            
            # Store original data for editing
            tree_item.setData(0, Qt.UserRole, (field_name, value, type_name))
            
            # Make value column editable for primitive types
            if type_name not in ['COMP', 'LIST', 'BA', 'IA', 'LA']:
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)
            
            # Set expandable for compound and list types
            if type_name in ['COMP', 'LIST']:
                tree_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                # Add a dummy child to ensure arrow shows up
                dummy_child = QTreeWidgetItem(tree_item)
                dummy_child.setText(0, "")
                dummy_child.setText(1, "")
                dummy_child.setText(2, "")
                dummy_child.setHidden(True)
            
            # Store item for parent-child relationship
            if level == 0:
                root_items.append(tree_item)
            else:
                # Find parent based on field name hierarchy
                parent_name = self._get_parent_name(field_name)
                if parent_name not in parent_items:
                    parent_items[parent_name] = []
                parent_items[parent_name].append(tree_item)
        
        # Second pass: establish parent-child relationships
        for item in root_items:
            field_name = item.text(1)
            parent_item.addChild(item)
            
            # Add children if this is a parent
            if field_name in parent_items:
                for child_item in parent_items[field_name]:
                    item.addChild(child_item)
    
    def _get_parent_name(self, field_name):
        """Extract parent name from field name"""
        if '.' in field_name:
            return field_name.rsplit('.', 1)[0]
        elif '[' in field_name:
            return field_name.split('[')[0]
        return None

    def _build_tree_from_dict(self, items, parent_item):
        """Build tree from dictionary items (fallback method)"""
        for key, value in items:
            # Determine type for display
            if isinstance(value, bool):
                type_name = 'B'
            elif isinstance(value, int):
                type_name = 'I' if abs(value) <= 2147483647 else 'L'
            elif isinstance(value, float):
                type_name = 'F'
            elif isinstance(value, str):
                type_name = 'S'
            elif isinstance(value, list):
                type_name = 'LIST'
            elif isinstance(value, dict):
                type_name = 'COMP'
            else:
                type_name = 'UNKNOWN'
            
            # Format value for display
            if isinstance(value, (list, dict)):
                if isinstance(value, list):
                    value_display = f"[{len(value)} items]"
                else:  # dict
                    value_display = f"{{{len(value)} items}}"
            else:
                value_display = str(value)
            
            # Create tree item
            tree_item = QTreeWidgetItem(parent_item)
            tree_item.setText(0, type_name)  # Type column
            tree_item.setText(1, key)  # Name column
            tree_item.setText(2, value_display)  # Value column
            
            # Apply color to type column
            type_color = self.get_type_color(type_name)
            tree_item.setForeground(0, QColor(type_color))
            
            # Store original data for editing
            tree_item.setData(0, Qt.UserRole, (key, value, type_name))
            
            # Check if this item has children (entries)
            has_children = isinstance(value, (dict, list)) and len(value) > 0
            
            # Make value column editable ONLY for primitive types that don't have children
            if type_name not in ['COMP', 'LIST'] and not has_children:
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)
            else:
                # Remove editable flag for compound/list types or items with children
                tree_item.setFlags(tree_item.flags() & ~Qt.ItemIsEditable)
                # Set visual indication that this item is not editable (slightly dimmed)
                tree_item.setForeground(2, QColor("#888888"))
            
            # Set expandable for compound and list types
            if type_name in ['COMP', 'LIST']:
                tree_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                # Add a dummy child to ensure arrow shows up
                dummy_child = QTreeWidgetItem(tree_item)
                dummy_child.setText(0, "")
                dummy_child.setText(1, "")
                dummy_child.setText(2, "")
                dummy_child.setHidden(True)

    def on_tree_item_double_clicked(self, item, column):
        """Handle double-click untuk inline editing"""
        # Allow editing for value column (column 2) only if item is editable
        if column == 2:  # Value column
            # Check if item is editable (has Qt.ItemIsEditable flag)
            if item.flags() & Qt.ItemIsEditable:
                # For QTreeWidget, we need to start editing the cell
                self.tree.editItem(item, column)
            else:
                # Show message that this item cannot be edited
                print(f"⚠️ Item '{item.text(1)}' cannot be edited (compound/list type or has children)")

    def on_item_changed(self, item, column):
        """Handle perubahan value dengan dialog konfirmasi"""
        # Skip if this is a programmatic change
        if self.is_programmatic_change:
            return
        
        # Skip if we're currently loading a file or changing worlds
        if not hasattr(self, 'nbt_data') or self.nbt_data is None:
            return
            
        # Check if this is the value column (column 2)
        if column == 2:  # Only for the value column
            try:
                # Get the original data from the item
                original_data = item.data(0, Qt.UserRole)
                if original_data:
                    field_name, original_value, type_name = original_data
                    
                    # Get the new value directly from the item
                    new_text = item.text(2)
                    try:
                        # Parse based on type
                        if type_name == 'B':  # boolean
                            if new_text.lower() in ['true', '1']:
                                new_value = True
                            elif new_text.lower() in ['false', '0']:
                                new_value = False
                            else:
                                raise ValueError(f"Invalid boolean value: {new_text}")
                        elif type_name in ['I', 'L']:  # integer/long
                            new_value = int(new_text)
                        elif type_name in ['F', 'D']:  # float/double
                            new_value = float(new_text)
                        elif type_name == 'S':  # string
                            new_value = new_text
                        else:
                            new_value = new_text
                        
                        # Update the data structure
                        if field_name in self.nbt_data:
                            self.nbt_data[field_name] = new_value
                            print(f"✅ Updated {field_name}: {original_value} → {new_value}")
                            
                            # Update window title
                            self.setWindowTitle("Bedrock NBT/DAT Editor - No Admin Mode - *Modified")
                            
                    except Exception as e:
                        print(f"❌ Error parsing value: {e}")
                        
            except Exception as e:
                print(f"❌ Error updating value: {e}")
    
    def perform_live_search(self):
        """Delegate to search utils"""
        self.search_utils.perform_live_search()

    def export_to_json(self):
        """Export the current NBT data to a JSON file."""
        if self.nbt_data is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data NBT untuk diekspor.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan File JSON", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.nbt_data, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "Sukses", f"Data NBT berhasil diekspor ke {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mengekspor data JSON: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditorNoAdmin()
    window.show()
    sys.exit(app.exec_())
