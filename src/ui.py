from machine import Pin, ADC, Timer
from configs import *

class UI:
    """
    Captures user inputs and provides visual feedback on system status.
    """
    
    IDLE = const(0)
    RAMP = const(1)
    STEADY = const(2)
    ERROR = const(3)
    
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
        self.dial_value = 0
        self._dial_alpha = dial_alpha
        assert 26 <= dial_pin <= 29, "Dial pin must be ADC-capable GPIO26-29"
        self._dial = ADC(Pin(dial_pin))
        self._dial_timer = Timer(-1)
        self._dial_timer.init(period=100, mode=Timer.PERIODIC, callback=self._dial_handler)
        
        # Power enable switch
        self._switch_state = False
        self._switch_timer = Timer(-1)
        self._switch = Pin(switch_pin, Pin.IN, Pin.PULL_UP)
        self._switch.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._switch_handler)
    
    @property
    def enable_zvs(self):
        return self._switch_state
    
    def _dial_handler(self, t: Timer) -> None:
        if self._switch_state:
            self.dial_value = self._dial_alpha * round(self._dial.read_u16() / 65535, 2) + (1 - self._dial_alpha) * self.dial_value
        else:
            self.dial_value = 0
    
    def _switch_handler(self, pin: Pin) -> None:
        
        def _debounce_handler(pin: Pin) -> None:
            self._switch_state = not bool(pin.value())
        
        self._switch_timer.init(
            period=50,
            mode=Timer.ONE_SHOT,
            callback=lambda t: _debounce_handler(pin)
        )
    
    def _flash_handler(self, t: Timer) -> None:
        if self.status == self.STEADY:
            if self._flash_counter == 0: self._green_led.on()
            elif self._flash_counter == 1: self._green_led.off()
            self._flash_counter = (self._flash_counter + 1) % 3
    
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
        elif status == self.ERROR:
            self._green_led.off()
            self._red_led.on()
