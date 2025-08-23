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
        
        def collect_and_filter_items(parent_item):
            """Recursively collect dan filter tree items"""
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                all_items.append(child)
                key_text = child.text(0).lower()
                
                # Check if search term matches key name
                if search_text.lower() in key_text:
                    found_items.append(child)
                    # Highlight the found item
                    child.setBackground(0, QColor("#ff6b35"))  # Orange background for key
                    child.setBackground(1, QColor("#ff6b35"))  # Orange background for value
                    child.setForeground(0, QColor("#ffffff"))  # White text for key
                    child.setForeground(1, QColor("#ffffff"))  # White text for value
                    
                    # Show this item dan semua parent-nya
                    child.setHidden(False)
                    parent = child.parent()
                    while parent and parent != self.tree.invisibleRootItem():
                        parent.setHidden(False)
                        self.tree.expandItem(parent)
                        parent = parent.parent()
                else:
                    # Hide item yang tidak cocok
                    child.setHidden(True)
                
                # Continue searching in children
                collect_and_filter_items(child)
        
        # Start search from root
        collect_and_filter_items(self.tree.invisibleRootItem())
        
        # Store results and update UI
        self.search_results = found_items
        
        if found_items:
            # Scroll to first result and select it
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
            # Show no results status - hide semua items
            for item in all_items:
                item.setHidden(True)
            
            self.search_status.setText(f"✗ Tidak ada hasil untuk '{search_text}' - {len(all_items)} item disembunyikan")
            self.search_status.setStyleSheet("""
                color: #ff6b6b;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 4px 8px;
                font-weight: bold;
            """)
            
            # Red border untuk no results
            self.update_search_input_style("#ff6b6b")
        
        # Reset flag setelah selesai programmatic changes
        if self.main_window:
            self.main_window.is_programmatic_change = False
    
    def show_all_items(self):
        """Tampilkan kembali semua items yang disembunyikan dan reset colors"""
        # Set flag untuk mencegah itemChanged signal jika belum di-set
        was_programmatic = self.main_window.is_programmatic_change if self.main_window else False
        if not was_programmatic and self.main_window:
            self.main_window.is_programmatic_change = True
        
        def show_all_recursive(parent_item):
            """Recursively show all tree items"""
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                # Show the item
                child.setHidden(False)
                # Reset background dan foreground colors
                child.setBackground(0, QColor("transparent"))
                child.setBackground(1, QColor("transparent"))
                self.restore_item_colors(child)
                # Continue with children
                show_all_recursive(child)
        
        # Start from root
        show_all_recursive(self.tree.invisibleRootItem())
        
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
        """Restore original colors untuk item"""
        # Ensure programmatic flag is set untuk color changes
        was_programmatic = self.main_window.is_programmatic_change if self.main_window else False
        if not was_programmatic and self.main_window:
            self.main_window.is_programmatic_change = True
        
        key_text = item.text(0)
        value_text = item.text(1)
        
        # Set default key color
        item.setForeground(0, QColor("#e1e1e1"))
        
        # Set value color based on data type (same logic as populate_tree)
        if not value_text.endswith(" entries"):  # Not a compound/list
            # Try to determine data type from value
            try:
                # Check if it's a number
                if '.' in value_text:
                    float(value_text)
                    item.setForeground(1, QColor("#ff6b6b"))  # Light red untuk float
                else:
                    int(value_text)
                    item.setForeground(1, QColor("#4da6ff"))  # Light blue untuk angka
            except ValueError:
                # It's a string
                item.setForeground(1, QColor("#51cf66"))  # Light green untuk string
        else:
            item.setForeground(1, QColor("#e1e1e1"))  # Default light gray for compounds
        
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
        
        # Collapse all tree items untuk clean view
        self.tree.collapseAll()
        
        # Expand only first level
        if self.tree.topLevelItemCount() > 0:
            self.tree.expandToDepth(0)
        
        # Reset flag setelah selesai programmatic changes
        if self.main_window:
            self.main_window.is_programmatic_change = False