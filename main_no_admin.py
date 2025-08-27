#!/usr/bin/env python3
"""
Bedrock NBT/DAT Editor - No Admin Version
Runs without requiring administrator privileges for development and testing
"""

import sys
import os
from typing import Any

# Import our separated modules
from resource.package_manager import *
from resource import MINECRAFT_WORLDS_PATH
from nbt_utility import BedrockNBTParser, NBTFileEditor
from resource import SearchUtils
from gui_components import (
    GUIComponents, EnhancedTypeDelegate, 
    WorldManager, FileOperations, TreeManager
)

# Additional imports needed for the main app
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QHeaderView,
    QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor, QPainter, QFont

class NBTEditorNoAdminMain(QMainWindow):
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
        
        # Set up class references for components
        self.nbt_reader_class = BedrockNBTParser
        self.nbt_editor_class = NBTFileEditor
        
        # Timer for search debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_live_search)
        
        # Flag to prevent itemChanged signal during search/programmatic changes
        self.is_programmatic_change = False
        
        # Initialize components first
        self.world_manager = WorldManager(None, self)  # Will be set in init_ui
        self.file_ops = FileOperations(self)
        self.tree_manager = TreeManager(self)
        
        self.init_ui()
        
        # Update world_manager with the actual widget
        self.world_manager.world_list = self.world_list
        
        # Initialize search utilities after UI is created
        self.search_utils = SearchUtils(self.tree, self.search_input, self.search_status, self.search_timer, self)
        
        # Connect search input to search utils
        self.search_input.textChanged.connect(self.search_utils.on_search_text_changed)
        
        # Load worlds (will show limited access message)
        self.load_worlds_no_admin()
        
        # Connect world selection
        self.world_list.itemClicked.connect(self.on_world_selected_no_admin)
        
        # Connect table item editing
        self.tree.itemDoubleClicked.connect(self.tree_manager.on_tree_item_double_clicked)
        self.tree.itemChanged.connect(self.tree_manager.on_item_changed)
        
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
        self.tree_manager.setup_tree(self.tree)
        
        center_layout.addWidget(self.tree)
        main_layout.addLayout(center_layout, 4)  # 4 = most space for table
        
        # Right panel for actions
        right_panel = QVBoxLayout()
        
        # Action buttons
        open_button = QPushButton("Open File")
        open_button.clicked.connect(self.file_ops.open_file)
        open_button.setStyleSheet(GUIComponents.get_button_style())
        right_panel.addWidget(open_button)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.file_ops.save_file)
        save_button.setStyleSheet(GUIComponents.get_button_style())
        right_panel.addWidget(save_button)
        
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

    def load_worlds_no_admin(self):
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
                "doFireTick": 1,  # Boolean as 1/0
                "doMobSpawning": 1,  # Boolean as 1/0
                "doTileDrops": 1,  # Boolean as 1/0
                "keepInventory": 0,  # Boolean as 1/0
                "naturalRegeneration": 1  # Boolean as 1/0
            },
            "abilities": {
                "flying": 0,  # Boolean as 1/0
                "instabuild": 0,  # Boolean as 1/0
                "invulnerable": 0,  # Boolean as 1/0
                "mayfly": 0,  # Boolean as 1/0
                "walking": 1  # Boolean as 1/0
            }
        }
        
        self.nbt_data = demo_data
        self.nbt_file = "demo_data"
        self.nbt_reader = None  # Use nbtlib fallback
        
        # Clear any previous search results
        self.search_utils.clear_search()
        
        # Populate tree with demo data
        self.tree_manager.populate_tree(self.nbt_data)
        
        # Update window title
        self.setWindowTitle("Bedrock NBT/DAT Editor - No Admin Mode - Demo Data")
        
        print("✅ Demo data loaded successfully")

    def on_world_selected_no_admin(self, item):
        """Handle world selection for no-admin mode"""
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
        
        # Use the regular world manager for real worlds
        self.world_manager.on_world_selected(item)

    def clear_current_data(self):
        """Clear current data and reset state"""
        self.file_ops.clear_current_data()

    def populate_tree(self, nbt_node, parent_item=None):
        """Populate tree widget with NBT data"""
        self.tree_manager.populate_tree(nbt_node, parent_item)

    def perform_live_search(self):
        """Delegate to search utils"""
        self.search_utils.perform_live_search()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditorNoAdminMain()
    window.show()
    sys.exit(app.exec_())
