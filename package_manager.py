import sys
import subprocess

def ensure_package(pkg):
    """Ensure a package is installed, install it if not available"""
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Install required packages
for pkg in ["PyQt5", "nbtlib"]:
    ensure_package(pkg)

# Try to import amulet-nbt for better Bedrock support (optional)
try:
    from amulet_nbt import load as amulet_load
    AMULET_AVAILABLE = True
    print("✅ amulet-nbt available for enhanced Bedrock parsing")
except ImportError:
    print("ℹ️ amulet-nbt not available, will use nbtlib for parsing")
    AMULET_AVAILABLE = False
    amulet_load = None

# Import required modules
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, 
    QAction, QMessageBox, QWidget, QVBoxLayout, QPushButton, QListWidget, 
    QLabel, QHBoxLayout, QSizePolicy, QLineEdit
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
import nbtlib
import struct
