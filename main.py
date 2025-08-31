#!/usr/bin/env python3
"""
Bedrock NBT/DAT Editor with Generic NBT Parser
Reads and displays NBT files with field names, values, and data types
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
    check_admin_privileges, WorldManager, FileOperations, TreeManager
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

class NBTEditorMain(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Check admin privileges first
        self.admin_mode = check_admin_privileges()
        
        self.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser)")
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
        
        # Load worlds
        self.world_manager.load_worlds()
        
        # Connect world selection
        self.world_list.itemClicked.connect(self.world_manager.on_world_selected)
        
        # Connect table item editing
        self.tree.itemDoubleClicked.connect(self.tree_manager.on_tree_item_double_clicked)
        self.tree.itemChanged.connect(self.tree_manager.on_item_changed)
        
        print("✅ NBT Editor initialized successfully")

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
        
        # Admin mode warning (if not in admin mode)
        if not self.admin_mode:
            admin_warning = QLabel("⚠️ Limited Access Mode - Some features may be restricted")
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
        
        # Warning notification about Long type issue
        long_type_warning = QLabel("⚠️")
        long_type_warning.setStyleSheet("""
            QLabel {
                color: #ff9500;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
                background-color: rgba(255, 149, 0, 0.1);
                border: 2px solid rgba(255, 149, 0, 0.3);
                border-radius: 10px;
                margin: 10px 0px;
                text-align: center;
            }
        """)
        long_type_warning.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(long_type_warning)
        
        # Warning text
        warning_text = QLabel("Key type L (Long) values are currently inaccurate.\nEditing Long values is temporarily disabled\nuntil this issue is resolved.")
        warning_text.setStyleSheet("""
            QLabel {
                color: #ff9500;
                font-size: 12px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(255, 149, 0, 0.05);
                border: 1px solid rgba(255, 149, 0, 0.2);
                border-radius: 6px;
                margin: 5px 0px;
                text-align: center;
            }
        """)
        warning_text.setAlignment(Qt.AlignCenter)
        warning_text.setWordWrap(True)
        right_panel.addWidget(warning_text)
        
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 1)  # 1 = minimum space for buttons
        
        central_widget.setLayout(main_layout)
        self.setStyleSheet("background-color: #181a20;")

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
    window = NBTEditorMain()
    window.show()
    sys.exit(app.exec_())
