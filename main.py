#!/usr/bin/env python3
"""
Bedrock NBT/DAT Editor
Main entry point for the application

This file serves as the entry point for the Bedrock NBT/DAT Editor application.
The actual application logic has been separated into multiple modules for better organization:

- package_manager.py: Handles package installation and imports
- minecraft_paths.py: Manages Minecraft world path detection
- nbt_utils.py: NBT conversion and utility functions
- bedrock_parser.py: Dynamic Bedrock NBT parsing with key detection
- search_utils.py: Search and filtering functionality
- gui_components.py: GUI styling and components
- main_app.py: Main application class and logic

Author: Adam Arias Jauhari
"""

# Import and run the main application
from main_app import NBTEditor
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditor()
    window.show()
    sys.exit(app.exec_())
