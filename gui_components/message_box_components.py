"""
Message Box Components
Contains styling for different types of message boxes
"""

class MessageBoxComponents:
    """Message box styling components"""
    
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
            }
            QMessageBox QPushButton:pressed {
                background-color: #009658;
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
            }
            QMessageBox QPushButton:pressed {
                background-color: #990000;
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
            }
            QMessageBox QPushButton:pressed {
                background-color: #cc7700;
            }
        """
