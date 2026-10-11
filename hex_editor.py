"""
Widget Hex Editor Kustom - Midnight Cyan & Obsidian Slate Theme
Menampilkan data biner EEPROM dalam format Hexadecimal + ASCII View + Data Inspector & Search.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class HexEditorWidget(ttk.Frame):
    """
    Widget Hex Editor interaktif profesional dengan tema Midnight Slate & Cyan Accent.
    """

    BYTES_PER_LINE = 16

    # Palet Warna Ultra-Premium Slate Obsidian
    COLOR_BG = "#0F172A"         # Slate 900
    COLOR_CARD = "#1E293B"       # Slate 800
    COLOR_FG = "#E2E8F0"         # Slate 200
    COLOR_HEADER = "#38BDF8"     # Sky Cyan
    COLOR_OFFSET = "#818CF8"     # Indigo Accent
    COLOR_HEX_EVEN = "#F8FAFC"   # White Slate
    COLOR_HEX_ODD = "#94A3B8"    # Slate Gray
    COLOR_ASCII = "#34D399"      # Emerald Mint
    COLOR_MODIFIED = "#EF4444"   # Vibrant Flame Red
    COLOR_SELECT = "#334155"     # Highlight Slate

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data_buffer = bytearray(256)
        self.modified_indices = set()
        self.current_selected_index = 0

        self._build_ui()
        self.render_hex_table()

    def _build_ui(self):
        """Membuat struktur UI Hex Editor modern."""
        # Frame Kontrol Atas (Search & Jump Offset)
        ctrl_bar = tk.Frame(self, bg=self.COLOR_CARD, padx=10, pady=8)
        ctrl_bar.pack(fill=tk.X)

        # Quick Search Box
        tk.Label(ctrl_bar, text="🔍 Cari Data (Hex / Text):", bg=self.COLOR_CARD, fg="#94A3B8", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        
        self.entry_search = tk.Entry(ctrl_bar, font=("Consolas", 10), bg="#0F172A", fg="#38BDF8", insertbackground="#FFFFFF", width=18, relief=tk.FLAT, bd=4)
        self.entry_search.pack(side=tk.LEFT, padx=2)
        self.entry_search.bind("<Return>", lambda e: self.search_data())

        btn_search = tk.Button(
            ctrl_bar, text="Cari", bg="#0284C7", fg="#FFFFFF", font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT, activebackground="#0EA5E9", command=self.search_data, padx=10, cursor="hand2"
        )
        btn_search.pack(side=tk.LEFT, padx=6)

        # Jump Offset Box
        tk.Label(ctrl_bar, text="📍 Lompat Ke Offset (Hex):", bg=self.COLOR_CARD, fg="#94A3B8", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(20, 6))
        
        self.entry_jump = tk.Entry(ctrl_bar, font=("Consolas", 10), bg="#0F172A", fg="#38BDF8", insertbackground="#FFFFFF", width=8, relief=tk.FLAT, bd=4)
        self.entry_jump.pack(side=tk.LEFT, padx=2)
        self.entry_jump.bind("<Return>", lambda e: self.jump_to_offset())

        btn_jump = tk.Button(
            ctrl_bar, text="Lompat", bg="#475569", fg="#FFFFFF", font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT, activebackground="#64748B", command=self.jump_to_offset, padx=10, cursor="hand2"
        )
        btn_jump.pack(side=tk.LEFT, padx=6)

        # Info Ringkasan Ukuran
        self.lbl_size = tk.Label(ctrl_bar, text="Ukuran: 256 B (0x0100)", bg=self.COLOR_CARD, fg=self.COLOR_HEADER, font=("Consolas", 9, "bold"))
        self.lbl_size.pack(side=tk.RIGHT, padx=5)

        # Main Text Editor Container
        editor_frame = tk.Frame(self, bg=self.COLOR_BG)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.text_editor = tk.Text(
            editor_frame,
            font=("Consolas", 10),
            wrap=tk.NONE,
            bg=self.COLOR_BG,
            fg=self.COLOR_FG,
            insertbackground="#FFFFFF",
            selectbackground=self.COLOR_SELECT,
            padx=14,
            pady=10,
            relief=tk.FLAT
        )

        v_scroll = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Styling Tag Syntax Highlighting
        self.text_editor.tag_configure("header", foreground=self.COLOR_HEADER, font=("Consolas", 10, "bold"))
        self.text_editor.tag_configure("offset", foreground=self.COLOR_OFFSET)
        self.text_editor.tag_configure("hex_even", foreground=self.COLOR_HEX_EVEN)
        self.text_editor.tag_configure("hex_odd", foreground=self.COLOR_HEX_ODD)
        self.text_editor.tag_configure("ascii", foreground=self.COLOR_ASCII)
        self.text_editor.tag_configure("modified", foreground="#FFFFFF", background=self.COLOR_MODIFIED, font=("Consolas", 10, "bold"))
        self.text_editor.tag_configure("search_match", foreground="#0F172A", background="#F59E0B", font=("Consolas", 10, "bold"))

        # Frame Bawah: Data Inspector (Kalkulator KM Word)
        inspector_bar = tk.Frame(self, bg=self.COLOR_CARD, padx=12, pady=6)
        inspector_bar.pack(fill=tk.X)

        self.lbl_inspect_offset = tk.Label(inspector_bar, text="Offset: 0x0000", bg=self.COLOR_CARD, fg=self.COLOR_HEADER, font=("Consolas", 9, "bold"))
        self.lbl_inspect_offset.pack(side=tk.LEFT, padx=(0, 15))

        self.lbl_inspect_hex = tk.Label(inspector_bar, text="8-bit: 0x00 (0)", bg=self.COLOR_CARD, fg=self.COLOR_FG, font=("Consolas", 9))
        self.lbl_inspect_hex.pack(side=tk.LEFT, padx=12)

        self.lbl_inspect_word_le = tk.Label(inspector_bar, text="16-bit LE: 0x0000 (0 KM)", bg=self.COLOR_CARD, fg="#F59E0B", font=("Consolas", 9, "bold"))
        self.lbl_inspect_word_le.pack(side=tk.LEFT, padx=12)

        self.lbl_inspect_word_be = tk.Label(inspector_bar, text="16-bit BE: 0x0000 (0 KM)", bg=self.COLOR_CARD, fg="#A855F7", font=("Consolas", 9, "bold"))
        self.lbl_inspect_word_be.pack(side=tk.LEFT, padx=12)

        # Event Binding
        self.text_editor.bind("<ButtonRelease-1>", self._on_cursor_click)
        self.text_editor.bind("<Double-Button-1>", self._on_double_click_edit)
        self.text_editor.bind("<Key>", lambda e: "break" if (e.state != 4 or e.keysym not in ('c', 'C')) else None)

    def set_data(self, new_data: bytes or bytearray):
        """Memuat buffer data biner baru ke Hex Editor."""
        self.data_buffer = bytearray(new_data)
        self.modified_indices.clear()
        self.current_selected_index = 0
        self.lbl_size.config(text=f"Ukuran: {len(self.data_buffer)} B (0x{len(self.data_buffer):04X})")
        self.render_hex_table()
        self.update_inspector(0)

    def get_data(self) -> bytearray:
        """Mengambil buffer data biner dari Hex Editor."""
        return bytearray(self.data_buffer)

    def render_hex_table(self):
        """Merender seluruh isi buffer biner menjadi tampilan Hex Editor."""
        self.text_editor.config(state=tk.NORMAL)
        self.text_editor.delete("1.0", tk.END)

        header_str = "OFFSET    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  | ASCII Dump\n"
        header_str += "─" * 75 + "\n"
        self.text_editor.insert(tk.END, header_str, "header")

        total_bytes = len(self.data_buffer)

        for row_addr in range(0, total_bytes, self.BYTES_PER_LINE):
            offset_str = f"{row_addr:08X}: "
            self.text_editor.insert(tk.END, offset_str, "offset")

            line_bytes = self.data_buffer[row_addr : row_addr + self.BYTES_PER_LINE]
            for i in range(self.BYTES_PER_LINE):
                byte_index = row_addr + i
                if i == 8:
                    self.text_editor.insert(tk.END, " ")

                if byte_index < total_bytes:
                    b_val = line_bytes[i]
                    hex_str = f"{b_val:02X} "

                    tag = "modified" if byte_index in self.modified_indices else ("hex_even" if (i // 4) % 2 == 0 else "hex_odd")
                    self.text_editor.insert(tk.END, hex_str, tag)
                else:
                    self.text_editor.insert(tk.END, "   ")

            self.text_editor.insert(tk.END, " | ")
            ascii_str = ""
            for i in range(len(line_bytes)):
                b = line_bytes[i]
                ascii_str += chr(b) if 32 <= b <= 126 else "."

            self.text_editor.insert(tk.END, f"{ascii_str:<16}\n", "ascii")

        self.text_editor.config(state=tk.DISABLED)

    def update_inspector(self, index: int):
        """Memperbarui informasi Data Inspector."""
        if 0 <= index < len(self.data_buffer):
            self.current_selected_index = index
            b8 = self.data_buffer[index]
            
            if index + 1 < len(self.data_buffer):
                b8_next = self.data_buffer[index + 1]
                val_le = (b8_next << 8) | b8
                val_be = (b8 << 8) | b8_next
            else:
                val_le = b8
                val_be = b8

            self.lbl_inspect_offset.config(text=f"Offset: 0x{index:04X} ({index})")
            self.lbl_inspect_hex.config(text=f"8-bit: 0x{b8:02X} ({b8})")
            self.lbl_inspect_word_le.config(text=f"16-bit LE: 0x{val_le:04X} ({val_le} KM)")
            self.lbl_inspect_word_be.config(text=f"16-bit BE: 0x{val_be:04X} ({val_be} KM)")

    def _on_cursor_click(self, event):
        try:
            cursor_pos = self.text_editor.index(tk.CURRENT)
            line, col = map(int, cursor_pos.split('.'))

            if line < 3:
                return

            row_offset = (line - 3) * self.BYTES_PER_LINE
            if 10 <= col <= 57:
                col_hex = col - 10
                if col_hex > 24:
                    col_hex -= 1
                byte_idx_in_row = col_hex // 3
                target_index = row_offset + byte_idx_in_row
                
                self.update_inspector(target_index)
        except Exception:
            pass

    def _on_double_click_edit(self, event):
        try:
            cursor_pos = self.text_editor.index(tk.CURRENT)
            line, col = map(int, cursor_pos.split('.'))

            if line < 3:
                return

            row_offset = (line - 3) * self.BYTES_PER_LINE
            if 10 <= col <= 57:
                col_hex = col - 10
                if col_hex > 24:
                    col_hex -= 1
                byte_idx_in_row = col_hex // 3
                target_index = row_offset + byte_idx_in_row

                if target_index < len(self.data_buffer):
                    current_val = self.data_buffer[target_index]
                    self.prompt_edit_byte(target_index, current_val)
        except Exception:
            pass

    def prompt_edit_byte(self, index: int, current_val: int):
        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Byte - Offset 0x{index:04X}")
        dialog.geometry("300x140")
        dialog.configure(bg="#0F172A")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text=f"Ubah Nilai Hex di Offset 0x{index:04X}:", bg="#0F172A", fg=self.COLOR_FG, font=("Segoe UI", 10)).pack(pady=10)

        entry = tk.Entry(dialog, font=("Consolas", 12, "bold"), justify="center", bg="#1E293B", fg="#34D399", insertbackground="#FFFFFF")
        entry.insert(0, f"{current_val:02X}")
        entry.select_range(0, tk.END)
        entry.pack(pady=5)
        entry.focus()

        def apply_edit():
            hex_str = entry.get().strip()
            try:
                val = int(hex_str, 16)
                if 0 <= val <= 255:
                    self.data_buffer[index] = val
                    self.modified_indices.add(index)
                    self.render_hex_table()
                    self.update_inspector(index)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Nilai harus antara 00 dan FF (0 - 255)", parent=dialog)
            except ValueError:
                messagebox.showerror("Error", "Format Hex tidak valid!", parent=dialog)

        tk.Button(dialog, text="Simpan Perubahan", bg="#0284C7", fg="#FFFFFF", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, command=apply_edit, padx=15).pack(pady=8)
        entry.bind("<Return>", lambda e: apply_edit())

    def jump_to_offset(self):
        offset_hex = self.entry_jump.get().strip()
        try:
            target = int(offset_hex, 16)
            if 0 <= target < len(self.data_buffer):
                line_idx = (target // self.BYTES_PER_LINE) + 3
                self.text_editor.see(f"{line_idx}.0")
                self.update_inspector(target)
            else:
                messagebox.showwarning("Perhatian", f"Offset di luar jangkauan (0x0000 - 0x{len(self.data_buffer)-1:04X})", parent=self)
        except ValueError:
            messagebox.showerror("Error", "Masukkan alamat offset Hexadecimal yang valid!", parent=self)

    def search_data(self):
        query = self.entry_search.get().strip()
        if not query:
            return

        target_bytes = None
        try:
            clean_hex = query.replace(" ", "")
            if len(clean_hex) % 2 == 0:
                target_bytes = bytes.fromhex(clean_hex)
        except ValueError:
            target_bytes = None

        if target_bytes is None:
            target_bytes = query.encode("utf-8")

        found_idx = self.data_buffer.find(target_bytes)
        if found_idx != -1:
            line_idx = (found_idx // self.BYTES_PER_LINE) + 3
            self.text_editor.see(f"{line_idx}.0")
            self.update_inspector(found_idx)
            messagebox.showinfo("Ditemukan", f"Pola data ditemukan di Offset: 0x{found_idx:04X}", parent=self)
        else:
            messagebox.showinfo("Tidak Ditemukan", f"Pola '{query}' tidak ditemukan.", parent=self)
