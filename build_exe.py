#!/usr/bin/env python3
"""
Script Otomatis Pembuka & Pembuat Executable (.exe / Linux Standalone Binary)
Menggunakan PyInstaller.
"""

import os
import sys
import subprocess

def main():
    print("=" * 65)
    print(" 🛠️  PEMBUAT FILE EXECUTABLE EEPROM PROGRAMMER (CH341A)")
    print("=" * 65)

    # Cek PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("⚡ Memasang PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "--break-system-packages"])

    # Perintah PyInstaller No-Console Standalone dengan Hidden Imports PyUSB
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--hidden-import=usb",
        "--hidden-import=usb.core",
        "--hidden-import=usb.util",
        "--hidden-import=usb.backend.libusb1",
        "--name=EEPROM_Programmer",
        "main.py"
    ]

    print("Menjalankan proses bundling PyInstaller...")
    subprocess.check_call(cmd)

    dist_folder = os.path.abspath("dist")
    print("\n" + "=" * 65)
    print(" ✅ SUKSES! File Executable Siap Pakai:")
    if sys.platform.startswith("win"):
        print(f" 📂 Path: {dist_folder}\\EEPROM_Programmer.exe")
    else:
        print(f" 📂 Path: {dist_folder}/EEPROM_Programmer")
    print("=" * 65)

if __name__ == "__main__":
    main()
