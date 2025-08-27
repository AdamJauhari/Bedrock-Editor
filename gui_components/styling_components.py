"""
Styling Components
Contains all CSS styling for the GUI components
"""

from PyQt5.QtWidgets import QStyledItemDelegate, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap, QLinearGradient
from PyQt5.QtCore import Qt, QRect

class StylingComponents:
    """CSS styling for GUI components"""
    
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
                alternate-background-color: #1e2328;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                margin: 2px 0px;
                border-radius: 6px;
                background-color: transparent;
            }
            QTreeWidget::item:hover {
                background-color: #2d3139;
                border: 1px solid #0078d4;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #2d3139;
                color: #ffffff;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTreeWidget::branch {
                background-color: transparent;
                width: 25px;
                height: 20px;
                margin-left: -5px;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: none;
                border-image: none;
                background-color: transparent;
                color: #00bfff;
                font-size: 18px;
                font-weight: bold;
                padding-left: 0px;
                text-align: center;
                border: none;
                border-radius: 0px;
                margin-left: -5px;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: none;
                border-image: none;
                background-color: transparent;
                color: #00bfff;
                font-size: 18px;
                font-weight: bold;
                padding-left: 0px;
                text-align: center;
                border: none;
                border-radius: 0px;
                margin-left: -5px;
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
    def get_main_window_style():
        """Get main window styling"""
        return """
            QMainWindow {
                background-color: #181a20;
            }
        """
    
    @staticmethod
    def get_status_bar_style():
        """Get status bar styling"""
        return """
            QStatusBar {
                background-color: #23272e;
                color: #00bfff;
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                border-top: 1px solid #404040;
                padding: 6px;
            }
        """
    
    @staticmethod
    def get_scroll_bar_style():
        """Get scroll bar styling"""
        return """
            QScrollBar:vertical {
                background-color: #2d3139;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 5px;
                min-height: 20px;
                margin: 1px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #2d3139;
                height: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #404040;
                border-radius: 5px;
                min-width: 20px;
                margin: 1px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #555555;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """
    
    @staticmethod
    def get_type_indicator_style(type_name):
        """Get attractive styling for type indicators"""
        base_style = """
            QLabel {
                font-weight: bold;
                font-size: 12px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border-radius: 4px;
                padding: 2px 6px;
                margin: 1px;
                min-width: 20px;
                text-align: center;
            }
        """
        
        # Define colors and styles for different types
        type_styles = {
            'B': f"""
                {base_style}
                QLabel {{
                    background-color: #ff4444;
                    color: white;
                    border: 1px solid #cc3333;
                }}
            """,
            'I': f"""
                {base_style}
                QLabel {{
                    background-color: #00d084;
                    color: white;
                    border: 1px solid #00b36b;
                }}
            """,
            'L': f"""
                {base_style}
                QLabel {{
                    background-color: #4169e1;
                    color: white;
                    border: 1px solid #3158d1;
                }}
            """,
            'F': f"""
                {base_style}
                QLabel {{
                    background-color: #ffaa00;
                    color: white;
                    border: 1px solid #e69500;
                }}
            """,
            'D': f"""
                {base_style}
                QLabel {{
                    background-color: #ff00ff;
                    color: white;
                    border: 1px solid #cc00cc;
                }}
            """,
            'S': f"""
                {base_style}
                QLabel {{
                    background-color: #00bfff;
                    color: white;
                    border: 1px solid #0099cc;
                }}
            """,
            '📁': f"""
                {base_style}
                QLabel {{
                    background-color: #ff9500;
                    color: white;
                    border: 1px solid #e6850e;
                }}
            """,
            '📄': f"""
                {base_style}
                QLabel {{
                    background-color: #800080;
                    color: white;
                    border: 1px solid #660066;
                }}
            """,
            'BA': f"""
                {base_style}
                QLabel {{
                    background-color: #ff4500;
                    color: white;
                    border: 1px solid #cc3700;
                }}
            """,
            'IA': f"""
                {base_style}
                QLabel {{
                    background-color: #4169e1;
                    color: white;
                    border: 1px solid #3158d1;
                }}
            """,
            'LA': f"""
                {base_style}
                QLabel {{
                    background-color: #8a2be2;
                    color: white;
                    border: 1px solid #6b1fcc;
                }}
            """
        }
        
        return type_styles.get(type_name, f"""
            {base_style}
            QLabel {{
                background-color: #666666;
                color: white;
                border: 1px solid #555555;
            }}
        """)
    
    @staticmethod
    def get_type_color_enhanced(type_name):
        """Get enhanced color scheme for type indicators"""
        colors = {
            'B': '#ff4444',    # Bright Red for Boolean/Byte
            'I': '#00d084',    # Bright Green for Integer
            'L': '#4169e1',    # Royal Blue for Long
            'F': '#ffaa00',    # Bright Orange for Float
            'D': '#ff00ff',    # Magenta for Double
            'S': '#00bfff',    # Bright Blue for String
            '📁': '#ff9500',   # Orange for Compound
            '📄': '#800080',   # Purple for List
            'BA': '#ff4500',   # Orange Red for Byte Array
            'IA': '#4169e1',   # Royal Blue for Int Array
            'LA': '#8a2be2',   # Blue Violet for Long Array
        }
        return colors.get(type_name, '#666666')  # Gray for unknown types

    @staticmethod
    def get_enhanced_tree_style():
        """Get enhanced tree widget styling with better type column appearance"""
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
                alternate-background-color: #1e2328;
            }
            QTreeWidget::item {
                padding: 8px 12px;
                margin: 3px 0px;
                border-radius: 8px;
                background-color: transparent;
            }
            QTreeWidget::item:hover {
                background-color: #2d3139;
                border: 1px solid #0078d4;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #1e2328;
                color: #00bfff;
                font-weight: bold;
                font-size: 15px;
                padding: 12px 8px;
                border: none;
                border-right: 1px solid #404040;
                border-bottom: 2px solid #00bfff;
            }
            QHeaderView::section:hover {
                background-color: #2d3139;
            }
        """

class EnhancedTypeDelegate(QStyledItemDelegate):
    """Custom delegate for enhanced type display with attractive badges and branch indicators"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        if index.column() == 0:  # Only for type column
            self.paint_type_badge(painter, option, index)
            # Also paint branch indicators for items with children
            self.paint_branch_indicator(painter, option, index)
        else:
            super().paint(painter, option, index)
    
    def paint_type_badge(self, painter, option, index):
        """Paint type indicator as an attractive badge"""
        painter.save()
        
        # Get the type text
        type_text = index.data()
        if not type_text:
            painter.restore()
            return
        
        # Calculate badge dimensions
        rect = option.rect
        badge_width = min(rect.width() - 8, 40)  # Fixed width for consistency
        badge_height = min(rect.height() - 4, 28)  # Fixed height for consistency
        
        # Center the badge in the cell
        badge_x = rect.x() + (rect.width() - badge_width) // 2
        badge_y = rect.y() + (rect.height() - badge_height) // 2
        badge_rect = QRect(badge_x, badge_y, badge_width, badge_height)
        
        # Draw background with gradient (but not for compound and list types)
        if type_text not in ['📁', '📄']:
            self.draw_badge_background(painter, badge_rect, type_text)
            # Draw text with white color for types with background
            painter.setPen(QColor("white"))
        else:
            # For compound and list types, draw text with colored text (no background)
            if type_text == '📁':
                painter.setPen(QColor("#ff9500"))  # Orange for compound
            else:  # 📄
                painter.setPen(QColor("#800080"))  # Purple for list
        
        # Set font
        font = QFont("Segoe UI", 11, QFont.Bold)
        if type_text in ['📁', '📄']:
            font.setPointSize(14)  # Larger font for emoji types
        painter.setFont(font)
        
        # Center text in badge
        text_rect = badge_rect
        painter.drawText(text_rect, Qt.AlignCenter, type_text)
        
        painter.restore()
    
    def paint_branch_indicator(self, painter, option, index):
        """Paint branch indicators (arrows) for expandable items"""
        tree_widget = self.parent()
        if tree_widget:
            item = tree_widget.itemFromIndex(index)
            if item and item.childCount() > 0:
                # Draw arrow symbol
                painter.save()
                painter.setPen(QColor("#00bfff"))
                font = QFont("Segoe UI", 12, QFont.Bold)
                painter.setFont(font)
                
                # Position for arrow - move to the left to avoid collision with type
                rect = option.rect
                x = rect.x() - 20  # Move further left to avoid type column
                y = rect.y() + rect.height() // 2 + 4
                
                # Draw arrow based on expanded state
                if item.isExpanded():
                    painter.drawText(x, y, "▼")
                else:
                    painter.drawText(x, y, "▶")
                
                painter.restore()
    
    def draw_badge_background(self, painter, rect, type_text):
        """Draw attractive gradient background for badge"""
        # Define gradient colors based on type
        gradient_colors = {
            'B': ('#ff6b6b', '#ff4444'),      # Red gradient
            'I': ('#51cf66', '#00d084'),      # Green gradient
            'L': ('#74c0fc', '#4169e1'),      # Blue gradient
            'F': ('#ffd43b', '#ffaa00'),      # Yellow gradient
            'D': ('#f783ac', '#ff00ff'),      # Magenta gradient
            'S': ('#4dabf7', '#00bfff'),      # Cyan gradient
            '📁': ('#ffb84d', '#ff9500'),     # Orange gradient
            '📄': ('#cc99ff', '#800080'),     # Purple gradient
            'BA': ('#ff8a65', '#ff4500'),     # Orange-red gradient
            'IA': ('#74c0fc', '#4169e1'),     # Blue gradient
            'LA': ('#b197fc', '#8a2be2'),     # Purple gradient
        }
        
        start_color, end_color = gradient_colors.get(type_text, ('#adb5bd', '#666666'))
        
        # Create gradient
        gradient = QLinearGradient(rect.x(), rect.y(), rect.x(), rect.y() + rect.height())
        gradient.setColorAt(0, QColor(start_color))
        gradient.setColorAt(1, QColor(end_color))
        
        # Draw rounded rectangle with gradient
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 8, 8)
        
        # Add subtle border
        border_color = QColor(end_color)
        border_color.setAlpha(150)
        painter.setPen(border_color)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, 8, 8)
