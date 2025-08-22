# Bedrock NBT/DAT Editor

A Python GUI application for editing Minecraft Bedrock Edition NBT and DAT files, particularly `level.dat` files.

## Features

- **World Browser**: Automatically detects and lists Minecraft Bedrock worlds
- **NBT Editor**: View and edit NBT data in a tree structure
- **Live Search**: Filter NBT keys in real-time
- **File Support**: Supports `.nbt`, `.dat`, `.snbt`, and `.txt` files
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.7 or higher
- PyQt5
- nbtlib
- amulet-nbt (optional, for enhanced Bedrock support)

## Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install PyQt5 nbtlib
   ```
3. Run the program:
   ```bash
   python main.py
   ```

## Usage

1. **Launch the program**: Run `python main.py`
2. **Select a world**: Click on a world from the left sidebar
3. **Browse NBT data**: The center panel shows the NBT structure
4. **Search**: Use the search box to filter keys
5. **Edit values**: Double-click on values to edit them
6. **Save changes**: Use the save button in the toolbar

## Features

### World Detection
The program automatically finds Minecraft Bedrock worlds in the default locations:
- **Windows**: `%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_*\LocalState\games\com.mojang\minecraftWorlds`
- **macOS**: `~/Library/Application Support/mcpelauncher/games/com.mojang/minecraftWorlds`
- **Linux**: `~/.local/share/mcpelauncher/games/com.mojang/minecraftWorlds`

### NBT Parsing
- Supports both Bedrock and Java Edition NBT formats
- Uses multiple parsing methods for maximum compatibility
- Fallback to manual parsing for problematic files

### Search and Filter
- Real-time search as you type
- Highlights matching items
- Shows result count
- Easy to clear search and show all items

### Editing
- Inline editing of NBT values
- Confirmation dialogs for changes
- Color-coded data types (integers, floats, strings)

## File Formats Supported

- **NBT files** (`.nbt`): Binary NBT format
- **DAT files** (`.dat`): Minecraft data files (usually NBT)
- **SNBT files** (`.snbt`): String NBT format
- **Text files** (`.txt`): Simple key-value format

## Troubleshooting

### Common Issues

1. **"amulet-nbt not available"**: This is normal - the program works with just nbtlib
2. **No worlds found**: Make sure Minecraft Bedrock is installed and you have created worlds
3. **Permission errors**: Run as administrator if needed for system folders

### Testing

Run the test script to verify everything works:
```bash
python test_program.py
```

## Author

**Adam Arias Jauhari**

## License

This project is open source. Feel free to modify and distribute.

## Contributing

Feel free to submit issues and enhancement requests!
