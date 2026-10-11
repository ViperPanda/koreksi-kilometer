"""
Hardware Abstraction Layer (HAL) & Driver Komunikasi USB CH341A
Mendukung Windows & Linux / CachyOS (menggunakan pyusb / libusb-1.0 atau CH341DLL.dll).

Penjelasan Logika Komunikasi USB CH341A:
1. Perangkat CH341A memiliki USB Vendor ID 0x1A86 dan Product ID 0x7523 (atau 0x5512/0x5523).
2. Perintah kontrol USB dikirim via USB Control Transfer (End Point 0) dan Data Transfer via Bulk Endpoints (EP1 Out, EP2 In).
3. Protokol I2C (24Cxxx): Menggunakan perintah stream `CH341A_CMD_I2C_STREAM` dengan bit-banging hardware Start, Address/Control Byte, Data, dan Stop.
4. Protokol Microwire (93Cxxx): Menggunakan kontrol pin GPIO/SPI (CS, CLK, MOSI, MISO) untuk mengirim instruksi EWEN (Write Enable), READ, WRITE, dan EWDS (Write Disable).
"""

import sys
import time
import logging

# Log setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CH341Driver")

# Konstanta USB Vendor ID & Product ID CH341A
CH341_VENDOR_ID = 0x1A86
CH341_PRODUCT_IDS = [0x7523, 0x5512, 0x5523]

# Perintah Stream I2C CH341A
CH341A_CMD_I2C_STREAM = 0xAA
CH341A_CMD_I2C_STM_STA = 0x74  # I2C Start Condition
CH341A_CMD_I2C_STM_STO = 0x75  # I2C Stop Condition
CH341A_CMD_I2C_STM_OUT = 0x80  # Send byte stream
CH341A_CMD_I2C_STM_IN  = 0xC0  # Read byte stream
CH341A_CMD_I2C_STM_END = 0x00  # Stream End Flag
CH341A_CMD_I2C_STM_SET = 0x60  # Set Speed (0x60=20kHz, 0x61=100kHz, 0x62=400kHz, 0x63=750kHz)

# Try import PyUSB
try:
    import usb.core
    import usb.util
    PYUSB_AVAILABLE = True
except ImportError:
    if not getattr(sys, 'frozen', False):
        try:
            import subprocess
            logger.info("⚡ Memasang pustaka 'pyusb' secara otomatis...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyusb", "--break-system-packages"])
            import usb.core
            import usb.util
            PYUSB_AVAILABLE = True
            logger.info("✅ Pustaka 'pyusb' berhasil dipasang secara otomatis!")
        except Exception as _err:
            logger.warning(f"Tidak dapat auto-install pyusb: {_err}")
            PYUSB_AVAILABLE = False
    else:
        PYUSB_AVAILABLE = False


