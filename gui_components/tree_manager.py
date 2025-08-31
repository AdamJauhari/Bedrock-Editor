"""
Tree Manager
Handles NBT data tree display and editing functionality
"""

from typing import Any
from PyQt5.QtWidgets import QTreeWidgetItem, QHeaderView, QTreeWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .styling_components import StylingComponents, EnhancedTypeDelegate

class TreeManager:
    """Manages NBT data tree display and editing"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def setup_tree(self, tree_widget):
        """Setup tree widget with proper configuration"""
        tree_widget.setHeaderLabels(["Type", "Nama", "Value"])
        tree_widget.setAlternatingRowColors(True)
        tree_widget.setStyleSheet(StylingComponents.get_enhanced_tree_style())
        
        # Set column widths with stretch factors for responsive layout
        tree_widget.setColumnWidth(0, 100)  # Type column (fixed width) - wider for enhanced display
        tree_widget.setColumnWidth(1, 300)  # Nama column (initial width)
        tree_widget.setColumnWidth(2, 400)  # Value column (initial width)
        
        # Set stretch factors for responsive columns
        tree_widget.header().setStretchLastSection(True)  # Value column stretches
        tree_widget.header().setSectionResizeMode(0, QHeaderView.Fixed)  # Type fixed
        tree_widget.header().setSectionResizeMode(1, QHeaderView.Interactive)  # Nama interactive
        tree_widget.header().setSectionResizeMode(2, QHeaderView.Stretch)  # Value stretches
        
        # Set tree properties
        tree_widget.setSelectionBehavior(QTreeWidget.SelectRows)
        tree_widget.setEditTriggers(QTreeWidget.NoEditTriggers)
        tree_widget.setRootIsDecorated(False)  # Disable default branch indicators (using custom ones)
        tree_widget.setItemsExpandable(True)  # Allow items to be expanded
        
        # Set custom delegate for enhanced type display
        tree_widget.setItemDelegateForColumn(0, EnhancedTypeDelegate(tree_widget))
    
    def populate_tree(self, nbt_node, parent_item=None):
        """Populate tree widget with NBT data using hierarchical structure"""
        try:
            # Clear existing data
            self.main_window.tree.clear()
            
            # Use NBT reader structure if available
            if hasattr(self.main_window, 'nbt_reader') and self.main_window.nbt_reader:
                # Get structure from NBT reader
                structure = self.main_window.nbt_reader.get_structure_display()
                
                # Create hierarchical tree structure
                self._build_tree_hierarchy(structure, self.main_window.tree.invisibleRootItem())
                        
            else:
                # Fallback to original method if no NBT reader (using nbtlib data)
                print("⚠️ Using nbtlib data format")
                if isinstance(nbt_node, dict):
                    items = sorted(nbt_node.items())
                    self._build_tree_from_dict(items, self.main_window.tree.invisibleRootItem())
                
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
            # Temporarily disable editing for Long type (L) due to accuracy issues
            if type_name not in ['📁', '📄', 'BA', 'IA', 'LA', 'L'] and not has_children:
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)
            else:
                # Remove editable flag for compound/list types, items with children, or Long type
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
            # Temporarily disable editing for Long type (L) due to accuracy issues
            if type_name not in ['📁', '📄', 'L'] and not has_children:
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)
            else:
                # Remove editable flag for compound/list types, items with children, or Long type
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
                self.main_window.tree.editItem(item, column)
            else:
                # Get the type of the item
                item_type = item.text(0)
                item_name = item.text(1)
                
                # Show specific message for Long type
                if item_type == 'L':
                    print(f"⚠️ Item '{item_name}' (Long type) cannot be edited - values are currently inaccurate")
                else:
                    # Show message that this item cannot be edited
                    print(f"⚠️ Item '{item_name}' cannot be edited (compound/list type or has children)")

    def on_item_changed(self, item, column):
        """Handle perubahan value dengan dialog konfirmasi"""
        # Skip if this is a programmatic change
        if self.main_window.is_programmatic_change:
            return
        
        # Skip if we're currently loading a file or changing worlds
        if not hasattr(self.main_window, 'nbt_data') or self.main_window.nbt_data is None:
            return
            
        # Check if this is the value column (column 2)
        if column == 2:  # Only for the value column
            try:
                # Get the original data from the item
                original_data = item.data(0, Qt.UserRole)
                if original_data:
                    field_name, original_value, type_name = original_data
                    
                    # Prevent editing Long type values due to accuracy issues
                    if type_name == 'L':
                        print(f"⚠️ Cannot edit Long type field '{field_name}' - values are currently inaccurate")
                        # Revert the change
                        item.setText(2, str(original_value))
                        return
                    
                    # Get the new value directly from the item
                    new_text = item.text(2)
                    
                    # Check if value actually changed
                    if str(original_value) == new_text:
                        print(f"ℹ️ Field {field_name} unchanged: {original_value}")
                        return
                    
                    # Initialize NBTEditor if not already done
                    if self.main_window.nbt_editor is None:
                        self.main_window.nbt_editor = self.main_window.nbt_editor_class(self.main_window.nbt_file)
                        self.main_window.nbt_editor.load_file()
                    
                    # Convert new_text to appropriate type based on original_value
                    new_value = self.main_window.file_ops.convert_value_to_type(new_text, original_value, type_name)
                    
                    # Update the field using NBTEditor
                    if self.main_window.nbt_editor.update_field(field_name, new_value):
                        # Update the data structure for display
                        if field_name in self.main_window.nbt_data:
                            self.main_window.nbt_data[field_name] = new_value
                        
                        # Update window title to show modification
                        self.main_window.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser) - *Modified")
                        
                        print(f"✅ Updated {field_name}: {original_value} → {new_value}")
                    else:
                        # Revert the change if update failed
                        item.setText(2, str(original_value))
                        print(f"❌ Failed to update {field_name}, reverted to original value")
                            
            except Exception as e:
                print(f"❌ Error updating value: {e}")
    
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
