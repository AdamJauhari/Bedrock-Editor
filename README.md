# Bedrock NBT/DAT Editor

Editor untuk file NBT/DAT Minecraft Bedrock Edition dengan fitur auto-detection untuk menemukan key yang belum terdaftar.

## Fitur Utama

### 🔍 Reliable NBT Parsing System
Program sekarang menggunakan sistem parsing yang reliable dan menghasilkan output yang bersih sesuai dengan struktur level.dat yang benar:

- **Reliable NBT Parsing**: Menggunakan library NBT yang teruji untuk parsing yang akurat
- **Clean Output**: Menghasilkan data yang bersih tanpa key per huruf atau substring
- **Proper Hierarchy**: Menampilkan struktur nested yang benar untuk compound fields
- **Correct Field Names**: Menggunakan nama field yang benar sesuai standar Minecraft
- **Accurate Values**: Menampilkan nilai yang akurat tanpa duplikasi atau error
- **Compound Support**: Mendukung struktur compound seperti `abilities` dan `experiments`
- **Version Arrays**: Menangani array versi seperti `MinimumCompatibleClientVersion`

### 🎯 Output yang Bersih dan Akurat
Program akan menampilkan data level.dat dengan struktur yang benar dan bersih:
- **Field names yang benar** sesuai standar Minecraft (tidak ada partial names)
- **Values yang akurat** tanpa duplikasi atau error parsing
- **Proper hierarchy** untuk compound fields seperti `abilities` dan `experiments`
- **Correct data types** (byte, int, long, float, string, arrays)
- **Clean structure** tanpa key per huruf atau substring yang tidak valid

### 📊 Debug Information
Program menampilkan informasi debug saat auto-detection:
```
🔍 Scanning for unknown fields...
✅ Found X unknown fields: [field1, field2, field3]
Auto-detected field: fieldname = value (type: int)
Auto-detected compound: abilities = {...}
```

## Cara Kerja Reliable NBT Parsing

1. **Library-Based Parsing**: Menggunakan library NBT yang teruji (nbtlib, amulet-nbt)
2. **Known Field Mapping**: Menggunakan daftar field yang sudah dikenal dan teruji
3. **Compound Structure Parsing**: Parsing struktur compound dengan field yang benar
4. **Type-Specific Extraction**: Mengekstrak nilai berdasarkan tipe data yang tepat
5. **Error Handling**: Menangani error parsing dengan graceful fallback
6. **Clean Output Generation**: Menghasilkan output yang bersih dan terstruktur

## Penggunaan

1. Jalankan program: `python main.py`
2. Pilih world dari daftar atau buka file NBT/DAT
3. Program akan otomatis mendeteksi dan menampilkan semua key yang ada
4. Key yang auto-detected akan muncul di tree view dengan format yang sama

## Dependencies

- PyQt5
- nbtlib
- amulet-nbt (optional)

## Author

Bedrock NBT/DAT Editor by Adam Arias Jauhari