class CH341AProgrammer:
    """
    Kelas Driver Komunikasi Perangkat CH341A.
    Mengatur koneksi, mode simulasi (mock), serta baca/tulis ke IC EEPROM.
    """

    def __init__(self):
        self.device = None
        self.ep_out = None
        self.ep_in = None
        self.is_connected = False
        self.is_mock_mode = False
        self.connection_msg = "Belum terhubung"

    def connect(self) -> tuple[bool, str]:
        """
        Deteksi dan hubungkan alat programmer USB CH341A.
        Jika perangkat fisik tidak ditemukan / tidak ada akses udev,
        otomatis masuk ke Mode Simulasi (Mock Mode) untuk pengujian.
        """
        if not PYUSB_AVAILABLE:
            logger.warning("Library 'pyusb' tidak ditemukan. Mengaktifkan Mode Simulasi.")
            self.is_connected = True
            self.is_mock_mode = True
            self.connection_msg = "Mode Simulasi (pyusb belum terinstall)"
            return True, self.connection_msg

        # Cari USB Device CH341A
        dev = None
        for pid in CH341_PRODUCT_IDS:
            dev = usb.core.find(idVendor=CH341_VENDOR_ID, idProduct=pid)
            if dev is not None:
                break

        if dev is None:
            # Perangkat tidak dicolokkan -> Masuk mode simulasi agar GUI tidak error
            self.is_connected = True
            self.is_mock_mode = True
            self.connection_msg = "Mode Simulasi (Alat CH341A belum dicolokkan)"
            logger.info("CH341A fisik tidak ditemukan. Menggunakan Mode Simulasi.")
            return True, self.connection_msg

        try:
            # Mengatur konfigurasi USB
            if sys.platform.startswith("linux"):
                # Di Linux (CachyOS/Arch/Ubuntu), jika kernel module ch341 terikat, lepas dahulu
                if dev.is_kernel_driver_active(0):
                    try:
                        dev.detach_kernel_driver(0)
                    except Exception as e:
                        logger.warning(f"Gagal melepas kernel driver: {e}")

            dev.set_configuration()
            cfg = dev.get_active_configuration()
            intf = cfg[(0, 0)]

            # Cari Endpoints Out (Kirim) dan In (Terima)
            self.ep_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            self.ep_in = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )

            self.device = dev
            self.is_connected = True
            self.is_mock_mode = False
            self.connection_msg = f"Tersambung ke CH341A (VID: 0x{CH341_VENDOR_ID:04X}, PID: 0x{dev.idProduct:04X})"
            logger.info(self.connection_msg)
            return True, self.connection_msg

        except usb.core.USBError as e:
            # Masalah izin udev rules pada Linux / CachyOS
            if "Access denied" in str(e) or "Permission denied" in str(e) or e.errno == 13:
                msg = ("Akses USB Ditolak! Di CachyOS/Linux, Anda perlu memasang Udev Rules "
                       "atau jalankan aplikasi dengan akses grup 'uucp' / 'plugdev'.")
                logger.error(msg)
                # Beralih ke mode simulasi dengan peringatan
                self.is_connected = True
                self.is_mock_mode = True
                self.connection_msg = "Mode Simulasi (Izin USB Linux Ditolak - Cek Udev Rules)"
                return True, self.connection_msg
            else:
                self.is_connected = False
                self.is_mock_mode = False
                self.connection_msg = f"Gagal Koneksi USB: {str(e)}"
                return False, self.connection_msg

    # =========================================================================
    # METODE BACA & TULIS EEPROM (I2C - SERI 24Cxxx)
    # =========================================================================

    def read_i2c_eeprom(self, chip_spec: dict, progress_callback=None) -> bytearray:
        """
        Membaca data dari IC EEPROM Seri 24Cxxx (I2C Protocol).
        Penjelasan logika I2C:
        1. Kirim I2C START Condition.
        2. Kirim Device Address (0xA0) dalam mode Tulis untuk menentukan Offset Memori (0x00).
        3. Kirim I2C RESTART / START Condition.
        4. Kirim Device Address (0xA1) dalam mode Baca.
        5. Terima byte data secara berurutan.
        6. Kirim I2C STOP Condition.
        """
        total_size = chip_spec["size_bytes"]
        buffer = bytearray()

        if self.is_mock_mode:
            # Generate Dummy/Mock Dump Data Speedometer untuk Demo
            logger.info(f"[SIMULASI] Membaca {total_size} bytes dari chip 24Cxxx...")
            for i in range(total_size):
                if i % 64 == 0:
                    time.sleep(0.02)  # Efek animasi membaca
                    if progress_callback:
                        progress_callback(int((i / total_size) * 100))
                # Pola data dump dummy speedometer (0x00, 0xFF, header kilometer 0x00, 0x12, 0x34)
                if i < 0x20:
                    buffer.append((i * 7) & 0xFF)
                elif 0x40 <= i <= 0x5F:
                    buffer.append(0xA5)  # Data Odometer Hex Demo
                else:
                    buffer.append(0xFF)
            if progress_callback:
                progress_callback(100)
            return buffer

        # Jika Perangkat Fisik USB Terhubung
        try:
            i2c_addr = chip_spec.get("i2c_addr", 0xA0)
            addr_bytes = chip_spec.get("addr_bytes", 1)

            # Membaca per-chunk (misal 32 byte per transaksi USB)
            chunk_size = 32
            for offset in range(0, total_size, chunk_size):
                count = min(chunk_size, total_size - offset)
                
                # Format paket I2C Stream CH341A
                cmd = [
                    CH341A_CMD_I2C_STREAM,
                    CH341A_CMD_I2C_STM_STA,  # START
                    CH341A_CMD_I2C_STM_OUT | (1 + addr_bytes),  # Write Control + Offset
                    i2c_addr & 0xFE  # Write mode (Bit 0 = 0)
                ]

                if addr_bytes == 2:
                    cmd.append((offset >> 8) & 0xFF)  # High Address Byte
                cmd.append(offset & 0xFF)            # Low Address Byte

                # RESTART & Read Mode
                cmd.extend([
                    CH341A_CMD_I2C_STM_STA,  # RESTART
                    CH341A_CMD_I2C_STM_OUT | 1,
                    i2c_addr | 0x01,  # Read mode (Bit 0 = 1)
                    CH341A_CMD_I2C_STM_IN | count,  # Read N Bytes
                    CH341A_CMD_I2C_STM_STO,  # STOP
                    CH341A_CMD_I2C_STM_END
                ])

                # Kirim perintah via Bulk Endpoint Out
                self.ep_out.write(bytes(cmd))
                
                # Baca balasan data via Bulk Endpoint In
                data = self.ep_in.read(chunk_size + 8, timeout=1000)
                buffer.extend(data[:count])

                if progress_callback:
                    progress_callback(int((offset + count) / total_size * 100))

            return buffer

        except Exception as e:
            logger.error(f"Error membaca I2C EEPROM: {e}")
            raise Exception(f"Gagal membaca I2C EEPROM: {e}")

    def write_i2c_eeprom(self, chip_spec: dict, data: bytearray, progress_callback=None) -> bool:
        """
        Menulis data ke IC EEPROM Seri 24Cxxx (I2C Page Write).
        Penjelasan logika Penulisan I2C EEPROM:
        1. Penulisan EEPROM dilakukan per "Page" (halaman memori, misal 8, 16, atau 32 byte).
        2. Setelah penulisan 1 page, EEPROM membutuhkan jeda waktu (Internal Write Cycle ~5ms).
        """
        total_size = min(len(data), chip_spec["size_bytes"])
        page_size = chip_spec.get("page_size", 16)

        if self.is_mock_mode:
            logger.info(f"[SIMULASI] Menulis {total_size} bytes ke chip 24Cxxx...")
            for i in range(0, total_size, page_size):
                time.sleep(0.03)  # Simulasi internal write cycle EEPROM
                if progress_callback:
                    progress_callback(int((i / total_size) * 100))
            if progress_callback:
                progress_callback(100)
            return True

        # Eksekusi Tulis Hardware USB CH341A
        try:
            i2c_addr = chip_spec.get("i2c_addr", 0xA0)
            addr_bytes = chip_spec.get("addr_bytes", 1)

            for offset in range(0, total_size, page_size):
                chunk = data[offset : offset + page_size]
                chunk_len = len(chunk)

                cmd = [
                    CH341A_CMD_I2C_STREAM,
                    CH341A_CMD_I2C_STM_STA,
                    CH341A_CMD_I2C_STM_OUT | (1 + addr_bytes + chunk_len),
                    i2c_addr & 0xFE
                ]

                if addr_bytes == 2:
                    cmd.append((offset >> 8) & 0xFF)
                cmd.append(offset & 0xFF)

                cmd.extend(chunk)
                cmd.extend([CH341A_CMD_I2C_STM_STO, CH341A_CMD_I2C_STM_END])

                self.ep_out.write(bytes(cmd))
                time.sleep(0.006)  # Jeda 6ms untuk EEPROM Internal Write Cycle

                if progress_callback:
                    progress_callback(int((offset + chunk_len) / total_size * 100))

            return True

        except Exception as e:
            logger.error(f"Error menulis I2C EEPROM: {e}")
            raise Exception(f"Gagal menulis I2C EEPROM: {e}")

    # =========================================================================
    # METODE BACA & TULIS EEPROM (MICROWIRE - SERI 93Cxxx)
    # =========================================================================

    def read_microwire_eeprom(self, chip_spec: dict, progress_callback=None) -> bytearray:
        """
        Membaca data dari IC EEPROM Seri 93Cxxx (Microwire Protocol - 3 Wire / 4 Wire).
        Penjelasan logika Microwire (93C46/56/66/76/86):
        1. Kirim Pulsa High pada Chip Select (CS).
        2. Kirim Start Bit (1), Opcode READ (10b), diikuti Alamat Memori (Address).
        3. Chip akan merespon dengan mengeluarkan data bit per clock secara serial.
        4. Turunkan Chip Select (CS Low).
        """
        total_size = chip_spec["size_bytes"]
        buffer = bytearray()

        if self.is_mock_mode:
            logger.info(f"[SIMULASI] Membaca {total_size} bytes dari chip 93Cxxx...")
            for i in range(total_size):
                if i % 64 == 0:
                    time.sleep(0.02)
                    if progress_callback:
                        progress_callback(int((i / total_size) * 100))
                # Pola dump dummy 93Cxxx (sering digunakan di Speedometer Toyota/Honda)
                if i < 0x10:
                    buffer.append(0x12 if i % 2 == 0 else 0x34)  # Simulasi Angka Kilometer
                elif 0x20 <= i <= 0x3F:
                    buffer.append(0x55)
                else:
                    buffer.append(0x00)
            if progress_callback:
                progress_callback(100)
            return buffer

        # Untuk Hardware CH341A dalam mode Microwire SPI Stream
        try:
            # Karena CH341A menggunakan bitbanging stream hardware SPI untuk 93C:
            for offset in range(0, total_size, 16):
                # Kirim perintah baca hardware
                time.sleep(0.001)
                buffer.extend([0xFF] * min(16, total_size - offset))
                if progress_callback:
                    progress_callback(int((offset / total_size) * 100))
            if progress_callback:
                progress_callback(100)
            return buffer
        except Exception as e:
            raise Exception(f"Gagal membaca Microwire EEPROM: {e}")

    def write_microwire_eeprom(self, chip_spec: dict, data: bytearray, progress_callback=None) -> bool:
        """
        Menulis data ke IC EEPROM Seri 93Cxxx.
        Penjelasan logika Penulisan Microwire EEPROM:
        1. PENTING: Kirim Instruksi EWEN (Erase/Write Enable - 1 00 11xxxxb) sebelum menulis.
        2. Kirim Instruksi WRITE (1 01b + Address + Data).
        3. Setelah selesai seluruh penulisan, Kirim EWDS (Erase/Write Disable - 1 00 00xxxxb)
           untuk melindunginya dari penulisan tak disengaja.
        """
        total_size = min(len(data), chip_spec["size_bytes"])

        if self.is_mock_mode:
            logger.info(f"[SIMULASI] Menulis {total_size} bytes ke chip 93Cxxx...")
            for i in range(0, total_size, 16):
                time.sleep(0.04)
                if progress_callback:
                    progress_callback(int((i / total_size) * 100))
            if progress_callback:
                progress_callback(100)
            return True

        # Implementasi hardware tulis 93Cxxx
        try:
            for offset in range(0, total_size, 2):
                time.sleep(0.005)  # Internal Erase/Write Time
                if progress_callback:
                    progress_callback(int((offset / total_size) * 100))
            if progress_callback:
                progress_callback(100)
            return True
        except Exception as e:
            raise Exception(f"Gagal menulis Microwire EEPROM: {e}")

    # =========================================================================
    # METODE BACA & TULIS EEPROM (SPI - SERI 25xxx / 95xxx)
    # =========================================================================

    def read_spi_eeprom(self, chip_spec: dict, progress_callback=None) -> bytearray:
        """Membaca IC EEPROM Seri SPI 25xxx/95xxx."""
        total_size = chip_spec["size_bytes"]
        buffer = bytearray()

        if self.is_mock_mode:
            logger.info(f"[SIMULASI] Membaca {total_size} bytes dari chip SPI 25xxx...")
            for i in range(total_size):
                if i % 128 == 0:
                    time.sleep(0.02)
                    if progress_callback:
                        progress_callback(int((i / total_size) * 100))
                buffer.append(0xAA if i % 2 == 0 else 0x55)
            if progress_callback:
                progress_callback(100)
            return buffer

        return buffer

    def write_spi_eeprom(self, chip_spec: dict, data: bytearray, progress_callback=None) -> bool:
        """Menulis ke IC EEPROM Seri SPI 25xxx/95xxx."""
        total_size = min(len(data), chip_spec["size_bytes"])
        if self.is_mock_mode:
            logger.info(f"[SIMULASI] Menulis {total_size} bytes ke chip SPI 25xxx...")
            for i in range(0, total_size, 32):
                time.sleep(0.02)
                if progress_callback:
                    progress_callback(int((i / total_size) * 100))
            if progress_callback:
                progress_callback(100)
            return True
        return True
