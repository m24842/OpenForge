import asyncio
from configs import *
from ui import UI
from zvs import ZVSController
from cooling import CoolingController

class SystemController:
    """
    Manages furnace operation.
    Receives inputs from the UI, monitors ZVS and coolant temps, controls the ZVS and cooling systems.
    """
    def __init__(
        self,
        max_zvs_temp: float = MAX_ZVS_TEMP,
        max_zvs_supply_temp: float = MAX_ZVS_SUPPLY_TEMP,
        max_coolant_temp: float = MAX_COOLANT_TEMP,
    ) -> None:
        self._cooling_task = None
        self._heating_task = None
        self._max_zvs_temp = max_zvs_temp
        self._max_zvs_supply_temp = max_zvs_supply_temp
        self._max_coolant_temp = max_coolant_temp
        
        # Initialize all subsystems
        self._ui = UI()
        self._cooling = CoolingController()
        self._zvs = ZVSController()

    async def _cooling_operation(self) -> None:
        """
        Enable cooling system when ZVS is enabled or coolant temp exceeds max threshold.
        """
        while True:
            await asyncio.sleep(0.1)
            if self._zvs.enabled or self._cooling.temp > self._max_coolant_temp:
                self._cooling.enable()
            else:
                self._cooling.disable()
    
    async def _heating_operation(self) -> None:
        """
        Power ZVS based on UI inputs and ZVS status.
        """
        try:
            prev_pct = 0
            while True:
                await asyncio.sleep(0.1)
                pct = self._ui.dial_value
                if pct == prev_pct: continue # Avoid redundant commands to ZVS power supply
                prev_pct = pct
                
                if self._ui.enable_zvs:
                    if self._zvs.steady: self._ui.set_status(UI.STEADY)
                    else: self._ui.set_status(UI.RAMP)
                    self._zvs.enable()
                    self._zvs.set_current_limit(pct)
                else:
                    self._ui.set_status(UI.IDLE)
                    self._zvs.disable()
        except asyncio.CancelledError:
            # Shutdown procedure
            self._zvs.disable()
            self._ui.set_status(UI.ERROR)
    
    async def _monitored_operation(self) -> None:
        """
        Run furnace operations while monitoring temps to trigger safe shutdown if thresholds are exceeded.
        """
        await self._zvs.start_update() # Start ZVS state updates
        self._cooling_task = asyncio.create_task(self._cooling_operation()) # Manage cooling system
        self._heating_task = asyncio.create_task(self._heating_operation()) # Manage ZVS power
        while True:
            await asyncio.sleep(0.1)
            stop = any([
                self._zvs.temp > self._max_zvs_temp, # ZVS over-temp
                self._zvs.supply_temp > self._max_zvs_supply_temp, # ZVS supply over-temp
                self._cooling.temp > self._max_coolant_temp, # Coolant over-temp
            ])
            if stop and not self._heating_task.done():
                # Shutdown ZVS
                self._heating_task.cancel()
                try: await self._heating_task
                except asyncio.CancelledError: pass
            elif not stop:
                if not self._heating_task.done(): continue
                exc = self._heating_task.exception()
                if exc: print("Heating task err:", exc)
                self._heating_task = asyncio.create_task(self._heating_operation()) # Restart ZVS operation
    
    async def run(self) -> None:
        asyncio.create_task(self._monitored_operation())
        while True: await asyncio.sleep(1)
