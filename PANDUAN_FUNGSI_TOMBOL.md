# 📖 Panduan Lengkap Fungsi Tombol & Fitur Aplikasi EEPROM Programmer CH341A

Dokumen ini berisi panduan mendalam mengenai fungsi dari setiap **tombol**, **dropdown**, **kolom input**, dan **panel interaktif** pada aplikasi GUI EEPROM Programmer & Tool Koreksi Kilometer Speedometer.

---

## 🧭 Daftar Isi
1. [Toolbar Tombol Aksi Utama](#1-toolbar-tombol-aksi-utama)
2. [Panel Konfigurasi Target IC EEPROM](#2-panel-konfigurasi-target-ic-eeprom)
3. [Panel Koreksi Kilometer Instant (Odometer Calculator)](#3-panel-koreksi-kilometer-instant-odometer-calculator)
4. [Hex Editor, Fitur Search & Data Inspector](#4-hex-editor-fitur-search--data-inspector)
5. [Konsol Log Status & Progress Bar](#5-konsol-log-status--progress-bar)
6. [Alur Kerja Pengerjaan Aman (Best Practices)](#6-alur-kerja-pengerjaan-aman-best-practices)

---

## 1. 🔘 Toolbar Tombol Aksi Utama

Terletak di bagian atas aplikasi di bawah banner judul:

| Tombol / Fitur | Ikon | Fungsi & Cara Penggunaan |
| :--- | :---: | :--- |
| **Hubungkan Alat** | 🔌 | **Mendeteksi Programmer USB CH341A**.<br>Memeriksa apakah dongle CH341A sudah dicolokkan ke port USB. Jika alat belum dicolokkan, aplikasi otomatis aktif dalam *Mode Simulasi Demo* agar fitur Hex Editor tetap dapat diuji. |
| **Membaca Chip (Read)** | 📖 | **Membaca Data Dump EEPROM**.<br>Menarik seluruh isi data biner dari IC EEPROM yang dijepit SOIC8 clip dan menampilkannya secara langsung ke tabel Hex Editor. |
| **Buka File** | 📂 | **Memuat File Biner Laptop**.<br>Membuka file dump biner (`.bin` atau `.hex`) dari folder laptop/PC Anda ke dalam Hex Editor untuk diperiksa atau diedit. |
| **Simpan File** | 💾 | **Mengekspor File Dump Biner**.<br>Mengekspor isi buffer Hex Editor menjadi file biner (`.bin` atau `.hex`). Digunakan untuk menyimpan **backup original** atau file editan baru. |
| **Tulis (Flash/Write)** | 🔥 | **Menyuntikkan Data Ke Chip**.<br>Menuliskan kembali data biner hasil editan dari Hex Editor langsung ke dalam chip IC EEPROM di PCB speedometer. |

---

## 2. 🎛️ Panel Konfigurasi Target IC EEPROM

Panel ini digunakan untuk menentukan jenis chip EEPROM pada speedometer yang sedang Anda kerjakan:

- **Seri Chip (Dropdown)**:
  - `24Cxxx (I2C)`: Untuk speedometer Honda (Vario, Beat, Accord), Yamaha (NMAX, Aerox), Toyota lama (Corolla, Soluna), Hyundai, Kia.
  - `93Cxxx (Microwire)`: Sangat mendominasi speedometer mobil Jepang modern (Avanza, Innova, Rush, Yaris, Vios, Fortuner, Jazz, Brio, Mobilio, Ertiga, Pajero, Livina).
  - `25xxx / 95xxx (SPI)`: Umumnya untuk speedometer/airbag mobil Eropa (VW, Audi, BMW, Mercedes) & ECU.
- **Tipe IC Target (Dropdown)**:
  - Memilih model & kapasitas IC spesifik (contoh: `24C04`, `93C56`, `93C66 (x16)`, `93C86 (x16)`).
- **Label Informasi Spesifikasi (Kuning/Emas)**:
  - Menampilkan kapasitas memori (Bytes), tipe protokol, serta contoh jenis kendaraan yang menggunakan chip tersebut.

---

## 3. 🚗 Panel Koreksi Kilometer Instant (Odometer Calculator)

Fitur khusus untuk mengonversi angka kilometer target menjadi kode Hexadecimal secara otomatis:

- **Merk / Model Kendaraan (Dropdown Preset)**:
  - `Denso 16-bit (Toyota/Daihatsu/Honda)`: Algoritma standar untuk Toyota Avanza, Innova, Rush, Yaris, Vios, Fortuner, Honda Jazz, Brio, Mobilio, Suzuki Ertiga.
  - `Nissan / Mitsubishi 16-bit`: Algoritma untuk Nissan Grand Livina, March, Juke, Mitsubishi Pajero Sport, Xpander.
  - `Honda Vario / NMAX Motor`: Algoritma untuk speedometer sepeda motor digital.
  - `Direct Word 16-bit (Standard)`: Algoritma konversi 16-bit standar.
- **Target KM Baru (Input Box)**:
  - Tempat Anda mengetikkan nilai kilometer baru yang diinginkan (contoh: `85000` untuk 85.000 KM).
- **Offset (Hex) (Input Box)**:
  - Alamat awal lokasi penyimpanan data kilometer di memori Hex (default `0000` atau `0020`).
- **✨ TERAPKAN KILOMETER BARU KE HEX (Tombol)**:
  - Mengonversi nilai KM target ke dalam susunan byte Hex secara presisi dan menyuntikkannya ke tabel Hex Editor. Byte yang berubah akan ditandai dengan **warna Merah/Oranye**.

---

## 4. 💻 Hex Editor, Fitur Search & Data Inspector

Panel tengah interaktif untuk memeriksa dan merubah isi byte biner memori:

- **🔍 Cari (Hex / Text)**:
  - Ketik pola byte Hex (misal: `A5 5A`) atau teks ASCII lalu tekan Enter untuk menemukan lokasi data.
- **📍 Lompat ke Offset**:
  - Ketik alamat offset Hex (misal: `0020`) untuk melompat langsung ke baris alamat tersebut.
- **Tabel Grid Hex Editor**:
  - `OFFSET`: Baris alamat memori Hex (`00000000:`).
  - `00 - 0F`: Grid 16 Byte data Hexadecimal per baris. Anda dapat mengedit sel byte secara langsung dengan **Double-Click** pada angka hex tersebut.
  - `ASCII Dump`: Visualisasi karakter teks ASCII.
- **Data Inspector Bar (Bawah Hex Editor)**:
  - `16-bit LE (Little Endian)`: Menampilkan kalkulasi otomatis nilai 16-bit dari byte yang sedang diklik (sangat berguna untuk mengecek nilai kilometer manual).
  - `16-bit BE (Big Endian)`: Menampilkan nilai 16-bit format Big Endian.

---

## 5. 📝 Konsol Log Status & Progress Bar

Terletak di bagian paling bawah layar:

- **Progress Bar**: Indikator visual persentase (0% - 100%) saat proses pembacaan atau penulisan chip sedang berjalan.
- **Text Log Console**: Catatan histori real-time setiap aktivitas komunikasi USB (contoh: *"Tersambung ke CH341A"*, *"Selesai membaca 512 Bytes"*, *"Koreksi KM Diterapkan"*, *"Flash Selesai"*).

---

## 6. 🛡️ Alur Kerja Pengerjaan Aman (Best Practices)

1. **Langkah 1**: Jepitkan SOIC8 clip ke chip EEPROM speedometer (pastikan kabel MERAH di Pin 1).
2. **Langkah 2**: Klik **🔌 1. Hubungkan Alat**.
3. **Langkah 3**: Pilih seri chip dan tipe IC target (misal `93C66 (x16)`).
4. **Langkah 4**: Klik **📖 2. Membaca Chip (Read)**.
5. **Langkah 5 (WAJIB)**: Klik **💾 4. Simpan File (.bin)** dan simpan sebagai backup original (`Speedo_Ori.bin`).
6. **Langkah 6**: Masukkan angka kilometer target pada **Panel Koreksi Kilometer Instant** lalu klik **✨ TERAPKAN KILOMETER BARU KE HEX**.
7. **Langkah 7**: Klik **🔥 5. Tulis (Flash)** untuk menyuntikkan data baru kembali ke speedometer.
