import sys
import os
import subprocess
def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for pkg in ["PyQt5", "nbtlib", "amulet-nbt"]:
    ensure_package(pkg)

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTreeWidget, QTreeWidgetItem, QAction, QMessageBox, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import nbtlib
from amulet_nbt import load as amulet_load

MINECRAFT_WORLDS_PATH = r"C:\Users\adamj\AppData\Local\Packages\Microsoft.MinecraftUWP_8wekyb3d8bbwe\LocalState\games\com.mojang\minecraftWorlds"

class NBTEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bedrock NBT/DAT Editor")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon("icon.png"))
        self.nbt_file = None
        self.nbt_data = None
        self.init_ui()

    def init_ui(self):
        # Menu
        open_action = QAction(QIcon(), "Buka File", self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction(QIcon(), "Simpan", self)
        save_action.triggered.connect(self.save_file)
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        # Main widget & layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Sidebar: World List
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        label_world = QLabel("Daftar Dunia Minecraft Bedrock")
        label_world.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        sidebar.addWidget(label_world)
        self.world_list = QListWidget()
        self.world_list.setMaximumWidth(260)
        self.world_list.setStyleSheet("background-color: #23272e; color: #e1e1e1; font-size: 14px; border-radius: 8px; padding: 6px;")
        self.world_list.itemClicked.connect(self.on_world_selected)
        self.load_worlds()
        sidebar.addWidget(self.world_list)
        main_layout.addLayout(sidebar)

        # Center: NBT Tree
        center_layout = QVBoxLayout()
        label_nbt = QLabel("Isi File NBT/DAT")
        label_nbt.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        center_layout.addWidget(label_nbt)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Key", "Value"])
        self.tree.itemChanged.connect(self.on_item_changed)
        self.tree.setStyleSheet("background-color: #23272e; color: #e1e1e1; font-size: 14px; border-radius: 8px; padding: 6px;")
        self.tree.itemClicked.connect(self.on_tree_item_selected)
        center_layout.addWidget(self.tree)
        main_layout.addLayout(center_layout)

        # Right: Detail Panel
        detail_layout = QVBoxLayout()
        label_detail = QLabel("Detail Tag NBT")
        label_detail.setStyleSheet("color: #00bfff; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        detail_layout.addWidget(label_detail)
        self.detail_key = QLabel("Key: -")
        self.detail_value = QLabel("Value: -")
        self.detail_key.setStyleSheet("color: #e1e1e1; font-size: 14px; margin-bottom: 4px;")
        self.detail_value.setStyleSheet("color: #e1e1e1; font-size: 14px; margin-bottom: 12px;")
        detail_layout.addWidget(self.detail_key)
        detail_layout.addWidget(self.detail_value)
        self.edit_value_btn = QPushButton("Edit Value")
        self.edit_value_btn.setStyleSheet("background-color: #00bfff; color: #23272e; font-weight: bold; border-radius: 6px; padding: 6px 12px;")
        self.edit_value_btn.clicked.connect(self.edit_selected_value)
        self.edit_value_btn.setEnabled(False)
        detail_layout.addWidget(self.edit_value_btn)
        self.save_btn = QPushButton("Simpan Perubahan")
        self.save_btn.setStyleSheet("background-color: #00ff99; color: #23272e; font-weight: bold; border-radius: 6px; padding: 6px 12px;")
        self.save_btn.clicked.connect(self.save_file)
        detail_layout.addWidget(self.save_btn)
        detail_layout.addStretch()
        main_layout.addLayout(detail_layout)

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
                self.world_list.addItem(f"{world_name}")

    def on_world_selected(self, item):
        # Cari folder berdasarkan urutan di world_list
        idx = self.world_list.row(item)
        folder = os.listdir(MINECRAFT_WORLDS_PATH)[idx]
        world_path = os.path.join(MINECRAFT_WORLDS_PATH, folder)
        level_dat = os.path.join(world_path, "level.dat")
        if os.path.exists(level_dat):
            self.nbt_file = level_dat
            try:
                nbt_obj = nbtlib.load(level_dat, gzipped=True)
                self.nbt_data = nbt_obj.root
                self.tree.clear()
                self.populate_tree(self.nbt_data, self.tree.invisibleRootItem())
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka level.dat:")
                msg.setInformativeText(str(e))
                msg.setStyleSheet("QLabel{color:#ff4444;font-size:14px;} QPushButton{color:#23272e;background:#ff4444;font-weight:bold;}")
                msg.exec_()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Buka File NBT/DAT/SNBT", "", "NBT/DAT/SNBT Files (*.nbt *.dat *.snbt *.txt)")
        if file_path:
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
                    self.tree.clear()
                    self.populate_tree(self.nbt_data, self.tree.invisibleRootItem())
                else:
                    # Coba buka file NBT normal, jika gagal coba gzipped
                    try:
                        self.nbt_data = nbtlib.load(self.nbt_file)
                    except Exception:
                        self.nbt_data = nbtlib.load(self.nbt_file, gzipped=True)
                    self.tree.clear()
                    root_tag = getattr(self.nbt_data, 'root', self.nbt_data)
                    if not hasattr(root_tag, 'items') and not isinstance(root_tag, list):
                        QMessageBox.warning(self, "Kosong", "File tidak berisi data NBT yang dapat ditampilkan.")
                        return
                    self.populate_tree(root_tag, self.tree.invisibleRootItem())
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal membuka file:")
                msg.setInformativeText(str(e))
                msg.setStyleSheet("QLabel{color:#ff4444;font-size:14px;} QPushButton{color:#23272e;background:#ff4444;font-weight:bold;}")
                msg.exec_()

    def save_file(self):
        if self.nbt_file and self.nbt_data:
            try:
                nbtlib.save(self.nbt_data, self.nbt_file)
                QMessageBox.information(self, "Sukses", "File berhasil disimpan!")
            except Exception as e:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Gagal menyimpan file:")
                msg.setInformativeText(str(e))
                msg.setStyleSheet("QLabel{color:#ff4444;font-size:14px;} QPushButton{color:#23272e;background:#ff4444;font-weight:bold;}")
                msg.exec_()

    def populate_tree(self, nbt_node, parent_item):
        # Recursively populate tree with NBT structure
        if hasattr(nbt_node, 'items'):
            items = list(nbt_node.items())
            if len(items) == 1:
                key, value = items[0]
                root_item = QTreeWidgetItem([str(key), ""])
                parent_item.addChild(root_item)
                self.populate_tree(value, root_item)
            else:
                for key, value in items:
                    item = QTreeWidgetItem([str(key), str(value) if not hasattr(value, 'items') and not isinstance(value, list) else "..."])
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    parent_item.addChild(item)
                    self.populate_tree(value, item)
        elif isinstance(nbt_node, list):
            for idx, value in enumerate(nbt_node):
                item = QTreeWidgetItem([str(idx), str(value) if not hasattr(value, 'items') and not isinstance(value, list) else "..."])
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                parent_item.addChild(item)
                self.populate_tree(value, item)
        else:
            item = QTreeWidgetItem(["Value", str(nbt_node)])
            parent_item.addChild(item)

    def on_tree_item_selected(self, item, column):
        self.detail_key.setText(f"Key: {item.text(0)}")
        self.detail_value.setText(f"Value: {item.text(1)}")
        self.edit_value_btn.setEnabled(True)

    def edit_selected_value(self):
        item = self.tree.currentItem()
        if item is not None:
            value, ok = self.get_text_input("Edit Value", f"Ubah value untuk '{item.text(0)}':", item.text(1))
            if ok:
                item.setText(1, value)
                self.detail_value.setText(f"Value: {value}")

    def get_text_input(self, title, label, default):
        from PyQt5.QtWidgets import QInputDialog
        value, ok = QInputDialog.getText(self, title, label, text=default)
        return value, ok

    def on_item_changed(self, item, column):
        # Simple edit: only updates display, not actual NBT structure
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBTEditor()
    window.show()
    sys.exit(app.exec_())
