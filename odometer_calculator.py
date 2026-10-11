"""
Modul Kalkulator & Algoritma Koreksi Kilometer Speedometer
Mengonversi nilai Kilometer (KM) target ke dalam pasangan byte Hexadecimal EEPROM.
Dukungan Preset: Toyota, Daihatsu, Honda, Mitsubishi, Suzuki, Nissan, & Motor Digital.
"""


class OdometerCalculator:
    """
    Kalkulator Algoritma Koreksi Odometer Kilometer & Pendeteksi Otomatis Offset.
    """

    @staticmethod
    def auto_detect_km_offset(buffer: bytearray) -> tuple[int, int]:
        """
        Memindai buffer biner untuk mendeteksi lokasi offset awal data kilometer
        dan mengestimasi nilai kilometer saat ini.
        Mengembalikan (found_offset, estimated_km).
        """
        if not buffer or len(buffer) < 16:
            return 0, 0

        # Pindai offset yang paling umum (0x0000, 0x0010, 0x0020, 0x0040)
        common_offsets = [0x0000, 0x0020, 0x0010, 0x0040]
        
        for offset in common_offsets:
            if offset + 4 <= len(buffer):
                b0 = buffer[offset]
                b1 = buffer[offset + 1]
                b2 = buffer[offset + 2]
                b3 = buffer[offset + 3]

                # Cek pola Denso Inverted Complement (b0^b2 == 0xFF && b1^b3 == 0xFF)
                if (b0 ^ b2) == 0xFF and (b1 ^ b3) == 0xFF:
                    val = (b1 << 8) | b0
                    estimated_km = val * 16
                    return offset, estimated_km

                # Cek pola Direct Word (b0 == b2 && b1 == b3)
                if b0 == b2 and b1 == b3 and (b0 != 0xFF or b1 != 0xFF):
                    val = (b1 << 8) | b0
                    estimated_km = val * 10
                    return offset, estimated_km

        return 0, 0

    @staticmethod
    def calculate_hex_bytes(target_km: int, preset_type: str) -> tuple[bytearray, int]:
        """
        Mengonversi nilai Kilometer target ke dalam array byte Hex.
        Mengembalikan (bytearray_data, default_start_offset).
        """

        if "Denso 16-bit (Toyota/Daihatsu/Honda)" in preset_type:
            val = (target_km // 16) & 0xFFFF
            inv_val = val ^ 0xFFFF
            
            b0 = val & 0xFF
            b1 = (val >> 8) & 0xFF
            ib0 = inv_val & 0xFF
            ib1 = (inv_val >> 8) & 0xFF
            
            pattern = bytearray([b0, b1, ib0, ib1] * 8)  # 32 byte block
            default_offset = 0x0000
            return pattern, default_offset

        elif "Nissan / Mitsubishi 16-bit" in preset_type:
            val = (target_km // 10) & 0xFFFF
            inv_val = val ^ 0xFFFF
            b0 = (val >> 8) & 0xFF
            b1 = val & 0xFF
            pattern = bytearray([b0, b1] * 16)
            default_offset = 0x0020
            return pattern, default_offset

        elif "Honda Vario / NMAX Motor" in preset_type:
            val = (target_km // 10) & 0xFFFF
            b0 = val & 0xFF
            b1 = (val >> 8) & 0xFF
            pattern = bytearray([b0, b1] * 8)
            default_offset = 0x0010
            return pattern, default_offset

        else:
            val = target_km & 0xFFFF
            b0 = val & 0xFF
            b1 = (val >> 8) & 0xFF
            pattern = bytearray([b0, b1] * 8)
            default_offset = 0x0000
            return pattern, default_offset
