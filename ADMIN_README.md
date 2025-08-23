# 🛡️ Bedrock NBT/DAT Editor - Administrator Mode

## 📋 Overview

Program ini membutuhkan hak akses **Administrator** untuk mengakses file Minecraft Bedrock Edition yang berada di folder sistem Windows.

## 🚀 Cara Menjalankan Program sebagai Administrator

### **Method 1: Menggunakan Batch File (Recommended)**
```bash
# Double-click file ini:
run_as_admin.bat
```

### **Method 2: Menggunakan PowerShell Script**
```powershell
# Double-click file ini:
run_as_admin.ps1
```

### **Method 3: Membuat Desktop Shortcut**
```bash
# Jalankan script ini sekali untuk membuat shortcut:
create_shortcut.bat
```
Kemudian gunakan shortcut di Desktop untuk menjalankan program.

### **Method 4: Manual Run as Administrator**
1. Buka Command Prompt atau PowerShell sebagai Administrator
2. Navigate ke folder program
3. Jalankan: `python main.py`

### **Method 5: Program Auto-Elevation**
Program akan otomatis meminta hak akses Administrator jika diperlukan.

## 🔧 File yang Dibuat

### **1. app.manifest**
- Windows manifest file untuk request administrator privileges
- Digunakan untuk UAC elevation

### **2. run_as_admin.bat**
- Batch file untuk menjalankan program sebagai administrator
- Includes error checking dan user feedback

### **3. run_as_admin.ps1**
- PowerShell script dengan fitur yang lebih advanced
- Auto-elevation jika tidak running sebagai admin

### **4. create_shortcut.bat**
- Script untuk membuat desktop shortcut
- Shortcut akan otomatis run as administrator

## 🎯 Fitur Administrator Mode

### **✅ Auto-Elevation**
- Program otomatis mendeteksi jika tidak running sebagai admin
- Menampilkan dialog konfirmasi sebelum elevation
- Restart program dengan hak akses administrator

### **✅ UAC Integration**
- Menggunakan Windows UAC (User Account Control)
- Dialog konfirmasi yang user-friendly
- Secure elevation process

### **✅ Error Handling**
- Check Python availability
- Check file existence
- Proper error messages

### **✅ Visual Indicators**
- Window title menunjukkan "(Administrator)"
- Console output yang informatif
- Status messages yang jelas

## 🔒 Security Features

### **✅ Safe Elevation**
- Hanya elevate jika benar-benar diperlukan
- Proper error handling untuk failed elevation
- Clean exit jika elevation gagal

### **✅ UAC Compliance**
- Mengikuti Windows security guidelines
- Proper manifest file
- Safe privilege escalation

## 📁 File Access

### **✅ Minecraft Worlds**
- Akses ke folder: `%LOCALAPPDATA%\Packages\Microsoft.MinecraftUWP_*\LocalState\games\com.mojang\minecraftWorlds\`
- Read/write access ke `level.dat` files
- Backup file creation

### **✅ System Integration**
- Registry access untuk world detection
- File system access untuk backup
- Temporary file management

## 🚨 Troubleshooting

### **Problem: "Access Denied"**
**Solution:**
1. Pastikan menjalankan sebagai Administrator
2. Gunakan `run_as_admin.bat` atau `run_as_admin.ps1`
3. Check Windows UAC settings

### **Problem: "Python not found"**
**Solution:**
1. Install Python dan tambahkan ke PATH
2. Restart computer setelah install Python
3. Check Python installation dengan: `python --version`

### **Problem: "File not found"**
**Solution:**
1. Pastikan semua file program ada di folder yang sama
2. Check file permissions
3. Run sebagai Administrator

### **Problem: "UAC Dialog not appearing"**
**Solution:**
1. Check Windows UAC settings
2. Disable antivirus temporarily
3. Use manual elevation method

## 📝 Notes

### **⚠️ Important:**
- Program **HARUS** dijalankan sebagai Administrator untuk mengakses file Minecraft
- File Minecraft berada di folder sistem yang protected
- Backup files akan dibuat di folder world yang sama

### **🔧 Technical Details:**
- Menggunakan `ctypes.windll.shell32.IsUserAnAdmin()` untuk check admin status
- Menggunakan `ctypes.windll.shell32.ShellExecuteW()` untuk elevation
- Manifest file untuk UAC integration
- Proper error handling dan user feedback

### **🎮 Minecraft Integration:**
- Deteksi otomatis folder Minecraft worlds
- Safe file operations dengan backup
- Type preservation untuk NBT data
- Clean display format

## 🎉 Success Indicators

### **✅ Program Running as Admin:**
- Window title: "Bedrock NBT/DAT Editor (Administrator)"
- Console output: "✅ Program berjalan dengan hak akses Administrator"
- No "Access Denied" errors

### **✅ File Access Working:**
- World list ter-load dengan sukses
- File save/load operations berhasil
- Backup files created properly

### **✅ User Experience:**
- Clean interface tanpa error messages
- Smooth file operations
- Proper type preservation
- No permission issues
