from machine import Pin
from configs import *
from canbus import SPI

class CoolingController:
    """
    Controls the cooling system activation and monitors coolant temperature.
    """
    def __init__(
        self,
        relay_pin: int = COOLING_RELAY_PIN,
        temp_spi: int = COOLING_TEMP_SPI,
        temp_sck: int = COOLING_TEMP_SCK,
        temp_miso: int = COOLING_TEMP_MISO,
        temp_cs: int = COOLING_TEMP_CS,
    ) -> None:
        self._temp_spi = SPI(
            idx=temp_spi,
            sck=Pin(temp_sck),
            mosi=None,
            miso=Pin(temp_miso),
            cs=Pin(temp_cs),
            # baudrate=1000000,
        )
        self._relay_pin = Pin(relay_pin, Pin.OUT, value=0)

    @property
    def temp(self) -> float:
        self._temp_spi.start()
        raw = self._temp_spi.transfer(read=True)
        self._temp_spi.end()
        if raw & 0x4: return 0
        return (raw >> 3) * 0.25

    def enable(self) -> None:
        self._relay_pin.value(1)

    def disable(self) -> None:
        self._relay_pin.value(0)
