"""
MAX6675 K-Type Thermocouple Reader
Hardware: Adafruit Feather RP2040
Interface: SPI0

MAX6675 Wiring:
  VCC  -> 3.3V
  GND  -> GND
  SCK  -> SCK
  SO   -> MISO
  CS   -> GPIO5
"""

from machine import Pin, SPI
import time

# ── Pin Configuration ─────────────────────────────────────────
SCK_PIN  = 2   # SPI Clock
MISO_PIN = 0   # Data from MAX6675 (SO)
CS_PIN   = 5   # Chip Select (active LOW)

# ── Constants ─────────────────────────────────────────────────
MAX6675_RESOLUTION = 0.25  # °C per LSB
CONVERSION_TIME_MS = 250


class MAX6675:
    def __init__(self, sck=SCK_PIN, miso=MISO_PIN, cs=CS_PIN):
        print(f"DEBUG init: SCK={sck}, MISO={miso}, CS={cs}")

        self._spi = SPI(
            0,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
            sck=Pin(sck),
            miso=Pin(miso)
        )

        self._cs = Pin(cs, Pin.OUT, value=1)
        print("DEBUG: SPI and CS initialized")

    def _read_raw(self):
        buf = bytearray(2)

        self._cs(0)
        time.sleep_us(10)
        self._spi.readinto(buf)
        self._cs(1)

        raw = (buf[0] << 8) | buf[1]

        print(f"DEBUG raw bytes: {buf[0]:08b} {buf[1]:08b}")
        print(f"DEBUG raw int  : {raw}")
        print(f"DEBUG raw hex  : {hex(raw)}")

        return raw

    def read(self):
        raw = self._read_raw()

        # Bit 0 = fault (thermocouple disconnected)
        if raw & 0x0001:
            print("DEBUG: Open thermocouple fault detected!")
            return None

        # Extract 12-bit temperature (bits 3–14)
        temp_raw = (raw >> 3) & 0x0FFF
        temp_c = temp_raw * MAX6675_RESOLUTION

        print(f"DEBUG temp_raw : {temp_raw}")
        print(f"DEBUG temp_c   : {temp_c}")

        return temp_c

    def read_fahrenheit(self):
        temp_c = self.read()
        if temp_c is None:
            return None
        return (temp_c * 9 / 5) + 32


# ── Main Loop ─────────────────────────────────────────────────
def main():
    sensor = MAX6675()

    print("\nMAX6675 K-Type Thermocouple Reader")
    print("Press CTRL+C to stop.\n")

    while True:
        print("-" * 40)

        temp_c = sensor.read()

        if temp_c is None:
            print("ERROR: Open thermocouple — check probe!")
        else:
            temp_f = (temp_c * 9 / 5) + 32
            print(f"Temperature: {temp_c:.2f} °C | {temp_f:.2f} °F")

        time.sleep_ms(CONVERSION_TIME_MS)


if __name__ == "__main__":
    main()