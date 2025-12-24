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
    check_admin_privileges, WorldManager, FileOperations, TreeManager,
    is_admin
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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class NBTEditorMain(QMainWindow):
    def __init__(self, admin_mode=False):
        super().__init__()
        
        # Store admin privileges status
        self.admin_mode = admin_mode
        
        self.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser)")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon(resource_path("icon.png")))
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
        
        # Spacer
        right_panel.addSpacing(20)
        
        # World Modifiers
        modifiers_label = QLabel("Quick Actions:")
        modifiers_label.setStyleSheet("color: #ffffff; margin-bottom: 5px; font-weight: bold; font-size: 14px;")
        right_panel.addWidget(modifiers_label)

        # Enable Achievements Button
        self.achievements_btn = QPushButton("Enable Achievements")
        self.achievements_btn.setToolTip("Sets hasBeenLoadedInCreative to 0 (False)")
        self.achievements_btn.clicked.connect(self.enable_achievements)
        self.achievements_btn.setStyleSheet(GUIComponents.get_info_button_style())
        right_panel.addWidget(self.achievements_btn)
        
        # Disable Experiments Button
        self.experiments_btn = QPushButton("Disable Experiments")
        self.experiments_btn.setToolTip("Disables all entries in the experiments tag")
        self.experiments_btn.clicked.connect(self.disable_experiments)
        self.experiments_btn.setStyleSheet(GUIComponents.get_warning_button_style())
        right_panel.addWidget(self.experiments_btn)
        
        # Right panel currently only contains action buttons
        
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

    def enable_achievements(self):
        """Enable achievements by setting hasBeenLoadedInCreative to 0 and cheatsEnabled to 0"""
        if not self.nbt_file or self.nbt_data is None:
            QMessageBox.warning(self, "Warning", "Please select a world first.")
            return

        try:
            # Initialize editor if needed
            if self.nbt_editor is None:
                self.nbt_editor = self.nbt_editor_class(self.nbt_file)
                self.nbt_editor.load_file()
            
            # Check current values
            current_creative = self.nbt_editor.get_field_value("hasBeenLoadedInCreative")
            current_cheats = self.nbt_editor.get_field_value("cheatsEnabled")
            
            changes_made = False
            
            # Update hasBeenLoadedInCreative
            if self.nbt_editor.update_field("hasBeenLoadedInCreative", 0):
                changes_made = True
                # Update local data structure for UI sync
                if isinstance(self.nbt_data, dict):
                    self.nbt_data["hasBeenLoadedInCreative"] = 0
                elif isinstance(self.nbt_data, list):
                    # Handle list of tuples from custom parser
                    for i, entry in enumerate(self.nbt_data):
                        if entry[0] == "hasBeenLoadedInCreative":
                            new_entry = list(entry)
                            new_entry[1] = 0
                            self.nbt_data[i] = tuple(new_entry)
                            break
            
            # Update cheatsEnabled - only if it exists or we can enable it (typically exists in Level.dat)
            # We'll try to update it regardless, if it doesn't exist update_field might return False or we can check first
            # But usually it's fine to try update.
            if self.nbt_editor.update_field("cheatsEnabled", 0):
                changes_made = True
                if isinstance(self.nbt_data, dict):
                    self.nbt_data["cheatsEnabled"] = 0
                elif isinstance(self.nbt_data, list):
                     for i, entry in enumerate(self.nbt_data):
                        if entry[0] == "cheatsEnabled":
                            new_entry = list(entry)
                            new_entry[1] = 0
                            self.nbt_data[i] = tuple(new_entry)
                            break

            if changes_made:
                # Update UI
                self.populate_tree(self.nbt_data)
                self.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser) - *Modified")
                
                QMessageBox.information(self, "Success", 
                    "Achievements enabled!\n\n"
                    "Field 'hasBeenLoadedInCreative' set to 0.\n"
                    "Field 'cheatsEnabled' set to 0.\n"
                    "Don't forget to click Save to apply changes.")
            else:
                # If update returned False, maybe it was already 0?
                if current_creative == 0 and current_cheats == 0:
                    QMessageBox.information(self, "Info", "Achievements are already fully enabled (Creative: 0, Cheats: 0).")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update one or more fields.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to enable achievements: {e}")

    def disable_experiments(self):
        """Disable all experiments"""
        if not self.nbt_file or self.nbt_data is None:
            QMessageBox.warning(self, "Warning", "Please select a world first.")
            return

        try:
            # Initialize editor if needed
            if self.nbt_editor is None:
                self.nbt_editor = self.nbt_editor_class(self.nbt_file)
                self.nbt_editor.load_file()
                
            # Use editor to get experiments dict safely
            experiments = self.nbt_editor.get_field_value("experiments")
            
            if not experiments or not isinstance(experiments, dict):
                QMessageBox.information(self, "Info", "No experiments tag found in this world.")
                return

            count = 0
            mod_made = False
            
            # Iterate and disable
            for key in list(experiments.keys()):
                field_path = f"experiments.{key}"
                # Set to 0 (False)
                if self.nbt_editor.update_field(field_path, 0):
                    experiments[key] = 0
                    mod_made = True
                    count += 1
            
            if mod_made:
                # Update local data structure for UI sync
                if isinstance(self.nbt_data, dict):
                    self.nbt_data["experiments"] = experiments
                elif isinstance(self.nbt_data, list):
                    # Handle list of tuples from custom parser
                    # We need to update sub-entries with names starting with "experiments."
                    for i, entry in enumerate(self.nbt_data):
                        name = entry[0]
                        if name.startswith("experiments."):
                            # Verify if this is one of the keys we updated
                            key = name.split(".")[-1]
                            if key in experiments:
                                # Create new tuple with updated value
                                new_entry = list(entry)
                                new_entry[1] = 0
                                self.nbt_data[i] = tuple(new_entry)
                
                self.populate_tree(self.nbt_data)
                self.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser) - *Modified")
                
                QMessageBox.information(self, "Success", 
                    f"Disabled {count} experiments.\n\n"
                    "Don't forget to click Save to apply changes.")
            else:
                QMessageBox.information(self, "Info", "All experiments are already disabled.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to disable experiments: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Check admin privileges before starting the app
    # This prevents UI from being created if we need to restart as admin
    is_admin_mode = check_admin_privileges()
    
    # Only if we didn't restart (check_admin_privileges returns True if already admin/limited mode
    # or False if it restarted the process)
    # Actually check_admin_privileges returns:
    # - True: Already admin OR failed to elevate (limited mode)
    # - False: Successfully triggered restart
    
    # But wait, check_admin_privileges returns False if it successfully triggered run_as_admin which returns success code > 32
    # So if it returns False, we should EXIT this process.
    
    # Let's fix usage:
    # If check_admin_privileges() returns False (meaning elevation triggered), we exit.
    
    # Re-reading logic in admin_utils.py:
    # check_admin_privileges calls run_as_admin
    # if run_as_admin returns True (success restart), check_admin_privileges returns False.
    # So if False, we exit.
    
    # However, in my new admin_utils.py:
    # run_as_admin returns True if ShellExecute > 32 (success)
    
    if is_admin_mode:
        app = QApplication(sys.argv)
        # Re-check actual admin status for the UI flag, since check_admin_privileges returns True for both Admin and Limited
        real_admin_status = is_admin()
        
        window = NBTEditorMain(admin_mode=real_admin_status)
        window.show()
        sys.exit(app.exec_())
    else:
        # Elevation triggered, exit this process
        sys.exit(0)
