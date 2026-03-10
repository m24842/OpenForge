from machine import Pin, ADC
from configs import *

class CoolingController:
    def __init__(self, relay_pin=COOLING_RELAY_PIN, temp_pin=COOLING_TEMP_PIN):
        self._relay_pin = Pin(relay_pin, Pin.OUT, value=0)
        assert 26 <= temp_pin <= 29, "Temp pin must be ADC-capable GPIO26-29"
        self._temp_pin = ADC(Pin(temp_pin))

    @property
    def temp(self):
        return self._temp_pin.read() * (3.3 / 4095) * 100

    def enable(self):
        self._relay_pin.value(1)

    def disable(self):
        self._relay_pin.value(0)