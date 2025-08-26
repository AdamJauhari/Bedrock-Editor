"""
Button Components
Contains styling for buttons and interactive elements
"""

class ButtonComponents:
    """Button styling components"""
    
    @staticmethod
    def get_button_style():
        """Get button styling"""
        return """
            QPushButton {
                background-color: #00d084;
                color: white;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                margin: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00b36b;
            }
            QPushButton:pressed {
                background-color: #009658;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888888;
            }
        """
    
    @staticmethod
    def get_secondary_button_style():
        """Get secondary button styling"""
        return """
            QPushButton {
                background-color: #404040;
                color: #e1e1e1;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 10px 16px;
                margin: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #555555;
                border: 1px solid #666666;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
                border: 1px solid #333333;
            }
        """
    
    @staticmethod
    def get_danger_button_style():
        """Get danger button styling"""
        return """
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                margin: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #cc3333;
            }
            QPushButton:pressed {
                background-color: #aa2222;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #888888;
            }
        """
    
    @staticmethod
    def get_warning_button_style():
        """Get warning button styling"""
        return """
            QPushButton {
                background-color: #ff9500;
                color: white;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                margin: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6850e;
            }
            QPushButton:pressed {
                background-color: #cc7700;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #888888;
            }
        """
    
    @staticmethod
    def get_info_button_style():
        """Get info button styling"""
        return """
            QPushButton {
                background-color: #00bfff;
                color: white;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                margin: 3px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0099cc;
            }
            QPushButton:pressed {
                background-color: #007799;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #888888;
            }
        """
