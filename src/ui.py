from machine import Pin, Timer
from configs import *

class UI:
    
    IDLE = const(0)
    RAMP = const(1)
    STEADY = const(2)
    ERROR = const(3)
    
    def __init__(
        self,
        green_led_pin=GREEN_LED_PIN,
        red_led_pin=RED_LED_PIN,
    ):
        self.status = self.IDLE
        
        self._green_led = Pin(green_led_pin, Pin.OUT, value=0)
        self._red_led = Pin(red_led_pin, Pin.OUT, value=0)
        self._flash_timer = Timer(0)
        self._flash_timer.init(period=100, mode=Timer.PERIODIC, callback=self._flash_handler)
        self._flash_counter = 0
    
    def _flash_handler(self, timer):
        if self.status == self.STEADY:
            match self._flash_counter:
                case 0: self._green_led.on()
                case 1: self._green_led.off()
            self._flash_counter = (self._flash_counter + 1) % 3
    
    def set_status(self, status):
        self.status = status
        match status:
            case self.IDLE:
                self._green_led.off()
                self._red_led.off()
            case self.RAMP:
                self._green_led.on()
                self._red_led.off()
            case self.STEADY:
                self._red_led.off()
            case self.ERROR:
                self._green_led.off()
                self._red_led.on()
    