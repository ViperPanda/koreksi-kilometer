#!/usr/bin/env python3
"""
Aplikasi Desktop GUI EEPROM Programmer Speedometer (CH341A)
Tema: Midnight Obsidian Slate & Sky Cyan Professional Edition.
Cross-Platform: Windows & CachyOS / Arch Linux.
"""

import os
import sys
import time
import threading

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError as e:
    print("\n" + "=" * 70)
    print("❌ ERROR: Pustaka C-Library Tkinter (libtk8.6.so) belum terpasang di CachyOS!")
    print("Silakan jalankan perintah berikut di Terminal untuk menginstalnya:\n")
    print("    sudo pacman -S tk\n")
    print("=" * 70 + "\n")
    sys.exit(1)

# Import modul lokal
from chip_database import CHIP_DATABASE, get_all_families, get_chip_list_by_family
from ch341_driver import CH341AProgrammer
from hex_editor import HexEditorWidget
from odometer_calculator import OdometerCalculator


class ModernButton(tk.Frame):
    """Widget Tombol Kustom Modern dengan Gradient Color & Hover Lighting Effect."""
    def __init__(self, parent, text, icon_str, bg_color, hover_color, command=None, width=155, height=42):
        super().__init__(parent, bg=bg_color, cursor="hand2", width=width, height=height)
        self.pack_propagate(False)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color

        self.label = tk.Label(
            self, text=f"{icon_str}  {text}", bg=bg_color, fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        self.label.pack(expand=True, fill=tk.BOTH)

        for w in (self, self.label):
            w.bind("<Enter>", self._on_hover)
            w.bind("<Leave>", self._on_leave)
            w.bind("<Button-1>", self._on_click)

    def _on_hover(self, e):
        self.config(bg=self.hover_color)
        self.label.config(bg=self.hover_color)

    def _on_leave(self, e):
        self.config(bg=self.bg_color)
        self.label.config(bg=self.bg_color)

    def _on_click(self, e):
        if self.command:
            self.command()


class EEPROMProgrammerApp:
    """
    Aplikasi Utama GUI EEPROM Programmer & Tool Koreksi Kilometer Speedometer.
    Tema: Midnight Obsidian Slate & Sky Cyan Professional Edition.
    """

    BG_DARK = "#0F172A"       # Slate 900
    BG_CARD = "#1E293B"       # Slate 800
    BORDER_COLOR = "#334155"  # Slate 700
    TEXT_MAIN = "#F8FAFC"     # Slate 50
    TEXT_MUTED = "#94A3B8"    # Slate 400
    ACCENT_CYAN = "#38BDF8"   # Sky Cyan 400

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚡ EEPROM Programmer CH341A - Master Tool Koreksi Kilometer Speedometer")
        self.root.geometry("1180x820")
        self.root.minsize(1050, 720)
        self.root.configure(bg=self.BG_DARK)

        self.programmer = CH341AProgrammer()
        self.current_chip_name = "24C04"
        self.is_busy = False

        self._configure_styles()
        self._create_menu_bar()
        self._create_header_banner()
        self._create_toolbar()
        self._create_chip_config_panel()
        self._create_odometer_correction_panel()
        self._create_main_content()
        self._create_status_log_panel()

        self.log_message("=== EEPROM Programmer Speedometer Tool v3.0 (Midnight Edition) ===")
        self.log_message(f"Sistem Operasi: {sys.platform.upper()} (CachyOS / Linux & Windows)")
        self.log_message("Klik 'Hubungkan Alat' untuk mendeteksi programmer USB CH341A.\n")

    def _configure_styles(self):
        """Konfigurasi gaya ttk widget."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", font=("Segoe UI", 10), background=self.BG_DARK, foreground=self.TEXT_MAIN)
        self.style.configure("TFrame", background=self.BG_DARK)
        self.style.configure("TLabelframe", background=self.BG_CARD, foreground=self.ACCENT_CYAN, relief=tk.FLAT)
        self.style.configure("TLabelframe.Label", background=self.BG_CARD, foreground=self.ACCENT_CYAN, font=("Segoe UI", 10, "bold"))
        self.style.configure("TCombobox", fieldbackground="#0F172A", background="#0F172A", foreground="#FFFFFF", bordercolor="#334155")

    def _create_menu_bar(self):
        """Membuat Menu Bar Atas."""
        menubar = tk.Menu(self.root, bg=self.BG_DARK, fg=self.TEXT_MAIN)

        file_menu = tk.Menu(menubar, tearoff=0, bg=self.BG_CARD, fg=self.TEXT_MAIN)
        file_menu.add_command(label="📂 Buka File Dump (.bin / .hex)", command=self.open_file)
        file_menu.add_command(label="💾 Simpan File Dump (.bin)", command=self.save_file_bin)
        file_menu.add_command(label="💾 Simpan File Dump (.hex)", command=self.save_file_hex)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.BG_CARD, fg=self.TEXT_MAIN)
        tools_menu.add_command(label="🔌 Deteksi Ulang CH341A", command=self.connect_device)
        tools_menu.add_command(label="🐧 Pasang Udev Rules (CachyOS/Linux)", command=self.show_udev_instructions)
        menubar.add_cascade(label="Alat & Pengaturan", menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=0, bg=self.BG_CARD, fg=self.TEXT_MAIN)
        help_menu.add_command(label="⏱️ Cara Singkat Koreksi Odometer", command=self.show_odo_guide)
        help_menu.add_command(label="🚗 Panduan Seri IC per-Mobil", command=self.show_car_guide)
        help_menu.add_command(label="📍 Panduan Pinout SOIC8 Clip", command=self.show_soic_guide)
        help_menu.add_command(label="ℹ️ Tentang Aplikasi", command=self.show_about)
        menubar.add_cascade(label="Bantuan", menu=help_menu)

        self.root.config(menu=menubar)

    def _create_header_banner(self):
        """Header Banner dengan Badge Status & Accent Sky Cyan."""
        header_card = tk.Frame(self.root, bg=self.BG_CARD, padx=16, pady=12, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        header_card.pack(fill=tk.X, padx=12, pady=(10, 5))

        title_frame = tk.Frame(header_card, bg=self.BG_CARD)
        title_frame.pack(side=tk.LEFT)

        tk.Label(
            title_frame, text="⚡ CH341A EEPROM PROGRAMMER MASTER",
            font=("Segoe UI", 14, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN
        ).pack(anchor=tk.W)
        
        tk.Label(
            title_frame, text="Speedometer & Odometer Mileage Correction Tool",
            font=("Segoe UI", 9), bg=self.BG_CARD, fg=self.TEXT_MUTED
        ).pack(anchor=tk.W)

        self.lbl_status_badge = tk.Label(
            header_card, text="● DISCONNECTED", font=("Segoe UI", 9, "bold"),
            bg="#334155", fg="#94A3B8", padx=14, pady=6
        )
        self.lbl_status_badge.pack(side=tk.RIGHT)

    def _create_toolbar(self):
        """Toolbar Tombol Aksi Utama."""
        toolbar_card = tk.Frame(self.root, bg=self.BG_CARD, padx=12, pady=10, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        toolbar_card.pack(fill=tk.X, padx=12, pady=3)

        ModernButton(toolbar_card, "Hubungkan Alat", "🔌", "#059669", "#10B981", self.connect_device, width=145).pack(side=tk.LEFT, padx=3)
        ModernButton(toolbar_card, "Membaca Chip", "📖", "#0284C7", "#0EA5E9", self.read_chip, width=145).pack(side=tk.LEFT, padx=3)
        ModernButton(toolbar_card, "Buka File", "📂", "#475569", "#64748B", self.open_file, width=125).pack(side=tk.LEFT, padx=3)
        ModernButton(toolbar_card, "Simpan File", "💾", "#475569", "#64748B", self.save_file_bin, width=125).pack(side=tk.LEFT, padx=3)
        ModernButton(toolbar_card, "Tulis (Flash)", "🔥", "#DC2626", "#EF4444", self.write_chip, width=145).pack(side=tk.LEFT, padx=3)
        ModernButton(toolbar_card, "Pulihkan Backup", "🔄", "#6B21A8", "#7E22CE", self.restore_backup, width=160).pack(side=tk.LEFT, padx=3)

    def _create_chip_config_panel(self):
        """Panel Pemilihan Target Chip EEPROM."""
        config_card = tk.Frame(self.root, bg=self.BG_CARD, padx=16, pady=10, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        config_card.pack(fill=tk.X, padx=12, pady=3)

        row1 = tk.Frame(config_card, bg=self.BG_CARD)
        row1.pack(fill=tk.X)

        tk.Label(row1, text="Seri Chip:", bg=self.BG_CARD, fg=self.TEXT_MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=4)
        
        all_families = get_all_families()
        self.combo_family = ttk.Combobox(row1, values=all_families, state="readonly", width=44)
        if len(all_families) > 1:
            self.combo_family.set(all_families[1])
            default_chips = get_chip_list_by_family(all_families[1])
        else:
            default_chips = get_chip_list_by_family(all_families[0])
            
        self.combo_family.grid(row=0, column=1, padx=4, pady=2)
        self.combo_family.bind("<<ComboboxSelected>>", self._on_family_changed)

        tk.Label(row1, text="Tipe IC & Mobil Target:", bg=self.BG_CARD, fg=self.TEXT_MUTED, font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(14, 4))
        
        default_chips = get_chip_list_by_family("24Cxxx (I2C)")
        self.combo_chip = ttk.Combobox(row1, values=default_chips, state="readonly", width=44)
        if len(default_chips) > 2:
            self.combo_chip.set(default_chips[2])
            self.current_chip_name = default_chips[2]

        self.combo_chip.grid(row=0, column=3, padx=4, pady=2)
        self.combo_chip.bind("<<ComboboxSelected>>", self._on_chip_changed)

        self.lbl_chip_info = tk.Label(
            row1, text="Ukuran: 512 Bytes | Protokol: I2C | Honda Vario 125/150, Beat Fi",
            bg=self.BG_CARD, fg="#F59E0B", font=("Segoe UI", 9, "bold")
        )
        self.lbl_chip_info.grid(row=0, column=4, sticky=tk.W, padx=(16, 4))

    def _create_odometer_correction_panel(self):
        """PANEL KOREKSI KILOMETER INSTANT."""
        odo_card = tk.LabelFrame(
            self.root, text="🚗 PANEL KOREKSI KILOMETER INSTANT (ODOMETER CALCULATOR)",
            padx=12, pady=10, bg=self.BG_CARD, fg=self.ACCENT_CYAN, font=("Segoe UI", 10, "bold")
        )
        odo_card.pack(fill=tk.X, padx=12, pady=4)

        row = tk.Frame(odo_card, bg=self.BG_CARD)
        row.pack(fill=tk.X)

        tk.Label(row, text="Merk / Model Kendaraan:", bg=self.BG_CARD, fg=self.TEXT_MAIN, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=4)
        
        self.combo_car_preset = ttk.Combobox(
            row,
            values=[
                "Denso 16-bit (Toyota/Daihatsu/Honda)",
                "Nissan / Mitsubishi 16-bit",
                "Honda Vario / NMAX Motor",
                "Direct Word 16-bit (Standard)"
            ],
            state="readonly",
            width=32
        )
        self.combo_car_preset.set("Denso 16-bit (Toyota/Daihatsu/Honda)")
        self.combo_car_preset.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(row, text="Target KM Baru:", bg=self.BG_CARD, fg="#34D399", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(14, 4))
        
        self.entry_target_km = tk.Entry(row, font=("Consolas", 11, "bold"), width=12, bg="#0F172A", fg="#34D399", insertbackground="#FFFFFF", justify="center", bd=3)
        self.entry_target_km.insert(0, "85000")
        self.entry_target_km.grid(row=0, column=3, padx=4, pady=2)

        tk.Label(row, text="Offset (Hex):", bg=self.BG_CARD, fg=self.TEXT_MUTED, font=("Segoe UI", 9)).grid(row=0, column=4, sticky=tk.W, padx=(14, 4))
        
        self.entry_km_offset = tk.Entry(row, font=("Consolas", 10), width=8, bg="#0F172A", fg="#FFFFFF", insertbackground="#FFFFFF", justify="center", bd=3)
        self.entry_km_offset.insert(0, "0000")
        self.entry_km_offset.grid(row=0, column=5, padx=4, pady=2)

        # Tombol Deteksi Otomatis Lokasi KM
        btn_auto_detect = tk.Button(
            row, text="🔍 DETEKSI OTOMATIS LOKASI KM", bg="#0284C7", fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, activebackground="#0EA5E9",
            command=self.auto_detect_km, padx=10, pady=4, cursor="hand2"
        )
        btn_auto_detect.grid(row=0, column=6, padx=(10, 4), pady=2)

        # Tombol Terapkan KM (Warna Amber Gold)
        btn_apply_km = tk.Button(
            row, text="✨ TERAPKAN KILOMETER BARU KE HEX", bg="#D97706", fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"), relief=tk.FLAT, activebackground="#F59E0B",
            command=self.apply_km_correction, padx=14, pady=4, cursor="hand2"
        )
        btn_apply_km.grid(row=0, column=7, padx=(8, 4), pady=2)

    def auto_detect_km(self):
        """Mendeteksi lokasi offset kilometer secara otomatis dari data dump."""
        buffer = self.hex_editor.get_data()
        found_offset, estimated_km = OdometerCalculator.auto_detect_km_offset(buffer)

        self.entry_km_offset.delete(0, tk.END)
        self.entry_km_offset.insert(0, f"{found_offset:04X}")

        self.hex_editor.update_inspector(found_offset)

        if estimated_km > 0:
            self.log_message(f"🔍 Lokasi KM Terdeteksi di Offset 0x{found_offset:04X}! Estimasi KM: {estimated_km:,} KM")
            messagebox.showinfo(
                "Lokasi Kilometer Terdeteksi",
                f"Sistem menemukan lokasi data Kilometer pada Offset: 0x{found_offset:04X}\n\n"
                f"Perkiraan Kilometer Saat Ini: ~{estimated_km:,} KM\n\n"
                f"Kolom Offset telah otomatis diatur ke 0x{found_offset:04X}.",
                parent=self.root
            )
        else:
            self.log_message(f"🔍 Offset diatur ke alamat 0x{found_offset:04X}.")
            messagebox.showinfo("Deteksi Offset", f"Kolom Offset diatur ke alamat 0x{found_offset:04X}.", parent=self.root)

    def apply_km_correction(self):
        """Kalkulasi KM target & suntikkan ke Hex Editor."""
        km_str = self.entry_target_km.get().strip()
        preset = self.combo_car_preset.get()
        offset_hex = self.entry_km_offset.get().strip()

        try:
            target_km = int(km_str)
            if target_km < 0 or target_km > 999999:
                messagebox.showerror("Error", "Nilai Kilometer harus antara 0 dan 999.999 KM", parent=self.root)
                return

            offset = int(offset_hex, 16)
        except ValueError:
            messagebox.showerror("Format Error", "Masukkan angka Kilometer dan Offset Hexadecimal yang valid!", parent=self.root)
            return

        pattern_bytes, _ = OdometerCalculator.calculate_hex_bytes(target_km, preset)
        buffer = self.hex_editor.get_data()
        if offset + len(pattern_bytes) > len(buffer):
            messagebox.showerror("Offset Error", f"Offset 0x{offset:04X} terlalu besar untuk kapasitas chip!", parent=self.root)
            return

        for i in range(len(pattern_bytes)):
            idx = offset + i
            buffer[idx] = pattern_bytes[i]
            self.hex_editor.modified_indices.add(idx)

        self.hex_editor.set_data(buffer)
        self.hex_editor.update_inspector(offset)

        self.log_message(f"✨ Koreksi KM Diterapkan: {target_km:,} KM disuntikkan ke Offset 0x{offset:04X}!")
        messagebox.showinfo(
            "Koreksi Kilometer Berhasil",
            f"Nilai Kilometer {target_km:,} KM berhasil diterapkan ke Hex Editor di Offset 0x{offset:04X}!\n\n"
            "Perubahan byte ditandai dengan warna Merah/Oranye.\n"
            "Klik 'Tulis (Flash)' untuk menyuntikkan ke IC EEPROM speedometer mobil.",
            parent=self.root
        )

    def _create_main_content(self):
        """Area Utama Hex Editor."""
        content_frame = tk.Frame(self.root, bg=self.BG_DARK)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.hex_editor = HexEditorWidget(content_frame)
        self.hex_editor.pack(fill=tk.BOTH, expand=True)

    def _create_status_log_panel(self):
        """Panel Konsol Log Status di Bagian Bawah."""
        log_card = tk.Frame(self.root, bg=self.BG_CARD, padx=12, pady=6, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        log_card.pack(fill=tk.X, padx=12, pady=(4, 10))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(log_card, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 3))

        console_frame = tk.Frame(log_card, bg="#0B132B")
        console_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            console_frame, height=3, font=("Consolas", 9),
            bg="#0B132B", fg="#34D399", insertbackground="#FFFFFF",
            relief=tk.FLAT, wrap=tk.WORD
        )
        v_scroll = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # =========================================================================
    # EVENT HANDLERS & LOGIKA BISNIS
    # =========================================================================

    def log_message(self, message: str):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_text.insert(tk.END, timestamp + message + "\n")
        self.log_text.see(tk.END)

    def _on_family_changed(self, event):
        family = self.combo_family.get()
        chips = get_chip_list_by_family(family)
        self.combo_chip.config(values=chips)
        if chips:
            self.combo_chip.set(chips[0])
            self._on_chip_changed(None)

    def _on_chip_changed(self, event):
        chip_name = self.combo_chip.get()
        self.current_chip_name = chip_name
        spec = CHIP_DATABASE.get(chip_name)

        if spec:
            info_text = f"Ukuran: {spec['size_bytes']} Bytes | Protokol: {spec['protocol']} | {spec['common_uses']}"
            self.lbl_chip_info.config(text=info_text)

            current_data = self.hex_editor.get_data()
            if len(current_data) != spec['size_bytes']:
                new_buf = bytearray([0xFF] * spec['size_bytes'])
                self.hex_editor.set_data(new_buf)

            self.log_message(f"Target Chip dipilih: {chip_name} ({spec['size_bytes']} Bytes)")

    def connect_device(self):
        self.log_message("Mencari programmer USB CH341A...")
        success, msg = self.programmer.connect()

        if self.programmer.is_mock_mode:
            self.lbl_status_badge.config(text="● MODE SIMULASI (DEMO)", bg="#F59E0B", fg="#0F172A")
            self.log_message("PERINGATAN: " + msg)
            messagebox.showwarning(
                "Mode Simulasi Aktif",
                f"{msg}\n\nAplikasi dapat diuji untuk memuat file .bin, mengedit Hex, dan kalkulasi Odometer.\n"
                "Colokkan hardware CH341A ke USB untuk membaca chip fisik.",
                parent=self.root
            )
        elif success:
            self.lbl_status_badge.config(text="● CH341A TERHUBUNG", bg="#10B981", fg="#FFFFFF")
            self.log_message("Koneksi Berhasil: " + msg)
            messagebox.showinfo("Koneksi Berhasil", msg, parent=self.root)
        else:
            self.lbl_status_badge.config(text="● KONEKSI GAGAL", bg="#EF4444", fg="#FFFFFF")
            self.log_message("Gagal Koneksi: " + msg)
            messagebox.showerror("Koneksi Gagal", msg, parent=self.root)

    def read_chip(self):
        if self.is_busy:
            return

        chip_spec = CHIP_DATABASE.get(self.current_chip_name)
        if not chip_spec:
            return

        if not self.programmer.is_connected:
            self.connect_device()

        def _async_read():
            self.is_busy = True
            self.progress_var.set(0)
            self.log_message(f"Memulai proses pembacaan chip {self.current_chip_name}...")

            try:
                protocol = chip_spec["protocol"]
                if protocol == "I2C":
                    dump_data = self.programmer.read_i2c_eeprom(chip_spec, lambda p: self.progress_var.set(p))
                elif protocol == "MICROWIRE":
                    dump_data = self.programmer.read_microwire_eeprom(chip_spec, lambda p: self.progress_var.set(p))
                else:
                    dump_data = self.programmer.read_spi_eeprom(chip_spec, lambda p: self.progress_var.set(p))

                self.root.after(0, lambda: self._on_read_finished(dump_data))

            except Exception as e:
                err_str = str(e)
                self.root.after(0, lambda: self._on_read_failed(err_str))

        threading.Thread(target=_async_read, daemon=True).start()

    def _on_read_finished(self, dump_data: bytearray):
        self.is_busy = False
        self.progress_var.set(100)
        self.hex_editor.set_data(dump_data)
        self.log_message(f"✅ Selesai! Berhasil membaca {len(dump_data)} Bytes data Hexadecimal dari chip {self.current_chip_name}.")
        messagebox.showinfo("Pembacaan Selesai", f"Berhasil membaca {len(dump_data)} bytes dari EEPROM!", parent=self.root)

    def _on_read_failed(self, err_msg: str):
        self.is_busy = False
        self.progress_var.set(0)
        self.log_message(f"❌ Gagal Membaca Chip: {err_msg}")
        messagebox.showerror("Gagal Membaca Chip", f"Terjadi kesalahan saat membaca chip:\n{err_msg}", parent=self.root)

    def write_chip(self):
        if self.is_busy:
            return

        chip_spec = CHIP_DATABASE.get(self.current_chip_name)
        data_to_write = self.hex_editor.get_data()

        confirm = messagebox.askyesno(
            "Konfirmasi Tulis/Flash EEPROM",
            f"PERINGATAN: Menyuntikkan (write) data baru akan menimpa isi IC EEPROM {self.current_chip_name}.\n\n"
            "Pastikan SOIC8 clip terpasang dengan kuat dan urutan PIN 1 (Kabel Merah) sesuai.\nLanjutkan?",
            icon="warning", parent=self.root
        )
        if not confirm:
            return

        def _async_write():
            self.is_busy = True
            self.progress_var.set(0)
            self.log_message(f"Memulai flashing data baru ke chip {self.current_chip_name}...")

            try:
                protocol = chip_spec["protocol"]
                if protocol == "I2C":
                    res = self.programmer.write_i2c_eeprom(chip_spec, data_to_write, lambda p: self.progress_var.set(p))
                elif protocol == "MICROWIRE":
                    res = self.programmer.write_microwire_eeprom(chip_spec, data_to_write, lambda p: self.progress_var.set(p))
                else:
                    res = self.programmer.write_spi_eeprom(chip_spec, data_to_write, lambda p: self.progress_var.set(p))

                self.root.after(0, self._on_write_finished)

            except Exception as e:
                err_str = str(e)
                self.root.after(0, lambda: self._on_write_failed(err_str))

        threading.Thread(target=_async_write, daemon=True).start()

    def _on_write_finished(self):
        self.is_busy = False
        self.progress_var.set(100)
        self.log_message(f"🔥 Proses Flash Selesai! Data berhasil disuntikkan ke IC EEPROM {self.current_chip_name}.")
        messagebox.showinfo("Proses Flash Selesai", "Data berhasil disuntikkan kembali ke EEPROM!", parent=self.root)

    def _on_write_failed(self, err_msg: str):
        self.is_busy = False
        self.progress_var.set(0)
        self.log_message(f"❌ Gagal Menulis Chip: {err_msg}")
        messagebox.showerror("Gagal Menulis Chip", f"Kesalahan flashing:\n{err_msg}", parent=self.root)

    def restore_backup(self):
        """Memuat file backup original (.bin) dan langsung menyuntikkannya kembali ke chip EEPROM."""
        if self.is_busy:
            return

        filepath = filedialog.askopenfilename(
            title="Pilih File Backup Original (.bin / .hex)",
            filetypes=[("Binary Backup Files", "*.bin *.dump"), ("Intel HEX Files", "*.hex"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "rb") as f:
                backup_data = f.read()

            filename = os.path.basename(filepath)
            chip_spec = CHIP_DATABASE.get(self.current_chip_name)

            if len(backup_data) != chip_spec["size_bytes"]:
                resp = messagebox.askyesno(
                    "Ukuran Berbeda",
                    f"Ukuran file backup '{filename}' ({len(backup_data)} bytes) berbeda dengan kapasitas chip "
                    f"{self.current_chip_name} ({chip_spec['size_bytes']} bytes).\n\nTetap lanjutkan pemulihan (restore)?",
                    parent=self.root
                )
                if not resp:
                    return

            confirm = messagebox.askyesno(
                "Konfirmasi Pulihkan Backup Original",
                f"APAKAH ANDA YAKIN INGIN MEMULIHKAN BACKUP ORIGINAL?\n\n"
                f"File Backup: '{filename}' ({len(backup_data)} bytes)\n"
                f"Target Chip: {self.current_chip_name}\n\n"
                "Proses ini akan mengembalikan data speedometer ke kondisi semula sebelum diedit.\nLanjutkan?",
                icon="warning",
                parent=self.root
            )
            if not confirm:
                return

            self.hex_editor.set_data(backup_data)

            if not self.programmer.is_connected:
                self.connect_device()

            def _async_restore():
                self.is_busy = True
                self.progress_var.set(0)
                self.log_message(f"🔄 Memulai proses pemulihan (restore) dari file '{filename}'...")

                try:
                    protocol = chip_spec["protocol"]
                    if protocol == "I2C":
                        res = self.programmer.write_i2c_eeprom(chip_spec, bytearray(backup_data), lambda p: self.progress_var.set(p))
                    elif protocol == "MICROWIRE":
                        res = self.programmer.write_microwire_eeprom(chip_spec, bytearray(backup_data), lambda p: self.progress_var.set(p))
                    else:
                        res = self.programmer.write_spi_eeprom(chip_spec, bytearray(backup_data), lambda p: self.progress_var.set(p))

                    self.root.after(0, lambda: self._on_restore_finished(filename))

                except Exception as e:
                    err_str = str(e)
                    self.root.after(0, lambda: self._on_write_failed(err_str))

            threading.Thread(target=_async_restore, daemon=True).start()

        except Exception as e:
            self.log_message(f"❌ Gagal memuat file backup: {e}")
            messagebox.showerror("Gagal Membuka File Backup", str(e), parent=self.root)

    def _on_restore_finished(self, filename: str):
        self.is_busy = False
        self.progress_var.set(100)
        self.log_message(f"🔄 Pemulihan Backup Selesai! Data dari '{filename}' berhasil dikembalikan ke IC EEPROM.")
        messagebox.showinfo("Pemulihan Selesai", f"Berhasil memulihkan data original dari '{filename}' ke EEPROM speedometer!", parent=self.root)

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Buka File Dump EEPROM",
            filetypes=[("Binary Dump Files", "*.bin *.dump"), ("Intel HEX Files", "*.hex"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "rb") as f:
                content = f.read()

            self.hex_editor.set_data(content)
            filename = os.path.basename(filepath)
            self.log_message(f"📂 Berhasil memuat file: '{filename}' ({len(content)} Bytes)")
            messagebox.showinfo("File Dimuat", f"File '{filename}' ({len(content)} bytes) berhasil dimuat!", parent=self.root)

        except Exception as e:
            self.log_message(f"❌ Gagal membuka file: {e}")
            messagebox.showerror("Gagal Membuka File", str(e), parent=self.root)

    def save_file_bin(self):
        filepath = filedialog.asksaveasfilename(
            title="Simpan File Dump Biner",
            defaultextension=".bin",
            filetypes=[("Binary Dump File", "*.bin"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            data = self.hex_editor.get_data()
            with open(filepath, "wb") as f:
                f.write(data)

            filename = os.path.basename(filepath)
            self.log_message(f"💾 File berhasil disimpan ke: '{filename}' ({len(data)} Bytes)")
            messagebox.showinfo("Simpan Berhasil", f"File '{filename}' berhasil disimpan!", parent=self.root)

        except Exception as e:
            self.log_message(f"❌ Gagal menyimpan file: {e}")
            messagebox.showerror("Gagal Menyimpan File", str(e), parent=self.root)

    def save_file_hex(self):
        filepath = filedialog.asksaveasfilename(
            title="Simpan File Intel HEX",
            defaultextension=".hex",
            filetypes=[("Intel HEX File", "*.hex"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            data = self.hex_editor.get_data()
            hex_lines = []
            for addr in range(0, len(data), 16):
                chunk = data[addr : addr + 16]
                count = len(chunk)
                checksum = (count + (addr >> 8) + (addr & 0xFF) + 0x00 + sum(chunk)) & 0xFF
                checksum = (256 - checksum) & 0xFF
                hex_str = "".join([f"{b:02X}" for b in chunk])
                hex_lines.append(f":{count:02X}{addr:04X}00{hex_str}{checksum:02X}")
            hex_lines.append(":00000001FF")

            with open(filepath, "w") as f:
                f.write("\n".join(hex_lines))

            filename = os.path.basename(filepath)
            self.log_message(f"💾 File Intel Hex disimpan: '{filename}'")
            messagebox.showinfo("Simpan Berhasil", f"File '{filename}' berhasil disimpan!", parent=self.root)

        except Exception as e:
            messagebox.showerror("Gagal Menyimpan", str(e), parent=self.root)

    def show_odo_guide(self):
        """Menampilkan panduan singkat cara mengubah odometer kilometer."""
        guide_text = (
            "PANDUAN SINGKAT KOREKSI KILOMETER ODOMETER:\n\n"
            "1. Hubungkan Programmer USB CH341A ke laptop & jepitkan SOIC8 clip ke IC EEPROM speedometer.\n"
            "2. Klik '🔌 Hubungkan Alat' lalu pilih 'Seri Chip' & 'Tipe IC Target' (misal: 93C66 x16).\n"
            "3. Klik '📖 Membaca Chip (Read)' untuk menarik data dump speedometer ke Hex Editor.\n"
            "4. WAJIB BACKUP: Klik '💾 Simpan File (.bin)' dan simpan dengan nama 'Ori_Backup.bin'.\n"
            "5. Pada '🚗 PANEL KOREKSI KILOMETER INSTANT':\n"
            "   - Pilih 'Merk / Model Kendaraan' Anda (Toyota/Honda/Nissan/Motor).\n"
            "   - Ketik angka kilometer baru (contoh: 85000).\n"
            "   - Klik '✨ TERAPKAN KILOMETER BARU KE HEX' (Byte terubah akan berwarna Merah/Oranye).\n"
            "6. Klik '🔥 Tulis (Flash)' untuk menyuntikkan data baru kembali ke IC EEPROM speedometer!"
        )
        messagebox.showinfo("Cara Singkat Koreksi Odometer", guide_text, parent=self.root)

    def show_car_guide(self):
        car_data = (
            "Daftar Jenis Chip EEPROM pada Speedometer Kendaraan:\n\n"
            "• Toyota Avanza / Xenia Lama: 93C46 / 93C56\n"
            "• Toyota Avanza Veloz / Grand New: 93C66 (x16)\n"
            "• Toyota Innova Lama / Yaris Bakpao: 93C56\n"
            "• Toyota Innova Reborn / Fortuner VRZ: 93C86\n"
            "• Honda Jazz GD8 / City Lama: 93C56\n"
            "• Honda Jazz GE8 / Brio / Mobilio / Freed: 93C66\n"
            "• Honda HR-V / CR-V Gen 4 / Civic FB: 93C86\n"
            "• Honda Vario 125/150/160 / Beat Fi: 24C04 / 24C08\n"
            "• Yamaha NMAX / Aerox / PCX: 24C08 / 93C66\n"
            "• Mitsubishi Pajero Sport / Xpander: 93C76\n"
            "• Nissan Grand Livina / March / Juke: 93C76\n"
            "• Ford Ranger / Everest: 24C16"
        )
        messagebox.showinfo("Panduan Chip EEPROM Kendaraan", car_data, parent=self.root)

    def show_udev_instructions(self):
        udev_code = (
            '# CH341A USB Programmer Udev Rule\n'
            'SUBSYSTEM=="usb", ATTR{idVendor}=="1a86", ATTR{idProduct}=="7523", MODE="0666", GROUP="uucp"\n'
            'SUBSYSTEM=="usb", ATTR{idVendor}=="1a86", ATTR{idProduct}=="5512", MODE="0666", GROUP="uucp"\n'
        )
        cmd_str = f"echo '{udev_code}' | sudo tee /etc/udev/rules.d/99-ch341a.rules && sudo udevadm control --reload"

        top = tk.Toplevel(self.root)
        top.title("Petunjuk Udev Rules CachyOS / Linux")
        top.geometry("560x310")
        top.configure(bg=self.BG_CARD)

        tk.Label(top, text="Setup Udev Rules untuk CachyOS / Arch Linux", font=("Segoe UI", 11, "bold"), bg=self.BG_CARD, fg=self.ACCENT_CYAN).pack(pady=10)
        
        txt = tk.Text(top, font=("Consolas", 9), wrap=tk.WORD, height=9, bg="#0F172A", fg="#F8FAFC", relief=tk.FLAT)
        txt.insert(tk.END, f"Jalankan perintah ini di Terminal:\n\n{cmd_str}\n\nSetelah itu, cabut dan colokkan kembali dongle CH341A Anda.")
        txt.pack(padx=12, pady=5, fill=tk.BOTH, expand=True)

    def show_soic_guide(self):
        guide = (
            "PANDUAN KONEKSI SOIC8 CLIP KE SPEEDOMETER:\n\n"
            "1. Pin 1 (Kabel Merah) pada SOIC8 clip harus lurus sejajar dengan titik/titik sudut (Dot/Pin 1) pada IC EEPROM.\n"
            "2. Untuk seri 24Cxxx (I2C): Pastikan saklar jumper CH341A berada di posisi 24/25 I2C (3.3V / 5V).\n"
            "3. Untuk seri 93Cxxx (Microwire): Gunakan adapter converter 93C khusus atau sambungkan kabel jumper ke header SPI.\n"
            "4. Lepas aki/power instrumen speedometer sebelum menjepitkan SOIC8 clip untuk menghindari korsleting."
        )
        messagebox.showinfo("Panduan SOIC8 Clip", guide, parent=self.root)

    def show_about(self):
        about_text = (
            "EEPROM Programmer CH341A GUI v3.0 (Midnight Obsidian Edition)\n"
            "Didesain khusus untuk pembacaan & koreksi data dump Speedometer / Odometer Mobil & Motor.\n\n"
            "Mendukung OS: CachyOS / Arch Linux & Windows 10/11\n"
            "Fitur: Instant Odometer KM Calculator, Hex Editor, Search, Data Inspector 16-bit LE/BE."
        )
        messagebox.showinfo("Tentang Aplikasi", about_text, parent=self.root)


def main():
    root = tk.Tk()
    app = EEPROMProgrammerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
