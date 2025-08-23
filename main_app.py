import sys
import os
import nbtlib

# Import our separated modules
from package_manager import *
from minecraft_paths import MINECRAFT_WORLDS_PATH
from nbt_utils import nbt_to_dict, get_nbt_value_display
from bedrock_parser import BedrockParser
from search_utils import SearchUtils
from gui_components import GUIComponents

# Additional imports needed for the main app
from PyQt5.QtWidgets import QListWidgetItem

class NBTEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bedrock NBT/DAT Editor")
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
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        
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
        
        # Cari folder berdasarkan urutan di world_list
        idx = self.world_list.row(item)
        folder = os.listdir(MINECRAFT_WORLDS_PATH)[idx]
        world_path = os.path.join(MINECRAFT_WORLDS_PATH, folder)
        level_dat = os.path.join(world_path, "level.dat")
        if os.path.exists(level_dat):
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
                
                # Clear any previous search results
                self.search_utils.clear_search()
                
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
                    
                    # Clear any previous search results
                    self.search_utils.clear_search()
                    
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
                    
                    # Clear any previous search results
                    self.search_utils.clear_search()
                    
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
                nbtlib.save(self.nbt_data, self.nbt_file)
                # Success message dengan styling yang match
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Sukses")
                msg.setText("File berhasil disimpan!")
                msg.setStyleSheet(GUIComponents.get_message_box_style())
                msg.exec_()
            except Exception as e:
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

    def populate_tree(self, nbt_node, parent_item, entry_count=None):
        # Tampilkan semua entri NBT sebagai tree dengan Key dan Value terpisah
        if isinstance(nbt_node, dict) or hasattr(nbt_node, 'items'):
            # dict atau compound tag
            items = dict(nbt_node.items()) if hasattr(nbt_node, 'items') else nbt_node
            
            # Urutkan kunci untuk konsistensi tampilan
            sorted_items = sorted(items.items(), key=lambda x: str(x[0]))
            
            for key, value in sorted_items:
                value_display = get_nbt_value_display(value)
                
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
                    
                    # Set warna yang kontras untuk semua tipe data
                    if isinstance(value, int):
                        item.setForeground(1, QColor("#4da6ff"))  # Light blue untuk angka
                    elif isinstance(value, float):
                        item.setForeground(1, QColor("#ff6b6b"))  # Light red untuk float
                    elif isinstance(value, str):
                        item.setForeground(1, QColor("#51cf66"))  # Light green untuk string
                    else:
                        item.setForeground(1, QColor("#e1e1e1"))  # Default light gray
                    
                    parent_item.addChild(item)
                    
        elif isinstance(nbt_node, list):
            # List NBT - tampilkan index sebagai key
            for idx, value in enumerate(nbt_node):
                value_display = get_nbt_value_display(value)
                
                if isinstance(value, (dict, list)) or hasattr(value, 'items'):
                    item = QTreeWidgetItem([f"[{idx}]", value_display])
                    parent_item.addChild(item)
                    self.populate_tree(value, item)
                else:
                    item = QTreeWidgetItem([f"[{idx}]", value_display])
                    # Set hanya kolom Value (1) yang editable
                    item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    parent_item.addChild(item)
        else:
            # Nilai tunggal
            value_display = get_nbt_value_display(nbt_node)
            item = QTreeWidgetItem(["Value", value_display])
            parent_item.addChild(item)

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
            # Tampilkan dialog konfirmasi seperti di foto
            reply = self.show_confirmation_dialog(item.text(0), item.text(1))
            if reply == QMessageBox.Yes:
                # Konfirm perubahan
                print(f"Value changed for {item.text(0)}: {item.text(1)}")
                # TODO: Update actual NBT data structure
                pass
            else:
                # Batalkan perubahan - restore nilai asli jika diperlukan
                # Set flag to prevent infinite loop
                self.is_programmatic_change = True
                # Restore original value here if needed
                self.is_programmatic_change = False
    
    def show_confirmation_dialog(self, key, new_value):
        """Tampilkan dialog konfirmasi seperti di foto"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirm")
        msg.setText(f"Change '{key}' to '{new_value}'?")
        
        # Style dialog seperti tema aplikasi
        msg.setStyleSheet(GUIComponents.get_confirmation_dialog_style())
        
        # Set custom buttons
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        # Ubah text button menjadi "Confirm" dan "Cancel"
        yes_button = msg.button(QMessageBox.Yes)
        no_button = msg.button(QMessageBox.No)
        yes_button.setText("Confirm")
        no_button.setText("Cancel")
        
        return msg.exec_()
    
    def perform_live_search(self):
        """Delegate to search utils"""
        self.search_utils.perform_live_search()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditor()
    window.show()
    sys.exit(app.exec_())
