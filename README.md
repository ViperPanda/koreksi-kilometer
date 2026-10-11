# EEPROM Programmer CH341A GUI (Speedometer / Odometer Tool)

Aplikasi Desktop GUI berbasis **Python 3** dan **Tkinter** untuk membaca, mengedit, menyimpan, dan menulis (flash) data IC EEPROM seri **24Cxxx (I2C)**, **93Cxxx (Microwire)**, dan **25xxx/95xxx (SPI)** yang umum digunakan pada panel instrumen (speedometer), ECU, BCM, dan immobilizer kendaraan (mobil & motor).

Didesain cross-platform untuk **CachyOS / Arch Linux** dan **Windows 10/11**.

---

## Fitur Utama

1. **🔌 Hubungkan Alat (Connect)**: Mendeteksi hardware USB Programmer CH341A. Jika perangkat belum dicolokkan, otomatis mengaktifkan **Mode Simulasi (Demo)** agar GUI dan Hex Editor dapat langsung diuji.
2. **📖 Membaca Chip (Read)**: Menarik seluruh data biner dari IC EEPROM secara multithreaded (tanpa membuat UI freezing/macet).
3. **💻 Hex Editor Interaktif**: Format tampilan ala NeoProgrammer & HxD dengan kolom Offset, 16 Hex Bytes, dan Visualisasi ASCII. Dapat mengedit byte secara langsung via double click.
4. **💾 Buka & Simpan File**: Memuat dan mengekspor dump data biner ke format `.bin` dan `.hex`.
5. **🔥 Tulis Chip (Flash/Write)**: Menyuntikkan data biner baru kembali ke IC EEPROM via SOIC8 Clip.
6. **📝 Konsol Log Status Real-Time**: Menampilkan indikator progress bar dan log histori setiap aksi komunikasi USB.

---

## 🛠️ Peralatan Hardware yang Dibutuhkan

Untuk membaca dan menyuntikkan data ke IC EEPROM melalui port USB laptop/PC, Anda membutuhkan peralatan berikut:

1. **CH341A USB Programmer Board** *(Utama)*:
   - Modul modul USB programmer murah yang mendukung protokol I2C (24Cxxx) dan SPI/Microwire (93Cxxx / 25xxx).
   - Pastikan posisi jumper set berada di posisi **I2C/SPI** (bukan EPP/TTL).

2. **SOIC8 / SOP8 Test Clip** *(Sangat Direkomendasikan)*:
   - Klem/penjepit 8-pin khusus untuk menjepit IC EEPROM tipe SMD langsung di PCB speedometer **tanpa perlu mencabut/menysolder chip**.
   - **PENTING**: Pin 1 (kabel berwarna merah) pada clip harus dipasang sejajar dengan titik/titik sudut (Dot/Pin 1) pada IC EEPROM.

3. **SOP8 to DIP8 Adapter Socket**:
   - Digunakan jika IC EEPROM dilepas dari PCB speedometer dan dipasang ke socket adapter (lebar 150mil atau 208mil).

4. **Adapter Converter Seri 93Cxxx (Khusus Seri 93C)**:
   - Modul adapter tambahan khusus untuk menyesuaikan urutan pinout seri 93C46/56/66/76/86 (Microwire) ke header CH341A.

5. **Kabel Jumper DuPont (Female-to-Female)**:
   - Digunakan untuk koneksi manual jika titik tes (*testpoint*) pada PCB speedometer menggunakan pin header.

> [!TIP]
> **Tips Pembacaan Aman**: Lepas soket aki atau catu daya 12V dari panel instrumen speedometer sebelum menjepitkan SOIC8 clip untuk mencegah interferensi listrik atau kerusakan pada MCU.

---

## 📖 Panduan Langkah Demi Langkah: Membaca Data Speedometer Setelah Dashboard Dilepas

Berikut adalah urutan pengerjaan saat panel speedometer sudah dilepas dari mobil:

1. **Buka Casing Plastik Speedometer**:
   - Lepaskan klip/baut casing plastik pelindung hingga PCB instrumen terlihat.

2. **Cari & Identifikasi IC EEPROM di PCB**:
   - Cari chip berukuran kecil berkaki 8 (SMD SOP8/SOIC8).
   - Perhatikan kode tulisan di atas chip: `24C04`, `24C08`, `24C16`, `93C46`, `93C56`, `93C66`, `93C76`, atau `93C86`.
   - Cari **Titik (Dot/Pin 1)** pada sudut chip.

