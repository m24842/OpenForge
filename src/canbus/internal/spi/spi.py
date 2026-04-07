try:
    from typing import Optional, overload
except ImportError:
    pass

import sys
import time
from machine import Pin, SPI as MICROPYTHON_SPI

from . import (
    SPI_DEFAULT_BAUDRATE,
    SPI_DUMMY_INT,
    SPI_TRANSFER_LEN,
    SPI_HOLD_US,
)

class SPI:
    def __init__(self, idx: int, sck: Pin, mosi: Optional[Pin], miso: Optional[Pin], cs: Pin, baudrate: int = SPI_DEFAULT_BAUDRATE) -> None:
        self._SPICS = Pin(cs, Pin.OUT)
        self._SPI = MICROPYTHON_SPI(
            idx,
            sck=sck,
            mosi=mosi,
            miso=miso,
            baudrate=baudrate
        )
        self.end()

    def start(self) -> None:
        self._SPICS.value(0)
        time.sleep_us(SPI_HOLD_US)

    def end(self) -> None:
        self._SPICS.value(1)
        time.sleep_us(SPI_HOLD_US)

    def transfer(self, value: int = SPI_DUMMY_INT, transfer_len: int = SPI_TRANSFER_LEN, read: bool = False, as_bytes: bool = False) -> int | bytearray:
        """Write int value to SPI and read SPI as int value simultaneously.
        This method supports transfer single byte only,
        and the system byte order doesn't matter because of that. The input and
        output int value are unsigned.
        """
        value_as_byte = value.to_bytes(transfer_len, sys.byteorder)

        if read:
            output = bytearray(transfer_len)
            self._SPI.write_readinto(value_as_byte, output)
            if as_bytes: return output
            return int.from_bytes(output, sys.byteorder)
        self._SPI.write(value_as_byte)
        return value
