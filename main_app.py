import sys
import os
import nbtlib
import shutil
import ctypes
import subprocess

# Import our separated modules
from package_manager import *
from minecraft_paths import MINECRAFT_WORLDS_PATH
from nbt_utils import nbt_to_dict, get_nbt_value_display, convert_to_json_format, get_value_type_icon
from bedrock_parser import BedrockParser
from search_utils import SearchUtils
from gui_components import GUIComponents

# Additional imports needed for the main app
from PyQt5.QtWidgets import QListWidgetItem
import json

def is_admin():
    """Check if the current process has administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the application with administrator privileges"""
    try:
        if not is_admin():
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                " ".join(sys.argv), 
                None, 
                1
            )
            sys.exit(0)
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False
    return True

def check_admin_privileges():
    """Check and request admin privileges if needed"""
    if not is_admin():
        print("⚠️ Program membutuhkan hak akses Administrator untuk mengakses file Minecraft")
        print("🔄 Memulai ulang program dengan hak akses Administrator...")
        
        # Show message box before elevation
        from PyQt5.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Administrator Required")
        msg.setText("Program membutuhkan hak akses Administrator untuk mengakses file Minecraft.\n\nProgram akan dimulai ulang dengan hak akses Administrator.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        # Elevate privileges
        run_as_admin()
        return False
    else:
        print("✅ Program berjalan dengan hak akses Administrator")
        return True

class NBTEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Check admin privileges first
        if not check_admin_privileges():
            return  # Exit if elevation is needed
        
        self.setWindowTitle("Bedrock NBT/DAT Editor (Administrator)")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.png"))
        self.nbt_file = None
        self.nbt_data = None
        self.search_results = []  # Store search result items
        
        # Initialize Bedrock parser
        self.bedrock_parser = BedrockParser()
        
        # Timer for search debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_live_search)
        
        # Flag to prevent itemChanged signal during search/programmatic changes
        self.is_programmatic_change = False
        
        self.init_ui()
        
        # Initialize search utilities after UI is created
        self.search_utils = SearchUtils(self.tree, self.search_input, self.search_status, self.search_timer, self)
        
        # Connect search input to search utils
        self.search_input.textChanged.connect(self.search_utils.on_search_text_changed)
        
        # Connect clear search button
        self.clear_search_btn.clicked.connect(self.search_utils.clear_search)

    def init_ui(self):
        # Menu dan Toolbar
        menubar = self.menuBar()
        
        # File Menu
        open_action = QAction(QIcon(), "Buka File", self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction(QIcon(), "Simpan", self)
        save_action.triggered.connect(self.save_file)
        export_json_action = QAction(QIcon(), "Export ke JSON", self)
        export_json_action.triggered.connect(self.export_to_json)
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(export_json_action)
        
        # Toolbar dengan Save Button
        toolbar = self.addToolBar("Main")
        toolbar.setStyleSheet(GUIComponents.get_toolbar_style())
        
        # Save button di toolbar
        save_toolbar_action = QAction("💾 Simpan Perubahan", self)
        save_toolbar_action.triggered.connect(self.save_file)
        toolbar.addAction(save_toolbar_action)
        
        # Author attribution dengan format dua baris
        author_label = QLabel("Bedrock NBT/DAT Editor\nBy Adam Arias Jauhari")
        author_label.setStyleSheet(GUIComponents.get_author_label_style())
        author_label.setAlignment(Qt.AlignCenter)
        toolbar.addWidget(author_label)

        # Main widget & layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # Sidebar: World List
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        label_world = QLabel("Daftar Dunia Minecraft Bedrock")
        label_world.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        sidebar.addWidget(label_world)
        self.world_list = QListWidget()
        self.world_list.setMaximumWidth(280)
        self.world_list.setStyleSheet(GUIComponents.get_world_list_style())
        self.world_list.itemClicked.connect(self.on_world_selected)
        self.load_worlds()
        sidebar.addWidget(self.world_list)
        main_layout.addLayout(sidebar)

        # Center: NBT Tree
        center_layout = QVBoxLayout()
        label_nbt = QLabel("Isi File NBT/DAT")
        label_nbt.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        center_layout.addWidget(label_nbt)
        
        # Search Box
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        
        # Live search input field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter key - hanya tampilkan yang mengandung teks (contoh: 'crea', 'level', 'time')")
        self.search_input.setStyleSheet(GUIComponents.get_search_input_style())
        # Connect live search - will be connected after search_utils is initialized
        # self.search_input.textChanged.connect(self.search_utils.on_search_text_changed)
        
        # Search status label
        self.search_status = QLabel("Siap untuk mencari...")
        self.search_status.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            font-family: 'Segoe UI', Arial, sans-serif;
            padding: 4px 8px;
        """)
        
        # Show all items button
        self.clear_search_btn = QPushButton("👁 Tampilkan Semua")
        self.clear_search_btn.setStyleSheet(GUIComponents.get_clear_search_button_style())
        # Will connect after search_utils is initialized
        
        search_layout.addWidget(self.search_input, 1)  # Stretch factor 1 untuk mengambil lebih banyak space
        search_layout.addWidget(self.search_status)
        search_layout.addWidget(self.clear_search_btn)
        
        center_layout.addLayout(search_layout)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        
        # Set column widths untuk tabel yang lebih besar
        self.tree.setColumnWidth(0, 300)  # Key column - diperbesar
        self.tree.setColumnWidth(1, 500)  # Value column - diperbesar
        
        # Enhanced tree styling with better contrast
        self.tree.setStyleSheet(GUIComponents.get_tree_widget_style())
        
        # Set alternating row colors
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(20)
        
        center_layout.addWidget(self.tree)
        main_layout.addLayout(center_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.setStyleSheet("background-color: #181a20;")

    def clear_current_data(self):
        """Clear current data and reset state"""
        try:
            print("🧹 Clearing current data and state...")
            
            # Clear tree widget
            self.tree.clear()
            
            # Clear search results
            if hasattr(self, 'search_utils'):
                self.search_utils.clear_search()
            
            # Clear type info
            if hasattr(self, '_type_info'):
                self._type_info.clear()
                print("🧹 Cleared type info")
            
            # Reset data references
            self.nbt_data = None
            self.nbt_file = None
            
            # Reset window title
            self.setWindowTitle("Bedrock NBT/DAT Editor")
            
            # Clear any pending operations
            if hasattr(self, 'search_timer') and self.search_timer.isActive():
                self.search_timer.stop()
            
            print("✅ Current data cleared successfully")
            
        except Exception as e:
            print(f"❌ Error clearing current data: {e}")

    def load_worlds(self):
        self.world_list.clear()
        if os.path.exists(MINECRAFT_WORLDS_PATH):
            for folder in os.listdir(MINECRAFT_WORLDS_PATH):
                world_path = os.path.join(MINECRAFT_WORLDS_PATH, folder)
                level_dat = os.path.join(world_path, "level.dat")
                levelname_txt = os.path.join(world_path, "levelname.txt")
                icon_path = os.path.join(world_path, "world_icon.png")
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(world_path, "icon.png")
                if not os.path.exists(icon_path):
                    icon_path = os.path.join(world_path, "world_icon.jpeg")
                world_name = folder
                # Coba ambil dari levelname.txt
                if os.path.exists(levelname_txt):
                    try:
                        with open(levelname_txt, "r", encoding="utf-8") as f:
                            txt_name = f.read().strip()
                            if txt_name:
                                world_name = txt_name
                    except Exception:
                        pass
                # Jika tidak ada, fallback ke LevelName di level.dat
                elif os.path.exists(level_dat):
                    try:
                        nbt_data = nbtlib.load(level_dat, gzipped=True)
                        name_tag = nbt_data.root.get("LevelName")
                        if name_tag:
                            world_name = str(name_tag)
                    except Exception:
                        pass
                
                # Buat widget custom untuk world
                item_widget = GUIComponents.create_world_list_item(world_name, icon_path, world_path)
                
                # Tambahkan ke QListWidget
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.world_list.addItem(item)
                self.world_list.setItemWidget(item, item_widget)

    def on_world_selected(self, item):
        # Set flag immediately to prevent any itemChanged signals during world loading
        self.is_programmatic_change = True
        
        # Clear current data and state before loading new world
        self.clear_current_data()
        
        # Cari folder berdasarkan urutan di world_list
        idx = self.world_list.row(item)
        folder = os.listdir(MINECRAFT_WORLDS_PATH)[idx]
        world_path = os.path.join(MINECRAFT_WORLDS_PATH, folder)
        level_dat = os.path.join(world_path, "level.dat")
        
        if os.path.exists(level_dat):
            # Check file size first
            file_size = os.path.getsize(level_dat)
            if file_size < 100:  # File terlalu kecil
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"File level.dat terlalu kecil ({file_size} bytes). File mungkin kosong atau rusak.")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
                self.is_programmatic_change = False
                return
            
            self.nbt_file = level_dat
            try:
                # Deteksi format Bedrock/Java dengan magic bytes yang lebih akurat
                with open(level_dat, 'rb') as f:
                    first_8_bytes = f.read(8)
                    f.seek(0)
                    all_data = f.read(12)
                
                # Magic bytes untuk Bedrock Edition
                is_bedrock = (
                    first_8_bytes[:4] in [b'\x08\x00\x00\x00', b'\x0A\x00\x00\x00'] or  # Little endian header
                    first_8_bytes[:4] == b'\x00\x00\x00\x08' or  # Big endian
                    all_data[:4] in [b'\x08\x00\x00\x00', b'\x0A\x00\x00\x00'] or
                    len(first_8_bytes) >= 4 and first_8_bytes[0] in [0x08, 0x0A]  # NBT compound/list tag
                )
                
                # Gunakan dynamic parser yang baru untuk mendeteksi semua key
                print(f"Membaca {level_dat} dengan dynamic parser...")
                nbt_data = self.bedrock_parser.parse_bedrock_level_dat_manual(level_dat)
                
                if not nbt_data or len(nbt_data) == 0:
                    raise Exception("Dynamic parser gagal membaca level.dat")
                
                # Validasi bahwa data berisi struktur level.dat yang benar
                if isinstance(nbt_data, dict):
                    print(f"✅ Berhasil mendeteksi {len(nbt_data)} keys dalam level.dat")
                    print(f"Keys yang ditemukan: {list(nbt_data.keys())}")
                    
                self.nbt_data = nbt_data
                
                # Clear any previous search results and type info
                self.search_utils.clear_search()
                if hasattr(self, '_type_info'):
                    self._type_info.clear()
                    print("🧹 Cleared previous type info")
                
                # Initialize type info to ensure it exists
                if not hasattr(self, '_type_info'):
                    self._type_info = {}
                    print("🔧 Initialized type info dictionary")
                
                self.tree.clear()
                self.populate_tree(self.nbt_data, self.tree.invisibleRootItem())
                
                # Auto-expand first level untuk kemudahan navigasi
                self.tree.expandToDepth(0)
                
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka level.dat: {e}")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
            finally:
                # Always reset flag regardless of success or failure
                self.is_programmatic_change = False

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Buka File NBT/DAT/SNBT", "", "NBT/DAT/SNBT Files (*.nbt *.dat *.snbt *.txt)")
        if file_path:
            # Set flag immediately to prevent any itemChanged signals during file loading
            self.is_programmatic_change = True
            
            # Clear current data and state before loading new file
            self.clear_current_data()
            
            self.nbt_file = file_path
            try:
                # Jika file SNBT/text, parse manual
                if file_path.endswith('.snbt') or file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        snbt_text = f.read()
                    # SNBT sederhana: key: value\n
                    def parse_snbt(text):
                        tree = {}
                        for line in text.splitlines():
                            if ':' in line:
                                key, value = line.split(':', 1)
                                tree[key.strip()] = value.strip()
                        return tree
                    self.nbt_data = parse_snbt(snbt_text)
                    
                    # Clear any previous search results and type info
                    self.search_utils.clear_search()
                    if hasattr(self, '_type_info'):
                        self._type_info.clear()
                        print("🧹 Cleared previous type info")
                    
                    # Initialize type info to ensure it exists
                    if not hasattr(self, '_type_info'):
                        self._type_info = {}
                        print("🔧 Initialized type info dictionary")
                    
                    self.tree.clear()
                    self.populate_tree(self.nbt_data, self.tree.invisibleRootItem())
                else:
                    # Gunakan logic parsing NBT yang sama seperti level.dat
                    nbt_data = None
                    
                    # Deteksi format file berdasarkan magic bytes
                    with open(file_path, 'rb') as f:
                        first_bytes = f.read(8)
                    
                    is_bedrock_format = (
                        first_bytes[:4] in [b'\x08\x00\x00\x00', b'\x0A\x00\x00\x00'] or
                        len(first_bytes) >= 4 and first_bytes[0] in [0x08, 0x0A]
                    )
                    
                    # Coba berbagai metode parsing
                    parsing_methods = []
                    
                    if is_bedrock_format:
                        parsing_methods = []
                        if AMULET_AVAILABLE:
                            parsing_methods.append(("amulet-nbt", lambda: nbt_to_dict(amulet_load(file_path))))
                        parsing_methods.extend([
                            ("nbtlib", lambda: nbtlib.load(file_path)),
                            ("nbtlib-gzipped", lambda: nbtlib.load(file_path, gzipped=True))
                        ])
                    else:
                        parsing_methods = [
                            ("nbtlib-gzipped", lambda: nbtlib.load(file_path, gzipped=True)),
                            ("nbtlib", lambda: nbtlib.load(file_path))
                        ]
                        if AMULET_AVAILABLE:
                            parsing_methods.append(("amulet-nbt", lambda: nbt_to_dict(amulet_load(file_path))))
                    
                    for method_name, method_func in parsing_methods:
                        try:
                            print(f"Mencoba parsing dengan {method_name}...")
                            nbt_data = method_func()
                            print(f"Berhasil dengan {method_name}")
                            break
                        except Exception as e:
                            print(f"{method_name} gagal: {e}")
                            continue
                    
                    if nbt_data is None:
                        raise Exception("Tidak dapat membaca file dengan metode parsing apapun")
                    
                    # Proses data NBT
                    self.nbt_data = nbt_data
                    
                    # Clear any previous search results and type info
                    self.search_utils.clear_search()
                    if hasattr(self, '_type_info'):
                        self._type_info.clear()
                        print("🧹 Cleared previous type info")
                    
                    # Initialize type info to ensure it exists
                    if not hasattr(self, '_type_info'):
                        self._type_info = {}
                        print("🔧 Initialized type info dictionary")
                    
                    self.tree.clear()
                    root_tag = getattr(nbt_data, 'root', nbt_data)
                    
                    if not hasattr(root_tag, 'items') and not isinstance(root_tag, (list, dict)):
                        QMessageBox.warning(self, "Kosong", "File tidak berisi data NBT yang dapat ditampilkan.")
                        return
                    
                    self.populate_tree(root_tag, self.tree.invisibleRootItem())
                    
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka file: {e}")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
            finally:
                # Always reset flag regardless of success or failure
                self.is_programmatic_change = False

    def save_file(self):
        if self.nbt_file and self.nbt_data:
            try:
                print(f"💾 Saving file: {self.nbt_file}")
                print(f"📊 Data type: {type(self.nbt_data)}")
                
                # Create a backup of the original file only if there are changes
                backup_file = self.nbt_file + ".backup"
                if os.path.exists(self.nbt_file) and hasattr(self, '_type_info') and self._type_info:
                    import shutil
                    shutil.copy2(self.nbt_file, backup_file)
                    print(f"✅ Backup created: {backup_file}")
                elif os.path.exists(self.nbt_file):
                    print("ℹ️ No changes detected, skipping backup creation")
                
                # Use manual NBT writer approach
                if isinstance(self.nbt_data, dict):
                    print("🔄 Using manual NBT writer with type preservation...")
                    
                    try:
                        # Use the manual NBT writer from bedrock_parser with type preservation
                        type_info = getattr(self, '_type_info', {})
                        print(f"🔧 Saving with type preservation: {len(type_info)} keys")
                        
                        if type_info:
                            print(f"🔧 Type info keys: {list(type_info.keys())}")
                        
                        # Verify data structure before saving
                        print(f"🔍 Verifying data structure before save...")
                        for key, value in self.nbt_data.items():
                            print(f"   {key}: {value} (type: {type(value)})")
                        
                        success = self.bedrock_parser.save_nbt_data_manual_with_type_info(
                            self.nbt_data, self.nbt_file, type_info, debug_type_detection=True
                        )
                        
                        if success:
                            print("✅ File saved successfully with type preservation!")
                            
                            # Verify saved data by reading it back
                            self.verify_saved_data()
                            
                            # Reset window title setelah save berhasil
                            self.setWindowTitle("Bedrock NBT/DAT Editor")
                            
                            # Clear type info after successful save to prevent stale data
                            if hasattr(self, '_type_info'):
                                self._type_info.clear()
                                print("🧹 Cleared type info after successful save")
                            
                            # Success message dengan styling yang match
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Information)
                            msg.setWindowTitle("Sukses")
                            msg.setText("File berhasil disimpan dengan type preservation!")
                            msg.setStyleSheet(GUIComponents.get_message_box_style())
                            msg.exec_()
                        else:
                            raise Exception("Manual NBT writer with type preservation failed")
                            
                    except Exception as manual_error:
                        print(f"❌ Manual save failed: {manual_error}")
                        
                        # Fallback: save as JSON
                        json_file = self.nbt_file.replace('.dat', '.json')
                        import json
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(self.nbt_data, f, indent=2, ensure_ascii=False)
                        print(f"✅ Saved as JSON backup: {json_file}")
                        
                        # Show success message for JSON save
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setWindowTitle("Backup Saved")
                        msg.setText(f"Data disimpan sebagai JSON backup:\n{json_file}")
                        msg.setStyleSheet(GUIComponents.get_message_box_style())
                        msg.exec_()
                        
                else:
                    print("📁 Using existing nbtlib object...")
                    # Use the correct save method for nbtlib objects
                    self.nbt_data.save(self.nbt_file)
                    print("✅ File saved successfully!")
                    
                    # Reset window title setelah save berhasil
                    self.setWindowTitle("Bedrock NBT/DAT Editor")
                    
                    # Success message dengan styling yang match
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setWindowTitle("Sukses")
                    msg.setText("File berhasil disimpan!")
                    msg.setStyleSheet(GUIComponents.get_message_box_style())
                    msg.exec_()
                    
            except Exception as e:
                print(f"❌ Save error: {e}")
                print(f"❌ Error type: {type(e)}")
                import traceback
                traceback.print_exc()
                
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal menyimpan file: {e}")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Peringatan")
            msg.setText("Tidak ada file yang terbuka untuk disimpan!")
            msg.setStyleSheet(GUIComponents.get_warning_message_box_style())
            msg.exec_()

    def extract_nbt_value(self, value):
        """Extract actual value from NBT tag objects"""
        if hasattr(value, 'tag_id') and hasattr(value, 'value'):
            return value.value
        return value
    
    def populate_tree(self, nbt_node, parent_item):
        """Populate tree widget with NBT data with enhanced validation"""
        try:
            # Validate input
            if nbt_node is None:
                print("⚠️ Warning: nbt_node is None")
                return
            
            # Tampilkan semua entri NBT sebagai tree dengan Key dan Value terpisah
            if isinstance(nbt_node, dict) or hasattr(nbt_node, 'items'):
                # dict atau compound tag
                items = dict(nbt_node.items()) if hasattr(nbt_node, 'items') else nbt_node
                
                # Urutkan kunci untuk konsistensi tampilan
                sorted_items = sorted(items.items(), key=lambda x: str(x[0]))
                
                for key, value in sorted_items:
                    value_display = get_nbt_value_display(value)
                    type_icon = get_value_type_icon(value)
                    
                    if isinstance(value, (dict, list)) or hasattr(value, 'items'):
                        # Untuk compound/list, tampilkan key dan jumlah entries
                        item = QTreeWidgetItem([str(key), value_display])
                        
                        # Set icon berdasarkan tipe  
                        if isinstance(value, dict):
                            item.setIcon(0, self.style().standardIcon(self.style().SP_DirIcon))
                        elif isinstance(value, list):
                            item.setIcon(0, self.style().standardIcon(self.style().SP_FileDialogDetailedView))
                        
                        parent_item.addChild(item)
                        self.populate_tree(value, item)
                    else:
                        # Untuk nilai primitif - key di kolom 1, value di kolom 2
                        item = QTreeWidgetItem([str(key), value_display])
                        # Set hanya kolom Value (1) yang editable
                        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        # Store original value untuk tracking changes (extract value from NBT tags)
                        actual_value = self.extract_nbt_value(value)
                        item.setData(1, Qt.UserRole, actual_value)
                        
                        # Set icon berdasarkan tipe data
                        if type_icon == "B":
                            # Byte/Boolean - blue B icon
                            item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        elif type_icon == "I":
                            # Integer - blue I icon
                            item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        elif type_icon == "L":
                            # Long - green L icon
                            item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        elif type_icon == "F":
                            # Float - orange F icon
                            item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        elif type_icon == "S":
                            # String - yellow quotes icon
                            item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        
                        # Set warna yang kontras untuk semua tipe data
                        if isinstance(value, bool):
                            item.setForeground(1, QColor("#4da6ff"))  # Light blue untuk boolean
                        elif isinstance(value, int):
                            if abs(value) > 2147483647:
                                item.setForeground(1, QColor("#51cf66"))  # Light green untuk long
                            else:
                                item.setForeground(1, QColor("#4da6ff"))  # Light blue untuk integer
                        elif isinstance(value, float):
                            item.setForeground(1, QColor("#ff6b6b"))  # Light red untuk float
                        elif isinstance(value, str):
                            item.setForeground(1, QColor("#ffd43b"))  # Yellow untuk string
                        else:
                            item.setForeground(1, QColor("#e1e1e1"))  # Default light gray
                        
                        parent_item.addChild(item)
                        
            elif isinstance(nbt_node, list):
                # List NBT - tampilkan index sebagai key
                for idx, value in enumerate(nbt_node):
                    value_display = get_nbt_value_display(value)
                    type_icon = get_value_type_icon(value)
                    
                    if isinstance(value, (dict, list)) or hasattr(value, 'items'):
                        item = QTreeWidgetItem([f"[{idx}]", value_display])
                        parent_item.addChild(item)
                        self.populate_tree(value, item)
                    else:
                        item = QTreeWidgetItem([f"[{idx}]", value_display])
                        # Set hanya kolom Value (1) yang editable
                        item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                        # Store original value untuk tracking changes (extract value from NBT tags)
                        actual_value = self.extract_nbt_value(value)
                        item.setData(1, Qt.UserRole, actual_value)
                    
                    # Set icon dan warna berdasarkan tipe data
                    if type_icon == "B":
                        item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        item.setForeground(1, QColor("#4da6ff"))
                    elif type_icon == "I":
                        item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        item.setForeground(1, QColor("#4da6ff"))
                    elif type_icon == "L":
                        item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        item.setForeground(1, QColor("#51cf66"))
                    elif type_icon == "F":
                        item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        item.setForeground(1, QColor("#ff6b6b"))
                    elif type_icon == "S":
                        item.setIcon(0, self.style().standardIcon(self.style().SP_MessageBoxInformation))
                        item.setForeground(1, QColor("#ffd43b"))
                    
                    parent_item.addChild(item)
            else:
                # Nilai tunggal
                value_display = get_nbt_value_display(nbt_node)
                item = QTreeWidgetItem(["Value", value_display])
                parent_item.addChild(item)
                
        except Exception as e:
            print(f"❌ Error in populate_tree: {e}")
            import traceback
            traceback.print_exc()

    def on_tree_item_double_clicked(self, item, column):
        """Handle double-click untuk inline editing"""
        # Hanya allow edit pada kolom Value (column 1) dan untuk item yang bukan compound/list
        if column == 1 and not item.text(1).endswith(" entries"):
            # Set item sebagai editable untuk inline editing
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.tree.editItem(item, column)

    def on_item_changed(self, item, column):
        """Handle perubahan value dengan dialog konfirmasi"""
        # Skip if this is a programmatic change (search, color updates, loading worlds, etc.)
        if self.is_programmatic_change:
            return
        
        # Skip if we're currently loading a file or changing worlds
        if not hasattr(self, 'nbt_data') or self.nbt_data is None:
            return
            
        if column == 1:  # Hanya untuk kolom Value
            old_value = item.data(1, Qt.UserRole)  # Get original value
            new_value = item.text(1)
            
            # Skip if value hasn't actually changed
            if str(old_value) == new_value:
                print(f"ℹ️ No actual change for {item.text(0)}: {old_value}")
                return
            
            # Langsung update NBT data structure tanpa confirmation
            try:
                # Get parsed value from update_nbt_value
                parsed_value = self.update_nbt_value(item, new_value)
                print(f"✅ Value changed for {item.text(0)}: {old_value} → {parsed_value}")
                
                # Update item data untuk tracking dengan parsed value (bukan string)
                item.setData(1, Qt.UserRole, parsed_value)
                
                # Force immediate data structure update
                self.force_data_update(item.text(0), parsed_value)
                
                # Update window title untuk menunjukkan ada perubahan
                self.setWindowTitle("Bedrock NBT/DAT Editor - *Modified")
                
            except Exception as e:
                # Restore original value jika update gagal
                self.is_programmatic_change = True
                item.setText(1, str(old_value))
                self.is_programmatic_change = False
                
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal mengubah nilai: {e}")
                msg.setStyleSheet(GUIComponents.get_error_message_box_style())
                msg.exec_()
    

    
    def perform_live_search(self):
        """Delegate to search utils"""
        self.search_utils.perform_live_search()
    
    def update_nbt_value(self, item, new_value):
        """Update NBT data structure dengan nilai baru dengan type preservation"""
        key = item.text(0)
        
        # Parse new value berdasarkan tipe data asli
        original_value = item.data(1, Qt.UserRole)
        
        try:
            if isinstance(original_value, bool):
                # Handle boolean values
                if new_value.lower() in ['true', '1', 'yes', 'on']:
                    parsed_value = True
                elif new_value.lower() in ['false', '0', 'no', 'off']:
                    parsed_value = False
                else:
                    raise ValueError(f"Invalid boolean value: {new_value}")
                    
            elif isinstance(original_value, int):
                # Handle integer values - preserve original type
                if 'L' in new_value.upper():  # Long value
                    parsed_value = int(new_value.upper().replace('L', ''))
                else:
                    parsed_value = int(new_value)
                
                # Preserve original int type (int vs long)
                if isinstance(original_value, int) and abs(original_value) > 2147483647:
                    # Original was long, keep as long
                    pass  # parsed_value is already int, will be detected as long by writer
                else:
                    # Original was regular int
                    pass  # parsed_value is already int
                    
            elif isinstance(original_value, float):
                # Handle float values
                if 'f' in new_value.lower():  # Float value
                    parsed_value = float(new_value.lower().replace('f', ''))
                else:
                    parsed_value = float(new_value)
                    
            elif isinstance(original_value, str):
                # Handle string values
                parsed_value = str(new_value)
                
            elif isinstance(original_value, dict):
                # Handle dictionary values - preserve dictionary structure
                # This is for cases like 'experiments' dictionary
                if key == 'experiments':
                    # Special handling for experiments dictionary
                    experiments_dict = {}
                    for exp_key, exp_value in original_value.items():
                        # Convert all experiment values to integer 0 while preserving structure
                        experiments_dict[exp_key] = 0
                    parsed_value = experiments_dict
                    print(f"🔧 Special handling for experiments dict: {len(experiments_dict)} keys set to 0")
                else:
                    # For other dictionaries, try to parse as JSON or keep as dict
                    try:
                        import json
                        parsed_value = json.loads(new_value)
                    except:
                        # If not valid JSON, keep original structure
                        parsed_value = original_value
                
            else:
                # Default to string
                parsed_value = str(new_value)
            
            # Store original type information for manual NBT writer
            self.store_type_info(key, type(original_value), parsed_value)
            
            # Update NBT data structure
            self.update_nbt_data_recursive(self.nbt_data, key, parsed_value)
            
            print(f"🔧 Type preserved for '{key}': {type(original_value)} -> {type(parsed_value)}")
            
            # Return parsed value for tracking
            return parsed_value
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value format: {e}")
    
    def store_type_info(self, key, original_type, new_value):
        """Store type information for manual NBT writer with enhanced logging"""
        if not hasattr(self, '_type_info'):
            self._type_info = {}
        
        # Check if this is an experiment key
        is_experiment_key = key in [
            'data_driven_biomes', 'experimental_creator_cameras', 'experiments_ever_used',
            'gametest', 'jigsaw_structures', 'saved_with_toggled_experiments',
            'upcoming_creator_features', 'villager_trades_rebalance', 'y_2025_drop_3'
        ]
        
        # Handle nested keys (for experiments dictionary)
        if '.' in key or is_experiment_key:
            # This is a nested key like 'experiments.data_driven_biomes' or experiment key
            self._type_info[key] = {
                'original_type': original_type,
                'new_value': new_value,
                'is_nested': True,
                'is_experiment': is_experiment_key
            }
        else:
            self._type_info[key] = {
                'original_type': original_type,
                'new_value': new_value,
                'is_nested': False,
                'is_experiment': False
            }
        
        print(f"🔧 Stored type info for '{key}': {original_type} -> {type(new_value)} (value: {new_value}) [experiment: {is_experiment_key}]")
        
        # Debug: show current type info count
        print(f"📊 Total type info entries: {len(self._type_info)}")
    
    def force_data_update(self, key, new_value):
        """Force immediate update of data structure to ensure changes are saved"""
        if not hasattr(self, 'nbt_data') or self.nbt_data is None:
            return False
        
        # Direct update in nbt_data structure
        if isinstance(self.nbt_data, dict):
            if key in self.nbt_data:
                old_value = self.nbt_data[key]
                self.nbt_data[key] = new_value
                print(f"🔧 Force updated '{key}': {old_value} -> {new_value}")
                return True
        
        # Also try recursive update
        return self.update_nbt_data_recursive(self.nbt_data, key, new_value)
    
    def verify_saved_data(self):
        """Verify that saved data matches the expected values"""
        try:
            print("🔍 Verifying saved data...")
            
            # Read back the saved file
            saved_data = self.bedrock_parser.parse_bedrock_level_dat_manual(self.nbt_file)
            
            if not saved_data:
                print("❌ Could not read saved file for verification")
                return False
            
            # Check if type info exists
            if not hasattr(self, '_type_info') or not self._type_info:
                print("ℹ️ No type info to verify")
                return True
            
            # Verify key changes
            verification_errors = []
            for key, type_info in self._type_info.items():
                if key in saved_data:
                    saved_value = saved_data[key]
                    expected_value = type_info.get('new_value')
                    
                    if saved_value != expected_value:
                        verification_errors.append(f"Key '{key}': expected {expected_value}, got {saved_value}")
                        print(f"❌ Verification failed for '{key}': expected {expected_value}, got {saved_value}")
                    else:
                        print(f"✅ Verified '{key}': {saved_value}")
                else:
                    print(f"⚠️ Key '{key}' not found in saved data")
            
            if verification_errors:
                print(f"❌ Found {len(verification_errors)} verification errors:")
                for error in verification_errors:
                    print(f"   - {error}")
                return False
            else:
                print("✅ All changes verified successfully!")
                return True
                
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def update_nbt_data_recursive(self, data, target_key, new_value):
        """Recursively update NBT data structure with enhanced dictionary handling"""
        if isinstance(data, dict):
            # Check if target key exists in current level
            if target_key in data:
                # Special handling for experiments dictionary
                if target_key == 'experiments' and isinstance(new_value, dict):
                    # Update experiments dictionary while preserving structure
                    original_experiments = data[target_key]
                    if isinstance(original_experiments, dict):
                        # Update each experiment key to 0 while preserving type
                        for exp_key in original_experiments.keys():
                            if exp_key in new_value:
                                # Store type info for each experiment key
                                original_type = type(original_experiments[exp_key])
                                self.store_type_info(exp_key, original_type, new_value[exp_key])
                        data[target_key] = new_value
                        print(f"🔧 Updated experiments dict with {len(new_value)} keys")
                    else:
                        data[target_key] = new_value
                else:
                    data[target_key] = new_value
                return True
            else:
                # Search in nested dictionaries (including experiments dictionary)
                for key, value in data.items():
                    if isinstance(value, dict):
                        # Special handling for experiments dictionary
                        if key == 'experiments' and target_key in value:
                            # Update individual experiment value
                            original_value = value[target_key]
                            original_type = type(original_value)
                            value[target_key] = new_value
                            # Store type info for this experiment key
                            self.store_type_info(target_key, original_type, new_value)
                            print(f"🔧 Updated experiment '{target_key}': {original_value} -> {new_value}")
                            return True
                        elif self.update_nbt_data_recursive(value, target_key, new_value):
                            return True
                    elif isinstance(value, list):
                        # Search in list items if they are dictionaries
                        for item in value:
                            if isinstance(item, dict):
                                if self.update_nbt_data_recursive(item, target_key, new_value):
                                    return True
        return False
    
    def convert_dict_to_nbt_format(self, data):
        """Convert Python dict to proper NBT format"""
        from nbtlib import nbt
        
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = self.convert_value_to_nbt_format(value)
            return result
        elif isinstance(data, list):
            return [self.convert_value_to_nbt_format(item) for item in data]
        else:
            return self.convert_value_to_nbt_format(data)
    
    def convert_value_to_nbt_format(self, value):
        """Convert individual value to NBT format"""
        from nbtlib import nbt
        
        if isinstance(value, dict):
            return self.convert_dict_to_nbt_format(value)
        elif isinstance(value, list):
            return [self.convert_value_to_nbt_format(item) for item in value]
        elif isinstance(value, bool):
            return nbt.Byte(value)
        elif isinstance(value, int):
            if abs(value) > 2147483647:
                return nbt.Long(value)
            else:
                return nbt.Int(value)
        elif isinstance(value, float):
            return nbt.Float(value)
        elif isinstance(value, str):
            return str(value)  # Use string directly, nbtlib will handle conversion
        else:
            return str(value)  # Use string directly, nbtlib will handle conversion
    
    def convert_value_simple(self, value):
        """Convert value using simple approach"""
        from nbtlib import nbt
        
        if isinstance(value, bool):
            return nbt.Byte(value)
        elif isinstance(value, int):
            if abs(value) > 2147483647:
                return nbt.Long(value)
            else:
                return nbt.Int(value)
        elif isinstance(value, float):
            return nbt.Float(value)
        elif isinstance(value, str):
            return str(value)  # Let nbtlib handle string conversion
        else:
            return str(value)  # Convert to string
    
    def convert_dict_simple(self, data):
        """Convert dict using simple approach"""
        from nbtlib import nbt
        
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self.convert_dict_simple(value)
            elif isinstance(value, list):
                result[key] = [self.convert_value_simple(item) for item in value]
            else:
                result[key] = self.convert_value_simple(value)
        return result

    def export_to_json(self):
        """Export the current NBT data to a JSON file."""
        if self.nbt_data is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data NBT untuk diekspor.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Simpan File JSON", "", "JSON Files (*.json)")
        if file_path:
            try:
                json_data = convert_to_json_format(self.nbt_data)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=4)
                QMessageBox.information(self, "Sukses", f"Data NBT berhasil diekspor ke {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mengekspor data JSON: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditor()
    window.show()
    sys.exit(app.exec_())