3. **Jepitkan SOIC8 Test Clip**:
   - Jepitkan SOIC8 clip ke kaki IC EEPROM.
   - **KUNCI UTAMA**: Kabel warna **MERAH (Pin 1)** pada clip harus lurus sejajar dengan **Titik (Pin 1)** pada IC.
   - Hubungkan soket adapter clip ke header CH341A (Slot **24/25 I2C** untuk seri 24Cxxx, atau Slot **SPI/93C Adapter** untuk seri 93Cxxx).

4. **Colokkan CH341A ke Port USB Laptop**:
   - Tancapkan USB CH341A ke laptop (LED indikator merah di alat akan menyala).

5. **Baca Data di Aplikasi**:
   - Buka aplikasi **EEPROM Programmer CH341A** (klik 2x `dist/EEPROM_Programmer`).
   - Klik tombol **🔌 1. Hubungkan Alat**.
   - Pilih **Seri Chip** & **Tipe IC Target** sesuai kode chip di PCB (misal: `93C66 (x16)`).
   - Klik tombol **📖 2. Membaca Chip (Read)**.
   - Data biner Hex akan muncul otomatis di tabel Hex Editor!

6. **Wajib Simpan File Original (Backup)**:
   - **WAJIB**: Klik **💾 4. Simpan File (.bin)** dan simpan dengan nama `Speedo_Ori_Backup.bin` **SEBELUM** Anda mengubah nilai angka kilometer/odometer!

---

## Panduan Instalasi & Jalankan

### A. Di CachyOS / Arch Linux (Recommended)

1. **Install Dependensi System (Tkinter, PyUSB, & Libusb)**:
   ```bash
   sudo pacman -S tk python-pyusb libusb
   ```

2. **Pasang Udev Rules USB CH341A (Agar dapat diakses tanpa `sudo`)**:
   ```bash
   echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1a86", ATTR{idProduct}=="7523", MODE="0666", GROUP="uucp"' | sudo tee /etc/udev/rules.d/99-ch341a.rules
   echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="1a86", ATTR{idProduct}=="5512", MODE="0666", GROUP="uucp"' | sudo tee -a /etc/udev/rules.d/99-ch341a.rules
   sudo udevadm control --reload
   ```
   *Cabut dan colokkan kembali dongle CH341A Anda.*

3. **Jalankan Aplikasi**:
   - **Mode Direct Executable (Tanpa Terminal / Tanpa Install)**:
     Cukup klik 2x file [`dist/EEPROM_Programmer`](file:///home/barrr/Documents/koreksi_kilometer/dist/EEPROM_Programmer) atau via Menu Aplikasi **"EEPROM Programmer CH341A"**.
   - **Mode Python Script**:
     ```bash
     python3 main.py
     ```
   ```bash
   python3 main.py
   ```

---

### B. Di Windows 10/11

1. **Install Dependensi Python**:
   ```cmd
   pip install -r requirements.txt
   ```

2. **Driver USB CH341A**:
   - Pastikan driver CH341PAR / CH341SER atau driver Zadig (libusb-win32) telah terinstall di Windows.

3. **Jalankan Aplikasi**:
   ```cmd
   python main.py
   ```

---

## Struktur File Proyek

- [`main.py`](file:///home/barrr/Documents/koreksi_kilometer/main.py): Entrypoint GUI aplikasi Tkinter utama.
- [`ch341_driver.py`](file:///home/barrr/Documents/koreksi_kilometer/ch341_driver.py): Hardware Abstraction Layer (HAL) untuk komunikasi USB CH341A dengan komentar lengkap Bahasa Indonesia.
- [`hex_editor.py`](file:///home/barrr/Documents/koreksi_kilometer/hex_editor.py): Widget Hex Editor interaktif (Offset, Hex Grid, ASCII View, Search & Data Inspector).
- [`odometer_calculator.py`](file:///home/barrr/Documents/koreksi_kilometer/odometer_calculator.py): Modul kalkulator konversi algoritma kilometer odometer.
- [`chip_database.py`](file:///home/barrr/Documents/koreksi_kilometer/chip_database.py): Database spesifikasi IC EEPROM (24Cxxx, 93Cxxx, 25xxx).
- [`PANDUAN_FUNGSI_TOMBOL.md`](file:///home/barrr/Documents/koreksi_kilometer/PANDUAN_FUNGSI_TOMBOL.md): Panduan lengkap penjelasan fungsi setiap tombol & input aplikasi.
- [`requirements.txt`](file:///home/barrr/Documents/koreksi_kilometer/requirements.txt): Daftar dependensi Python (`pyusb`).
