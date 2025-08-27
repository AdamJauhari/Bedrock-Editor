"""
GUI Components Package
Contains modular GUI components for the Bedrock NBT Editor
"""

from .world_list_components import WorldListComponents
from .styling_components import StylingComponents, EnhancedTypeDelegate
from .message_box_components import MessageBoxComponents
from .button_components import ButtonComponents
from .admin_utils import is_admin, run_as_admin, check_admin_privileges
from .world_manager import WorldManager
from .file_operations import FileOperations
from .tree_manager import TreeManager

# For backward compatibility
class GUIComponents:
    """Legacy class that combines all GUI components"""
    
    # World List Components
    create_world_list_item = WorldListComponents.create_world_list_item
    _set_default_icon = WorldListComponents._set_default_icon
    get_world_item_hover_style = WorldListComponents.get_world_item_hover_style
    get_world_item_selected_style = WorldListComponents.get_world_item_selected_style
    
    # Styling Components
    get_toolbar_style = StylingComponents.get_toolbar_style
    get_author_label_style = StylingComponents.get_author_label_style
    get_world_list_style = StylingComponents.get_world_list_style
    get_search_input_style = StylingComponents.get_search_input_style
    get_clear_search_button_style = StylingComponents.get_clear_search_button_style
    get_tree_widget_style = StylingComponents.get_tree_widget_style
    get_enhanced_tree_style = StylingComponents.get_enhanced_tree_style
    get_main_window_style = StylingComponents.get_main_window_style
    get_status_bar_style = StylingComponents.get_status_bar_style
    get_scroll_bar_style = StylingComponents.get_scroll_bar_style
    get_type_indicator_style = StylingComponents.get_type_indicator_style

    
    # Message Box Components
    get_message_box_style = MessageBoxComponents.get_message_box_style
    get_error_message_box_style = MessageBoxComponents.get_error_message_box_style
    get_warning_message_box_style = MessageBoxComponents.get_warning_message_box_style
    
    # Button Components
    get_button_style = ButtonComponents.get_button_style
    get_secondary_button_style = ButtonComponents.get_secondary_button_style
    get_danger_button_style = ButtonComponents.get_danger_button_style
    get_warning_button_style = ButtonComponents.get_warning_button_style
    get_info_button_style = ButtonComponents.get_info_button_style

__all__ = [
    'GUIComponents',
    'WorldListComponents', 
    'StylingComponents',
    'MessageBoxComponents',
    'ButtonComponents',
    'EnhancedTypeDelegate',
    'is_admin',
    'run_as_admin', 
    'check_admin_privileges',
    'WorldManager',
    'FileOperations',
    'TreeManager'
]
