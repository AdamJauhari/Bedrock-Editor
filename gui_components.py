from PyQt5.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os

class GUIComponents:
    """Utility class for GUI components and styling"""
    
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
                GUIComponents._set_default_icon(icon_label)
        else:
            GUIComponents._set_default_icon(icon_label)
        
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
    def get_toolbar_style():
        """Get toolbar styling"""
        return """
            QToolBar {
                background-color: #23272e;
                border: none;
                spacing: 10px;
                padding: 8px;
            }
            QToolBar QToolButton {
                background-color: #00d084;
                color: white;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 2px;
            }
            QToolBar QToolButton:hover {
                background-color: #00b36b;
            }
            QToolBar QToolButton:pressed {
                background-color: #009658;
            }
        """
    
    @staticmethod
    def get_author_label_style():
        """Get author label styling"""
        return """
            color: #00bfff;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 8px 15px;
            margin: 0px 15px;
            background-color: rgba(0, 191, 255, 0.1);
            border: 1px solid rgba(0, 191, 255, 0.3);
            border-radius: 6px;
            line-height: 1.3;
        """
    
    @staticmethod
    def get_world_list_style():
        """Get world list styling"""
        return """
            QListWidget {
                background-color: #23272e;
                color: #e1e1e1;
                font-size: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0px;
                border-radius: 6px;
                background-color: transparent;
            }
            QListWidget::item:hover {
                background-color: #2d3139;
                border: 1px solid #0078d4;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """
    
    @staticmethod
    def get_search_input_style():
        """Get search input styling"""
        return """
            QLineEdit {
                background-color: #2d3139;
                color: #e1e1e1;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid #404040;
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #00bfff;
                background-color: #23272e;
            }
            QLineEdit::placeholder {
                color: #888888;
                font-style: italic;
            }
        """
    
    @staticmethod
    def get_clear_search_button_style():
        """Get clear search button styling"""
        return """
            QPushButton {
                background-color: #404040;
                color: #e1e1e1;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """
    
    @staticmethod
    def get_tree_widget_style():
        """Get tree widget styling"""
        return """
            QTreeWidget {
                background-color: #23272e;
                color: #e1e1e1;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 8px;
                selection-background-color: #0078d4;
                outline: none;
                gridline-color: #404040;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                margin: 1px 0px;
                border-radius: 4px;
                color: #e1e1e1;
                background-color: transparent;
            }
            QTreeWidget::item:hover {
                background-color: #2d3139;
                color: #ffffff;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTreeWidget::item:alternate {
                background-color: #1e2328;
            }
            QTreeWidget QLineEdit {
                background-color: #2d3139 !important;
                color: #ffffff !important;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 3px solid #ff6b35 !important;
                border-radius: 6px;
                padding: 6px 12px;
                selection-background-color: #4da6ff !important;
                selection-color: #ffffff !important;
                min-height: 20px;
            }
            QTreeWidget QLineEdit:focus {
                border: 4px solid #ff9500 !important;
                background-color: #2d3139 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #1e2328;
                color: #00bfff;
                font-weight: bold;
                font-size: 15px;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #404040;
                border-bottom: 2px solid #00bfff;
            }
            QHeaderView::section:hover {
                background-color: #2d3139;
            }
        """
    
    @staticmethod
    def get_message_box_style():
        """Get message box styling"""
        return """
            QMessageBox {
                background-color: #23272e;
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #00d084;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
                margin: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #00b36b;
                transform: scale(1.05);
            }
            QMessageBox QPushButton:pressed {
                background-color: #009658;
                transform: scale(0.95);
            }
        """
    
    @staticmethod
    def get_error_message_box_style():
        """Get error message box styling"""
        return """
            QMessageBox {
                background-color: #23272e;
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #ff0000;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
                margin: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #cc0000;
                transform: scale(1.05);
            }
            QMessageBox QPushButton:pressed {
                background-color: #990000;
                transform: scale(0.95);
            }
        """
    
    @staticmethod
    def get_warning_message_box_style():
        """Get warning message box styling"""
        return """
            QMessageBox {
                background-color: #23272e;
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #ff9500;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
                margin: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #e6850e;
                transform: scale(1.05);
            }
            QMessageBox QPushButton:pressed {
                background-color: #cc7700;
                transform: scale(0.95);
            }
        """
    
    @staticmethod
    def get_confirmation_dialog_style():
        """Get confirmation dialog styling"""
        return """
            QMessageBox {
                background-color: #23272e;
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #00bfff;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-width: 100px;
                margin: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #0099cc;
                transform: scale(1.05);
            }
            QMessageBox QPushButton:pressed {
                background-color: #0077aa;
                transform: scale(0.95);
            }
        """
