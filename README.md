# Bedrock NBT/DAT Editor

A powerful GUI application for editing Minecraft Bedrock Edition NBT/DAT files with a modern, user-friendly interface.

## Features

- **Modern Dark Theme**: Beautiful dark UI with blue accents
- **World Browser**: Automatically detects and lists Minecraft Bedrock worlds
- **Live Search**: Real-time filtering of NBT data with highlighting
- **Multi-Format Support**: Supports NBT, DAT, SNBT, and text files
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Multiple Parsers**: Uses both nbtlib and amulet-nbt for maximum compatibility
- **Manual Parser**: Custom parser for problematic Bedrock level.dat files
- **Inline Editing**: Double-click to edit values with confirmation dialogs

### 🎯 User Experience
- **Visual Feedback**: Enhanced status bar with real-time updates
- **Modern Styling**: Consistent design language throughout the application
- **Intuitive Interface**: Improved layout and navigation
- **Professional Look**: Clean, modern appearance suitable for professional use

### 🌳 Enhanced Branch Indicators
- **Beautiful Arrow Design**: Replaced default branch indicators with custom styled arrows
- **Clear Visual Hierarchy**: Distinct styling for expanded (▼) and collapsed (▶) states
- **Consistent Branding**: Branch indicators use the same blue accent color (#00bfff) as other UI elements
- **Better UX**: More intuitive and visually appealing tree navigation
- **Modern Typography**: Uses Segoe UI font with bold weight for better readability

### 📄📁 Visual Type Indicators
- **Emoji Type Icons**: List types display as 📄 and Compound types display as 📁
- **Intuitive Visual Cues**: Easy to distinguish between different NBT data structures
- **Consistent Color Coding**: Each type maintains its distinct color scheme
- **Enhanced Readability**: Visual icons make it easier to scan and understand data structure

### 🎨 Enhanced Type Display
- **Attractive Badge Design**: Type indicators now display as colorful badges with rounded corners
- **Icon Integration**: Each type includes a relevant emoji icon for better visual recognition
- **Gradient Backgrounds**: Beautiful gradient backgrounds for each type with subtle shadows
- **Professional Appearance**: Modern, polished look that enhances the overall user experience
- **Improved Spacing**: Better column sizing and padding for optimal readability

## Project Structure

The application has been modularized for better maintainability and organization:

### Core Files
- **`main.py`**: Entry point for admin mode - imports and runs the application with administrator privileges
- **`main_no_admin.py`**: Entry point for no-admin mode - runs without requiring administrator privileges for development/testing
- **`app.manifest`**: Windows manifest file for administrator privileges
- **`create_shortcut.bat`**: Batch script to create desktop shortcut with admin privileges

### Modular Components

#### 📁 `gui_components/` - GUI Components Package
- **`__init__.py`**: Package initialization and exports
- **`admin_utils.py`**: Administrator privileges handling and elevation
- **`world_manager.py`**: Minecraft world loading and management
- **`file_operations.py`**: File opening, saving, and NBT data management
- **`tree_manager.py`**: NBT data tree display and editing functionality
- **`styling_components.py`**: CSS styling for all GUI components
- **`button_components.py`**: Button styling and interactive elements
- **`message_box_components.py`**: Message box styling for different types
- **`world_list_components.py`**: World list item creation and display

#### 📁 `nbt_utility/` - NBT Utility Package
- **`__init__.py`**: Package initialization and exports
- **`nbt_editor.py`**: NBT file editing and saving functionality
- **`nbt_reader/`**: NBT reading and parsing components
  - **`__init__.py`**: Package initialization
  - **`bedrock_nbt_parser.py`**: Bedrock NBT parser for table format conversion
  - **`raw_nbt_reader.py`**: Raw NBT file reading and parsing

#### 📁 `resource/` - Resource Package
- **`__init__.py`**: Package initialization and exports
- **`minecraft_paths.py`**: Minecraft world path detection across platforms
- **`package_manager.py`**: Package installation and dependency management
- **`search_utils.py`**: Search and filtering functionality

### Assets
- **`icon.png`**: Application icon
- **`README.md`**: This documentation file

## Installation

1. **Automatic Installation**: The application automatically installs required packages:
   - PyQt5 (GUI framework)
   - nbtlib (NBT parsing)
   - amulet-nbt (optional, for better Bedrock support)

2. **Run the Application**:

   **Admin Mode** (Full functionality):
   ```bash
   python main.py
   ```

   **No-Admin Mode** (Development/Testing):
   ```bash
   python main_no_admin.py
   ```

   **Create Desktop Shortcut** (Windows):
   ```bash
   create_shortcut.bat
   ```

## Usage

### Opening Worlds
1. The application automatically scans for Minecraft Bedrock worlds
2. Click on any world in the left sidebar to load its level.dat file
3. The NBT data will be displayed in a tree structure on the right

### Opening Files
1. Use File → Open or the toolbar button
2. Supported formats: `.nbt`, `.dat`, `.snbt`, `.txt`
3. The application will automatically detect the file format and parse accordingly

### Searching
1. Use the search box to filter NBT keys
2. Live search updates as you type
3. Matching items are highlighted in orange
4. Click "Tampilkan Semua" to clear the search

### Editing Values
1. Double-click on any value in the tree
2. Enter the new value
3. Confirm the change in the dialog
4. Use the save button to persist changes

## Technical Details

### NBT Parsing Strategy
The application uses a multi-layered approach to parse NBT files:

1. **Format Detection**: Analyzes magic bytes to determine file format
2. **Primary Parser**: Uses amulet-nbt for Bedrock files (if available)
3. **Fallback Parser**: Uses nbtlib for Java files or as fallback
4. **Manual Parser**: Custom parser for problematic Bedrock level.dat files

### Cross-Platform Support
The application automatically detects Minecraft world paths on:
- **Windows**: `%APPDATA%\Local\Packages\Microsoft.MinecraftUWP_*\LocalState\games\com.mojang\minecraftWorlds`
- **macOS**: `~/Library/Application Support/mcpelauncher/games/com.mojang/minecraftWorlds`
- **Linux**: `~/.local/share/mcpelauncher/games/com.mojang/minecraftWorlds`

### Search Implementation
- **Debounced Search**: 300ms delay to prevent excessive filtering
- **Recursive Filtering**: Searches through all nested NBT structures
- **Visual Feedback**: Highlights matches and shows result counts
- **Performance Optimized**: Efficient tree traversal and filtering

## Development

### Adding New Features
1. **GUI Components**: Add new components to `gui_components/` package
2. **NBT Utilities**: Add new functionality to `nbt_utility/` package
3. **Search Features**: Extend `resource/search_utils.py` with new filtering options
4. **Styling**: Add new styles to `gui_components/styling_components.py`

### Code Organization
- **Modular Architecture**: Each package has a specific responsibility
- **Separation of Concerns**: GUI, NBT, and resource components are separated
- **Reusable Components**: GUI styling and utilities are centralized in packages
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Documentation**: Inline comments and docstrings for maintainability
- **Package Structure**: Clear organization with `__init__.py` files for proper imports

## Troubleshooting

### Common Issues
1. **No Worlds Found**: Check if Minecraft Bedrock is installed and has worlds
2. **Parse Errors**: The application will try multiple parsing methods automatically
3. **Save Failures**: Ensure the file isn't being used by Minecraft

### Debug Information
The application provides detailed console output for debugging:
- Parser selection and results
- World path detection
- Search performance metrics

## License

This project is open source and available

## Author

**Adam Arias Jauhari**

---

*Built with PyQt5 and Python 3.6+*
