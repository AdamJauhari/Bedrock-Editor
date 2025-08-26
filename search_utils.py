from PyQt5.QtGui import QColor

class SearchUtils:
    """Utility class for search and filtering functionality"""
    
    def __init__(self, tree_widget, search_input, search_status, search_timer, main_window=None):
        self.tree = tree_widget
        self.search_input = search_input
        self.search_status = search_status
        self.search_timer = search_timer
        self.search_results = []
        self.main_window = main_window  # Reference to main window for flag access
    
    def on_search_text_changed(self):
        """Handle text changes in search input untuk live search"""
        # Stop previous timer jika ada
        self.search_timer.stop()
        
        search_text = self.search_input.text().strip()
        
        if not search_text:
            # Jika search box kosong, tampilkan semua items
            # Set flag untuk mencegah itemChanged signal
            if self.main_window:
                self.main_window.is_programmatic_change = True
            
            self.show_all_items()
            self.search_results = []
            self.search_status.setText("Siap untuk mencari...")
            self.search_status.setStyleSheet("""
                color: #888888;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 8px;
            """)
            # Reset search input style
            self.update_search_input_style("#404040")
            # Reset window title
            self.tree.window().setWindowTitle("Bedrock NBT/DAT Editor")
            
            # Reset flag setelah selesai
            if self.main_window:
                self.main_window.is_programmatic_change = False
            return
        
        # Update status saat mengetik
        self.search_status.setText(f"Mencari '{search_text}'...")
        self.search_status.setStyleSheet("""
            color: #00bfff;
            font-size: 12px;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 4px 8px;
        """)
        
        # Start timer dengan delay 300ms untuk debouncing
        self.search_timer.start(300)
    
    def perform_live_search(self):
        """Perform actual search dengan filter hasil - hanya tampilkan yang cocok"""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
        
        # Set flag untuk mencegah itemChanged signal
        if self.main_window:
            self.main_window.is_programmatic_change = True
        
        # Reset previous search state
        self.show_all_items()
        
        # Search through tree items dan hide yang tidak cocok
        found_items = []
        all_items = []
        
        # Search through all tree items recursively
        def search_tree_items(parent_item):
            for i in range(parent_item.childCount()):
                item = parent_item.child(i)
                all_items.append(item)
                
                # Get item text from name column (column 1)
                name_text = item.text(1).lower()
                
                # Check if search term matches field name
                if search_text.lower() in name_text:
                    found_items.append(item)
                    
                    # Highlight the found item
                    item.setBackground(0, QColor("#ff6b35"))  # Type column
                    item.setBackground(1, QColor("#ff6b35"))  # Name column
                    item.setBackground(2, QColor("#ff6b35"))  # Value column
                    item.setForeground(1, QColor("#ffffff"))  # White text for name
                    item.setForeground(2, QColor("#ffffff"))  # White text for value
                    # Keep original type color, don't override
                
                # Recursively search children
                if item.childCount() > 0:
                    search_tree_items(item)
        
        # Start search from root
        root_item = self.tree.invisibleRootItem()
        search_tree_items(root_item)
        
        # Store results and update UI
        self.search_results = found_items
        
        if found_items:
            # Select first result and scroll to it
            self.tree.setCurrentItem(found_items[0])
            self.tree.scrollToItem(found_items[0])
            
            # Show success status
            self.search_status.setText(f"✓ Menampilkan {len(found_items)} dari {len(all_items)} item untuk '{search_text}'")
            self.search_status.setStyleSheet("""
                color: #00d084;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 8px;
                font-weight: bold;
            """)
            
            # Green border untuk success
            self.update_search_input_style("#00d084")
            
            # Update window title dengan search results count
            original_title = "Bedrock NBT/DAT Editor"
            self.tree.window().setWindowTitle(f"{original_title} - Filtered: {len(found_items)}/{len(all_items)} items")
        else:
            # Show no results status
            self.search_status.setText(f"✗ Tidak ada hasil untuk '{search_text}' - {len(all_items)} item diperiksa")
            self.search_status.setStyleSheet("""
                color: #ff0000;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 8px;
                font-weight: bold;
                background-color: rgba(255, 0, 0, 0.1);
                border: 1px solid rgba(255, 0, 0, 0.3);
                border-radius: 4px;
            """)
            
            # Red border untuk no results
            self.update_search_input_style("#ff0000")
        
        # Reset flag setelah selesai programmatic changes
        if self.main_window:
            self.main_window.is_programmatic_change = False
    
    def show_all_items(self):
        """Tampilkan kembali semua items dan reset colors"""
        # Set flag untuk mencegah itemChanged signal jika belum di-set
        was_programmatic = self.main_window.is_programmatic_change if self.main_window else False
        if not was_programmatic and self.main_window:
            self.main_window.is_programmatic_change = True
        
        # Reset colors for all tree items recursively
        def reset_tree_items(parent_item):
            for i in range(parent_item.childCount()):
                item = parent_item.child(i)
                # Reset background dan foreground colors
                item.setBackground(0, QColor("transparent"))
                item.setBackground(1, QColor("transparent"))
                item.setBackground(2, QColor("transparent"))
                self.restore_item_colors(item)
                
                # Recursively reset children
                if item.childCount() > 0:
                    reset_tree_items(item)
        
        # Start from root
        root_item = self.tree.invisibleRootItem()
        reset_tree_items(root_item)
        
        # Reset flag hanya jika kita yang set (tidak override flag yang sudah ada)
        if not was_programmatic and self.main_window:
            self.main_window.is_programmatic_change = False
    
    def update_search_input_style(self, border_color):
        """Update search input border color"""
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2d3139;
                color: #e1e1e1;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 16px;
            }}
            QLineEdit:focus {{
                border: 2px solid #00bfff;
                background-color: #23272e;
            }}
            QLineEdit::placeholder {{
                color: #888888;
                font-style: italic;
            }}
        """)
    
    def restore_item_colors(self, item):
        """Restore original colors untuk tree item"""
        # Ensure programmatic flag is set untuk color changes
        was_programmatic = self.main_window.is_programmatic_change if self.main_window else False
        if not was_programmatic and self.main_window:
            self.main_window.is_programmatic_change = True
        
        # Get the type name from the item (column 0)
        type_name = item.text(0)
        if hasattr(self.main_window, 'get_type_color'):
            # Restore the original type color
            type_color = self.main_window.get_type_color(type_name)
            item.setForeground(0, QColor(type_color))
        else:
            # Fallback to default color if get_type_color not available
            item.setForeground(0, QColor("#e1e1e1"))
        
        # Set default colors for other columns
        item.setForeground(1, QColor("#e1e1e1"))  # Name column
        item.setForeground(2, QColor("#e1e1e1"))  # Value column
        
        # Reset flag hanya jika kita yang set
        if not was_programmatic and self.main_window:
            self.main_window.is_programmatic_change = False
    
    def clear_search(self):
        """Clear search results dan restore original appearance"""
        # Stop search timer jika ada
        self.search_timer.stop()
        
        # Set flag untuk mencegah itemChanged signal
        if self.main_window:
            self.main_window.is_programmatic_change = True
        
        # Show all items dan restore colors
        self.show_all_items()
        
        # Clear search results list
        self.search_results = []
        
        # Clear search input
        self.search_input.clear()
        
        # Reset search status
        self.search_status.setText("Siap untuk mencari...")
        self.search_status.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 4px 8px;
        """)
        
        # Reset search input style
        self.update_search_input_style("#404040")
        
        # Reset window title
        self.tree.window().setWindowTitle("Bedrock NBT/DAT Editor")
        
        # Tree widget doesn't need row hiding, all items are visible by default
        
        # Reset flag setelah selesai programmatic changes
        if self.main_window:
            self.main_window.is_programmatic_change = False