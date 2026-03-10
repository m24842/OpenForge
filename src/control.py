import asyncio
from machine import Pin, Timer
from rotary_encoder import RotaryEncoder
from configs import *
from ui import UI
from zvs import ZVSController
from cooling import CoolingController

class SystemController:
    def __init__(
        self,
        dial_clk_pin,
        dial_dt_pin,
        dial_res=DIAL_RES,
        max_zvs_temp=MAX_ZVS_TEMP,
        max_zvs_supply_temp=MAX_ZVS_SUPPLY_TEMP,
        max_coolant_temp=MAX_COOLANT_TEMP,
    ):
        self._cooling_task = None
        self._heating_task = None
        self._enable_zvs = False
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
        self._dial_sw_timer = Timer(-1)
        self._dial_sw.irq(trigger=Pin.IRQ_FALLING, handler=self._dial_sw_debounce)
        
        self._ui = UI()
        
        self._zvs = ZVSController()
        
        self._cooling = CoolingController()

    def _dial_sw_debounce(self, pin):
        
        def post_debounce(pin):
            if pin.value() == 0: self._enable_zvs = not self._enable_zvs
            self._dial_sw.irq(trigger=Pin.IRQ_FALLING, handler=self._dial_sw_debounce)
        
        self._dial_sw.irq(handler=None)
        self._dial_sw_timer.init(mode=Timer.ONE_SHOT, period=50, callback=lambda t: post_debounce(pin))
    
    async def _cooling_operation(self):
        while True:
            await asyncio.sleep(0.1)
            if self._zvs.enabled or self._cooling.temp > self._max_coolant_temp:
                self._cooling.enable()
            else:
                self._cooling.disable()
    
    async def _heating_operation(self):
        try:
            while True:
                await self._dial_event.wait()
                self._dial_event.clear()
                pct = self._dial.value() / 100
                if self._enable_zvs:
                    if self._zvs.steady: self._ui.set_status(UI.STEADY)
                    else: self._ui.set_status(UI.RAMP)
                    self._zvs.enable()
                    self._zvs.set_current_limit(pct)
                else:
                    self._ui.set_status(UI.IDLE)
                    self._zvs.disable()
        except asyncio.CancelledError:
            self._zvs.disable()
            self._ui.set_status(UI.ERROR)
    
    async def _monitored_operation(self):
        self._cooling_task = asyncio.create_task(self._cooling_operation())
        self._heating_task = asyncio.create_task(self._heating_operation())
        while True:
            await asyncio.sleep(0.1)
            stop = any([
                self._zvs.temp > self._max_zvs_temp,
                self._zvs.supply_temp > self._max_zvs_supply_temp,
                self._cooling.temp > self._max_coolant_temp,
            ])
            if stop and not self._heating_task.done():
                self._heating_task.cancel()
                try: await self._heating_task
                except asyncio.CancelledError: pass
            elif not stop and self._heating_task.done():
                self._heating_task = asyncio.create_task(self._heating_operation())
    
    def run(self):
        asyncio.run(self._monitored_operation())