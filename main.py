#!/usr/bin/env python3
"""
Bedrock NBT/DAT Editor with Generic NBT Parser
Reads and displays NBT files with field names, values, and data types
"""

import sys
import os
import shutil
import ctypes
import subprocess
from typing import Any


# Import our separated modules
from package_manager import *
from minecraft_paths import MINECRAFT_WORLDS_PATH
from nbt_reader.bedrock_nbt_parser import BedrockNBTParser as NBTReader
from search_utils import SearchUtils
from gui_components import GUIComponents, EnhancedTypeDelegate
from nbt_editor import NBTEditor as NBTFileEditor

# Additional imports needed for the main app
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QHeaderView,
    QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor, QPainter, QFont

def is_admin():
    """Check if the current process has administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False



def run_as_admin():
    """Restart the application with administrator privileges"""
    try:
        if not is_admin():
            # Re-run the program with admin rights
            result = ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                " ".join(sys.argv), 
                None, 
                1
            )
            if result > 32:  # Success
                sys.exit(0)
            else:
                print("⚠️ User cancelled admin elevation")
                return False
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False
    return False  # Don't exit if already admin

def check_admin_privileges():
    """Check and request admin privileges if needed"""
    if not is_admin():
        print("⚠️ Program membutuhkan hak akses Administrator untuk mengakses file Minecraft")
        print("🔄 Memulai ulang program dengan hak akses Administrator...")
        
        # Try to elevate privileges
        if run_as_admin():
            return False  # Exit if elevation is needed
        else:
            print("⚠️ Gagal mendapatkan hak akses Administrator, menjalankan dalam mode terbatas...")
            return True  # Continue in limited mode
    else:
        print("✅ Program berjalan dengan hak akses Administrator")
        return True

class NBTEditor(QMainWindow):
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
        
        # Load worlds
        self.load_worlds()
        
        # Connect world selection
        self.world_list.itemClicked.connect(self.on_world_selected)
        
        # Connect table item editing
        self.tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        self.tree.itemChanged.connect(self.on_item_changed)
        
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
        self.tree.setHeaderLabels(["Type", "Nama", "Value"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet(GUIComponents.get_enhanced_tree_style())
        
        # Set column widths with stretch factors for responsive layout
        self.tree.setColumnWidth(0, 100)  # Type column (fixed width) - wider for enhanced display
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
        self.tree.setRootIsDecorated(False)  # Disable default branch indicators (using custom ones)
        self.tree.setItemsExpandable(True)  # Allow items to be expanded
        
        # Setup custom branch text
        # Set custom delegate for enhanced type display
        self.tree.setItemDelegateForColumn(0, EnhancedTypeDelegate(self.tree))
        
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
            self.nbt_editor = None  # NBT file editor instance
            
            # Reset window title
            self.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser)")
            
            # Clear any pending operations
            if hasattr(self, 'search_timer') and self.search_timer.isActive():
                self.search_timer.stop()
            
            print("✅ Current data cleared successfully")
            
        except Exception as e:
            print(f"❌ Error clearing current data: {e}")

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

    def on_world_selected(self, item):
        """Handle world selection"""
        item_data = item.data(Qt.UserRole)
        if not item_data:
            return
            
        item_type = item_data.get("type")
        
        if item_type == "error":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Access Error")
            msg.setText("Cannot access Minecraft worlds.\n\nPlease run as administrator or check file permissions.")
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
        file_path, _ = QFileDialog.getOpenFileName(self, "Buka File NBT/DAT", "", "NBT/DAT Files (*.nbt *.dat)")
        if file_path:
            # Set flag immediately to prevent any itemChanged signals during file loading
            self.is_programmatic_change = True
            
            # Clear current data and state before loading new file
            self.clear_current_data()
            
            self.nbt_file = file_path
            try:
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
        """Save current data to file using NBTEditor"""
        if self.nbt_file and self.nbt_data:
            try:
                print(f"💾 Saving file: {self.nbt_file}")
                
                # Initialize NBTEditor if not already done
                if self.nbt_editor is None:
                    self.nbt_editor = NBTFileEditor(self.nbt_file)
                    self.nbt_editor.load_file()
                
                # Check if there are any modifications to save
                if not self.nbt_editor.has_modifications():
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Info")
                    msg.setText("Tidak ada perubahan yang perlu disimpan.")
                    msg.setStyleSheet(GUIComponents.get_message_box_style())
                    msg.exec_()
                    return
                
                # Get modified fields
                modified_fields = self.nbt_editor.get_modified_fields()
                
                # Save the file
                if self.nbt_editor.save_file(backup=True):
                    # Success message
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Sukses")
                    msg.setText(f"File berhasil disimpan!\n\nPerubahan yang disimpan:\n" + 
                              "\n".join([f"• {field}" for field in modified_fields[:10]]) + 
                              (f"\n...dan {len(modified_fields) - 10} field lainnya" if len(modified_fields) > 10 else ""))
                    msg.setStyleSheet(GUIComponents.get_message_box_style())
                    msg.exec_()
                    
                    # Update window title to remove modification indicator
                    self.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser)")
                else:
                    raise Exception("Failed to save file")
                    
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
            '📁': '#FFA500',   # Orange for Compound
            '📄': '#800080',   # Purple for List
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
        # Create a mapping of field names to tree items
        item_map = {}
        
        # First pass: create all items and establish parent-child relationships
        for field_name, value, type_name, level in structure:
            # Create tree item
            if level == 0:
                tree_item = QTreeWidgetItem(parent_item)
            else:
                # Find parent item
                parent_name = self._get_parent_name(field_name)
                if parent_name in item_map:
                    tree_item = QTreeWidgetItem(item_map[parent_name])
                else:
                    # Fallback: add to root
                    tree_item = QTreeWidgetItem(parent_item)
            
            # Handle NBTValue objects for display
            display_value = value
            if hasattr(value, 'value'):  # NBTValue object
                display_value = value.value
            
            tree_item.setText(0, type_name)  # Type column
            tree_item.setText(1, field_name)  # Name column
            tree_item.setText(2, str(display_value))  # Value column
            
            # Type column styling is handled by EnhancedTypeDelegate
            
            # Store original data for editing
            tree_item.setData(0, Qt.UserRole, (field_name, display_value, type_name))
            
            # Check if this item has children (entries) and add arrow indicator
            # Check if there are any child items for this field
            has_children = any(child_field.startswith(field_name + '.') or 
                             (field_name in child_field and '[' in child_field and field_name == child_field.split('[')[0])
                             for child_field, _, _, child_level in structure if child_level > level)
            
            # Make value column editable ONLY for primitive types that don't have children
            if type_name not in ['📁', '📄', 'BA', 'IA', 'LA'] and not has_children:
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)
            else:
                # Remove editable flag for compound/list types or items with children
                tree_item.setFlags(tree_item.flags() & ~Qt.ItemIsEditable)
                            # Set visual indication that this item is not editable (slightly dimmed)
            tree_item.setForeground(2, QColor("#888888"))
            
            # Set expandable for compound and list types or items with children
            if type_name in ['📁', '📄'] or has_children:
                tree_item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                # Add a dummy child to ensure arrow shows up
                dummy_child = QTreeWidgetItem(tree_item)
                dummy_child.setText(0, "")
                dummy_child.setText(1, "")
                dummy_child.setText(2, "")
                dummy_child.setHidden(True)
            
            # Store item in map for parent-child relationships
            item_map[field_name] = tree_item
    
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
                # Check if integer 0/1 should be treated as boolean
                if value in [0, 1]:
                    type_name = 'B'  # Treat as boolean
                else:
                    type_name = 'I' if abs(value) <= 2147483647 else 'L'
            elif isinstance(value, float):
                type_name = 'F'
            elif isinstance(value, str):
                type_name = 'S'
            elif isinstance(value, list):
                type_name = '📄'
            elif isinstance(value, dict):
                type_name = '📁'
            else:
                type_name = 'UNKNOWN'
            
            # Format value for display
            if isinstance(value, (list, dict)):
                if isinstance(value, list):
                    value_display = f"[{len(value)} items]"
                else:  # dict
                    value_display = f"{{{len(value)} items}}"
            elif isinstance(value, bool) or (isinstance(value, int) and value in [0, 1]):
                # Display boolean as 0/1 for easier editing
                value_display = "1" if value else "0"
            else:
                value_display = str(value)
            
            # Create tree item
            tree_item = QTreeWidgetItem(parent_item)
            tree_item.setText(0, type_name)  # Type column
            tree_item.setText(1, key)  # Name column
            tree_item.setText(2, value_display)  # Value column
            
            # Type column styling is handled by EnhancedTypeDelegate
            
            # Store original data for editing
            tree_item.setData(0, Qt.UserRole, (key, value, type_name))
            
            # Check if this item has children (entries)
            has_children = isinstance(value, (dict, list)) and len(value) > 0
            
            # Make value column editable ONLY for primitive types that don't have children
            if type_name not in ['📁', '📄'] and not has_children:
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)
            else:
                # Remove editable flag for compound/list types or items with children
                tree_item.setFlags(tree_item.flags() & ~Qt.ItemIsEditable)
            
            # Set expandable for compound and list types or items with children
            if type_name in ['📁', '📄'] or has_children:
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
                    
                    # Check if value actually changed
                    if str(original_value) == new_text:
                        print(f"ℹ️ Field {field_name} unchanged: {original_value}")
                        return
                    
                    # Initialize NBTEditor if not already done
                    if self.nbt_editor is None:
                        self.nbt_editor = NBTFileEditor(self.nbt_file)
                        self.nbt_editor.load_file()
                    
                    # Convert new_text to appropriate type based on original_value
                    new_value = self._convert_value_to_type(new_text, original_value, type_name)
                    
                    # Update the field using NBTEditor
                    if self.nbt_editor.update_field(field_name, new_value):
                        # Update the data structure for display
                        if field_name in self.nbt_data:
                            self.nbt_data[field_name] = new_value
                        
                        # Update window title to show modification
                        self.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser) - *Modified")
                        
                        print(f"✅ Updated {field_name}: {original_value} → {new_value}")
                    else:
                        # Revert the change if update failed
                        item.setText(2, str(original_value))
                        print(f"❌ Failed to update {field_name}, reverted to original value")
                            
            except Exception as e:
                print(f"❌ Error updating value: {e}")
    
    def _convert_value_to_type(self, text_value: str, original_value: Any, type_name: str) -> Any:
        """Convert text value to appropriate type based on original value"""
        try:
            # If original value is a number, try to convert text to number
            if isinstance(original_value, (int, float)):
                if isinstance(original_value, int):
                    # Special handling for integer 0/1 as boolean
                    if original_value in [0, 1] and type_name == 'B':
                        text_lower = text_value.lower()
                        if text_lower in ['true', '1', 'yes', 'on']:
                            return 1
                        elif text_lower in ['false', '0', 'no', 'off']:
                            return 0
                        else:
                            return original_value  # Keep original if conversion fails
                    else:
                        return int(text_value)
                else:
                    return float(text_value)
            
            # If original value is boolean
            elif isinstance(original_value, bool):
                text_lower = text_value.lower()
                if text_lower in ['true', '1', 'yes', 'on']:
                    return True
                elif text_lower in ['false', '0', 'no', 'off']:
                    return False
                else:
                    return original_value  # Keep original if conversion fails
            
            # For strings and other types, return as string
            else:
                return text_value
                
        except (ValueError, TypeError):
            # If conversion fails, return original value
            return original_value
    
    def perform_live_search(self):
        """Delegate to search utils"""
        self.search_utils.perform_live_search()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditor()
    window.show()
    sys.exit(app.exec_())
