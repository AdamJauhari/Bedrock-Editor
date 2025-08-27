"""
File Operations
Handles file opening, saving, and NBT data management
"""

import os
from typing import Any
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from .message_box_components import MessageBoxComponents

class FileOperations:
    """Handles file operations for NBT files"""
    
    def __init__(self, main_window):
        self.main_window = main_window
    
    def open_file(self):
        """Open NBT file manually"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window, 
            "Buka File NBT/DAT", 
            "", 
            "NBT/DAT Files (*.nbt *.dat)"
        )
        if file_path:
            # Set flag immediately to prevent any itemChanged signals during file loading
            self.main_window.is_programmatic_change = True
            
            # Clear current data and state before loading new file
            self.main_window.clear_current_data()
            
            self.main_window.nbt_file = file_path
            try:
                # Try custom NBT parser first
                print(f"Loading {file_path} with custom NBT parser...")
                self.main_window.nbt_reader = self.main_window.nbt_reader_class()
                self.main_window.nbt_data = self.main_window.nbt_reader.read_nbt_file(file_path)
                
                # If custom parser returns empty data, try nbtlib as fallback
                if not self.main_window.nbt_data or len(self.main_window.nbt_data) == 0:
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
                msg.setText(f"Gagal membuka file: {e}")
                msg.setStyleSheet(MessageBoxComponents.get_error_message_box_style())
                msg.exec_()
            finally:
                # Always reset flag regardless of success or failure
                self.main_window.is_programmatic_change = False
    
    def save_file(self):
        """Save current data to file using NBTEditor"""
        if self.main_window.nbt_file and self.main_window.nbt_data:
            try:
                print(f"💾 Saving file: {self.main_window.nbt_file}")
                
                # Initialize NBTEditor if not already done
                if self.main_window.nbt_editor is None:
                    self.main_window.nbt_editor = self.main_window.nbt_editor_class(self.main_window.nbt_file)
                    self.main_window.nbt_editor.load_file()
                
                # Check if there are any modifications to save
                if not self.main_window.nbt_editor.has_modifications():
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Info")
                    msg.setText("Tidak ada perubahan yang perlu disimpan.")
                    msg.setStyleSheet(MessageBoxComponents.get_message_box_style())
                    msg.exec_()
                    return
                
                # Get modified fields
                modified_fields = self.main_window.nbt_editor.get_modified_fields()
                
                # Save the file
                if self.main_window.nbt_editor.save_file(backup=True):
                    # Success message
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Sukses")
                    msg.setText(f"File berhasil disimpan!\n\nPerubahan yang disimpan:\n" + 
                              "\n".join([f"• {field}" for field in modified_fields[:10]]) + 
                              (f"\n...dan {len(modified_fields) - 10} field lainnya" if len(modified_fields) > 10 else ""))
                    msg.setStyleSheet(MessageBoxComponents.get_message_box_style())
                    msg.exec_()
                    
                    # Update window title to remove modification indicator
                    self.main_window.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser)")
                else:
                    raise Exception("Failed to save file")
                    
            except Exception as e:
                print(f"❌ Save error: {e}")
                import traceback
                traceback.print_exc()
                
                msg = QMessageBox(self.main_window)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal menyimpan file: {e}")
                msg.setStyleSheet(MessageBoxComponents.get_error_message_box_style())
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Peringatan")
            msg.setText("Tidak ada file yang terbuka untuk disimpan!")
            msg.setStyleSheet(MessageBoxComponents.get_warning_message_box_style())
            msg.exec_()
    
    def clear_current_data(self):
        """Clear current data and reset state"""
        try:
            print("🧹 Clearing current data and state...")
            
            # Clear tree widget
            self.main_window.tree.clear()
            
            # Clear search results
            if hasattr(self.main_window, 'search_utils'):
                self.main_window.search_utils.clear_search()
            
            # Reset data references
            self.main_window.nbt_data = None
            self.main_window.nbt_file = None
            self.main_window.nbt_reader = None
            self.main_window.nbt_editor = None  # NBT file editor instance
            
            # Reset window title
            self.main_window.setWindowTitle("Bedrock NBT/DAT Editor (Generic Parser)")
            
            # Clear any pending operations
            if hasattr(self.main_window, 'search_timer') and self.main_window.search_timer.isActive():
                self.main_window.search_timer.stop()
            
            print("✅ Current data cleared successfully")
            
        except Exception as e:
            print(f"❌ Error clearing current data: {e}")
    
    def convert_value_to_type(self, text_value: str, original_value: Any, type_name: str) -> Any:
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
