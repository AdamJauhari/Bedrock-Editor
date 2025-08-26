"""
World List Components
Handles world list item creation and display
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os

class WorldListComponents:
    """Components for world list display"""
    
    @staticmethod
    def create_world_list_item(world_name, icon_path, world_path):
        """Create a custom world list item with icon and name"""
        item_widget = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(15, 15, 15, 15)
        vbox.setSpacing(10)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(130, 90)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(130, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
                icon_label.setStyleSheet("""
                    background-color: #1e2328;
                    border: 2px solid #404040;
                    border-radius: 8px;
                    margin-bottom: 4px;
                """)
            else:
                WorldListComponents._set_default_icon(icon_label)
        else:
            WorldListComponents._set_default_icon(icon_label)
        
        vbox.addWidget(icon_label, alignment=Qt.AlignHCenter)
        
        # Nama world dengan spacing yang cukup
        name_label = QLabel(world_name)
        name_label.setStyleSheet("""
            color: #e1e1e1;
            font-size: 14px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 8px 10px;
            margin-top: 8px;
            background-color: rgba(30, 35, 40, 0.9);
            border: 1px solid rgba(0, 191, 255, 0.3);
            border-radius: 8px;
        """)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(50)  # Batasi tinggi untuk mencegah overlap
        vbox.addWidget(name_label)
        
        item_widget.setLayout(vbox)
        return item_widget
    
    @staticmethod
    def _set_default_icon(icon_label):
        """Set default icon for world items"""
        icon_label.setText("🌍")
        icon_label.setStyleSheet("""
            background-color: #2d3139;
            color: #00bfff;
            border: 2px solid #404040;
            border-radius: 8px;
            font-size: 32px;
            margin-bottom: 4px;
        """)
    
    @staticmethod
    def _get_short_path(world_path):
        """Get shortened path for display"""
        try:
            # Extract folder name from path
            folder_name = os.path.basename(world_path)
            return f"📁 {folder_name}"
        except:
            return "📁 World"
    
    @staticmethod
    def get_world_item_hover_style():
        """Get hover style for world items"""
        return """
            QWidget {
                background-color: rgba(0, 191, 255, 0.05);
                border: 1px solid rgba(0, 191, 255, 0.2);
                border-radius: 8px;
                padding: 6px;
            }
        """
    
    @staticmethod
    def get_world_item_selected_style():
        """Get selected style for world items"""
        return """
            QWidget {
                background-color: rgba(0, 120, 212, 0.1);
                border: 1px solid #0078d4;
                border-radius: 8px;
                padding: 6px;
            }
        """
