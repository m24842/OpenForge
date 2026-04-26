from machine import Pin, ADC, Timer
from configs import *

class UI:
    """
    Captures user inputs and provides visual feedback on system status.
    """
    
    IDLE = const(0)
    RAMP = const(1)
    STEADY = const(2)
    OVERLOAD = const(3)
    ERROR = const(4)
    
    def __init__(
        self,
        green_led_pin: int = GREEN_LED_PIN,
        red_led_pin: int = RED_LED_PIN,
        dial_pin: int = DIAL_PIN,
        switch_pin: int = SWITCH_PIN,
        dial_alpha: float = DIAL_ALPHA,
    ) -> None:
        self.status = self.IDLE
        
        # Visual status LEDs
        self._green_led = Pin(green_led_pin, Pin.OUT, value=0)
        self._red_led = Pin(red_led_pin, Pin.OUT, value=0)
        self._flash_timer = Timer(-1)
        self._flash_timer.init(period=100, mode=Timer.PERIODIC, callback=self._flash_handler)
        self._flash_counter = 0
        
        # Power dial potentiometer
        self._dial_value = 0
        self._dial_alpha = dial_alpha
        assert 26 <= dial_pin <= 29, "Dial pin must be ADC-capable GPIO26-29"
        self._dial = ADC(Pin(dial_pin))
        self._dial_timer = Timer(-1)
        self._dial_timer.init(period=100, mode=Timer.PERIODIC, callback=self._dial_handler)
        
        # Power enable switch
        self._switch_state = False
        self._switch_timer = Timer(-1)
        self._switch = Pin(switch_pin, Pin.IN, Pin.PULL_UP)
        self._switch_timer.init(period=100, mode=Timer.PERIODIC, callback=self._switch_handler)
    
    @property
    def enable_zvs(self):
        return self._switch_state
    
    @property
    def zvs_power_level(self):
        if self._switch_state:
            return self._dial_value
        return 0
    
    def _dial_handler(self, t: Timer) -> None:
        self._dial_value = self._dial_alpha * round(self._dial.read_u16() / 65535, 2) + (1 - self._dial_alpha) * self._dial_value
    
    def _switch_handler(self, t: Timer) -> None:
        self._switch_state = not self._switch.value()
    
    def _flash_handler(self, t: Timer) -> None:
        
        def _flash(led: Pin) -> None:
            if self._flash_counter == 0: led.on()
            elif self._flash_counter == 1: led.off()
            self._flash_counter = (self._flash_counter + 1) % 3
        
        if self.status == self.STEADY:
            _flash(self._green_led)
        if self.status == self.OVERLOAD:
            _flash(self._red_led)
    
    def set_status(self, status: int) -> None:
        self.status = status
        if status == self.IDLE:
            self._green_led.off()
            self._red_led.off()
        elif status == self.RAMP:
            self._green_led.on()
            self._red_led.off()
        elif status == self.STEADY:
            self._red_led.off()
        elif status == self.OVERLOAD:
            self._green_led.off()
        elif status == self.ERROR:
            self._green_led.off()
            self._red_led.on()
