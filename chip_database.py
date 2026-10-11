"""
Database Spesifikasi IC EEPROM dengan Penjelasan Seri Chip dan Label Mobil.
Mendukung Seri 24Cxxx (I2C), Seri 93Cxxx (Microwire), dan Seri 25xxx/95xxx (SPI).
"""

CHIP_DATABASE = {
    # ------------------------------------------------------------------------
    # Seri 24Cxxx (I2C Protocol)
    # ------------------------------------------------------------------------
    "24C01 [Toyota/Honda Lama]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C01",
        "protocol": "I2C",
        "size_bytes": 128,
        "page_size": 8,
        "addr_bytes": 1,
        "i2c_addr": 0xA0,
        "description": "128 Bytes EEPROM I2C",
        "common_uses": "Speedometer motor lama, Toyota/Honda lama"
    },
    "24C02 [Corolla, Soluna, Accord Lama]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C02",
        "protocol": "I2C",
        "size_bytes": 256,
        "page_size": 8,
        "addr_bytes": 1,
        "i2c_addr": 0xA0,
        "description": "256 Bytes EEPROM I2C",
        "common_uses": "Speedometer Great Corolla, Soluna, Accord Lama"
    },
    "24C04 [Honda Vario 125/150, Beat Fi, Scoopy]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C04",
        "protocol": "I2C",
        "size_bytes": 512,
        "page_size": 16,
        "addr_bytes": 1,
        "i2c_addr": 0xA0,
        "description": "512 Bytes EEPROM I2C",
        "common_uses": "Speedometer Honda Vario 125/150, Beat Fi, Scoopy Fi"
    },
    "24C08 [Yamaha NMAX, Aerox, PCX, Vario 160]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C08",
        "protocol": "I2C",
        "size_bytes": 1024,
        "page_size": 16,
        "addr_bytes": 1,
        "i2c_addr": 0xA0,
        "description": "1 KB EEPROM I2C",
        "common_uses": "Speedometer Yamaha NMAX, Aerox, PCX, Vario 160"
    },
    "24C16 [Ford Ranger, Everest, Hyundai Getz]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C16",
        "protocol": "I2C",
        "size_bytes": 2048,
        "page_size": 16,
        "addr_bytes": 1,
        "i2c_addr": 0xA0,
        "description": "2 KB EEPROM I2C",
        "common_uses": "Ford Ranger, Everest, Hyundai Getz/Accent"
    },
    "24C32 [Ford Fiesta, Ecosport, Spin]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C32",
        "protocol": "I2C",
        "size_bytes": 4096,
        "page_size": 32,
        "addr_bytes": 2,
        "i2c_addr": 0xA0,
        "description": "4 KB EEPROM I2C",
        "common_uses": "Ford Fiesta, Ecosport, Chevrolet Spin"
    },
    "24C64 [Speedometer Eropa/Jepang Modern]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C64",
        "protocol": "I2C",
        "size_bytes": 8192,
        "page_size": 32,
        "addr_bytes": 2,
        "i2c_addr": 0xA0,
        "description": "8 KB EEPROM I2C",
        "common_uses": "Speedometer Mobil Eropa & Jepang modern"
    },
    "24C128 [ECU & Instrument Cluster Modern]": {
        "family": "24Cxxx (I2C) - Honda, Motor Digital, Toyota/Ford Lama",
        "chip_code": "24C128",
        "protocol": "I2C",
        "size_bytes": 16384,
        "page_size": 64,
        "addr_bytes": 2,
        "i2c_addr": 0xA0,
        "description": "16 KB EEPROM I2C",
        "common_uses": "ECU Engine & Instrument Cluster Modern"
    },

    # ------------------------------------------------------------------------
    # Seri 93Cxxx (Microwire Protocol)
    # ------------------------------------------------------------------------
    "93C46 [Toyota Avanza Lama, Suzuki Carry]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C46 (x8)",
        "protocol": "MICROWIRE",
        "size_bytes": 128,
        "org_bits": 8,
        "page_size": 2,
        "description": "128 Bytes Microwire EEPROM (x8)",
        "common_uses": "Toyota Avanza/Xenia Gen 1, Daihatsu Taruna, Suzuki Carry"
    },
    "93C56 [Honda Jazz GD8, City Lama, Suzuki Swift]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C56 (x8)",
        "protocol": "MICROWIRE",
        "size_bytes": 256,
        "org_bits": 8,
        "page_size": 2,
        "description": "256 Bytes Microwire EEPROM (x8)",
        "common_uses": "Honda Jazz GD8, City Lama, Suzuki Swift"
    },
    "93C56 [Toyota Innova Lama, Yaris Bakpao, Vios]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C56 (x16)",
        "protocol": "MICROWIRE",
        "size_bytes": 256,
        "org_bits": 16,
        "page_size": 2,
        "description": "256 Bytes Microwire EEPROM (x16)",
        "common_uses": "Toyota Innova Lama, Yaris Bakpao, Vios Gen 1"
    },
    "93C66 [Honda Jazz GE8, Brio, Mobilio, Freed]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C66 (x8)",
        "protocol": "MICROWIRE",
        "size_bytes": 512,
        "org_bits": 8,
        "page_size": 2,
        "description": "512 Bytes Microwire EEPROM (x8)",
        "common_uses": "Honda Jazz GE8, Freed, Brio, Mobilio, CRV Gen 3"
    },
    "93C66 [Toyota Avanza Veloz, Grand New, Rush, Terios]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C66 (x16)",
        "protocol": "MICROWIRE",
        "size_bytes": 512,
        "org_bits": 16,
        "page_size": 2,
        "description": "512 Bytes Microwire EEPROM (x16)",
        "common_uses": "Toyota Avanza Veloz, Grand New Avanza, Terios/Rush"
    },
    "93C76 [Nissan Grand Livina, March, Juke, X-Trail]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C76 (x8)",
        "protocol": "MICROWIRE",
        "size_bytes": 1024,
        "org_bits": 8,
        "page_size": 2,
        "description": "1 KB Microwire EEPROM (x8)",
        "common_uses": "Nissan Grand Livina, March, Juke, X-Trail T31"
    },
    "93C76 [Mitsubishi Pajero Sport, All New, Xpander]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C76 (x16)",
        "protocol": "MICROWIRE",
        "size_bytes": 1024,
        "org_bits": 16,
        "page_size": 2,
        "description": "1 KB Microwire EEPROM (x16)",
        "common_uses": "Mitsubishi Pajero Sport, All New Pajero, Xpander"
    },
    "93C86 [Toyota Innova Reborn, Fortuner VRZ, Hilux]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C86 (x8)",
        "protocol": "MICROWIRE",
        "size_bytes": 2048,
        "org_bits": 8,
        "page_size": 2,
        "description": "2 KB Microwire EEPROM (x8)",
        "common_uses": "Toyota Innova Reborn, Fortuner VRZ, Hilux All New"
    },
    "93C86 [Honda HR-V, Civic FB, CR-V Gen 4/5, Lexus]": {
        "family": "93Cxxx (Microwire) - Mobil Jepang (Avanza, Innova, Jazz, Pajero, Livina)",
        "chip_code": "93C86 (x16)",
        "protocol": "MICROWIRE",
        "size_bytes": 2048,
        "org_bits": 16,
        "page_size": 2,
        "description": "2 KB Microwire EEPROM (x16)",
        "common_uses": "Honda HR-V, Civic FB, CR-V Gen 4/5, Lexus"
    },

    # ------------------------------------------------------------------------
    # Seri 25xxx / 95xxx (SPI Protocol)
    # ------------------------------------------------------------------------
    "25040 / 95040 [Airbag & Speedometer VW/Audi]": {
        "family": "25xxx / 95xxx (SPI) - Mobil Eropa (VW, BMW, Mercy) & Airbag/ECU",
        "chip_code": "25040",
        "protocol": "SPI",
        "size_bytes": 512,
        "page_size": 16,
        "description": "512 Bytes SPI EEPROM",
        "common_uses": "Modul Airbag & Speedometer VW/Audi"
    },
    "25080 / 95080 [Immobilizer & ECU Bosch/Delphi]": {
        "family": "25xxx / 95xxx (SPI) - Mobil Eropa (VW, BMW, Mercy) & Airbag/ECU",
        "chip_code": "25080",
        "protocol": "SPI",
        "size_bytes": 1024,
        "page_size": 32,
        "description": "1 KB SPI EEPROM",
        "common_uses": "Modul Immobilizer & ECU Bosch/Delphi"
    },
    "25160 / 95160 [Speedometer BMW, Mercedes, Peugeot]": {
        "family": "25xxx / 95xxx (SPI) - Mobil Eropa (VW, BMW, Mercy) & Airbag/ECU",
        "chip_code": "25160",
        "protocol": "SPI",
        "size_bytes": 2048,
        "page_size": 32,
        "description": "2 KB SPI EEPROM",
        "common_uses": "Speedometer BMW, Mercedes, Peugeot"
    }
}


def get_chip_list_by_family(family_name: str) -> list:
    """Mengembalikan daftar nama IC berlabel mobil berdasarkan kategori seri."""
    return [name for name, spec in CHIP_DATABASE.items() if spec["family"] == family_name]


def get_all_families() -> list:
    """Mengembalikan daftar seluruh kategori IC EEPROM."""
    families = []
    for spec in CHIP_DATABASE.values():
        if spec["family"] not in families:
            families.append(spec["family"])
    return families
