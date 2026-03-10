import asyncio
from machine import Pin, Timer
from rotary_encoder import RotaryEncoder
from configs import *
from ui import UI
from zvs import ZVSController

class SystemController:
    def __init__(
        self,
        dial_clk_pin,
        dial_dt_pin,
        green_led_pin,
        red_led_pin,
        dial_res=DIAL_RES,
        max_zvs_temp=MAX_ZVS_TEMP,
        max_zvs_supply_temp=MAX_ZVS_SUPPLY_TEMP,
        max_coolant_temp=MAX_COOLANT_TEMP,
    ):
        self._main_task = None
        self._zvs_pwr = False
        self._max_zvs_temp = max_zvs_temp
        self._max_zvs_supply_temp = max_zvs_supply_temp
        self._max_coolant_temp = max_coolant_temp
        
        self._dial = RotaryEncoder(
            dial_clk_pin,
            dial_dt_pin,
            min_val=0,
            max_val=100,
            incr=dial_res,
            reverse=False,
            range_mode=RotaryEncoder.RANGE_BOUNDED,
            pull_up=True,
            half_step=False,
            invert=False,
        )
        self._dial_event = asyncio.Event()
        self._dial.add_listener(lambda: self._dial_event.set())

        self._dial_sw = Pin(16, Pin.IN, Pin.PULL_UP)
        self._dial_sw_time = Timer(-1)

        self._dial_sw.irq(trigger=Pin.IRQ_FALLING, handler=self._dial_sw_debounce)
        
        self._ui = UI(green_led_pin, red_led_pin)
        
        self._zvs = ZVSController()

    def _dial_sw_debounce(self, pin):
        
        def post_debounce(pin):
            if pin.value() == 0: self._zvs_pwr = not self._zvs_pwr
            self._dial_sw.irq(trigger=Pin.IRQ_FALLING, handler=self._dial_sw_debounce)
        
        self._dial_sw.irq(handler=None)
        self._dial_sw_time.init(mode=Timer.ONE_SHOT, period=50, callback=lambda t: post_debounce(pin))
    
    async def normal_operation(self):
        try:
            while True:
                await self._dial_event.wait()
                self._dial_event.clear()
                pct = self._dial.value() / 100
                if self._zvs_pwr:
                    if self._zvs.steady: self._ui.set_status(UI.STEADY)
                    else: self._ui.set_status(UI.RAMP)
                    self._zvs.toggle_pwr(1)
                    self._zvs.set_current_limit(pct)
                else:
                    self._ui.set_status(UI.IDLE)
                    self._zvs.toggle_pwr(0)
        except asyncio.CancelledError:
            self._zvs.toggle_pwr(0)
            self._ui.set_status(UI.ERROR)
    
    async def monitored_operation(self):
        self._main_task = asyncio.create_task(self.normal_operation())
        while True:
            await asyncio.sleep(0.1)
            # TODO: Get temp readings from ZVS driver and cooling loop
            if any([
                self._zvs.supply_temp > self._max_zvs_supply_temp,
            ]):
                self._main_task.cancel()
                try: await self._main_task
                except asyncio.CancelledError: pass
            elif self._main_task.done():
                self._main_task = asyncio.create_task(self.normal_operation())
    
    def run(self):
        asyncio.run(self.monitored_operation())