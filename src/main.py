import asyncio
from configs import *
from control import SystemController

if __name__ == "__main__":
    asyncio.run(SystemController(
        max_zvs_temp=MAX_ZVS_TEMP,
        max_zvs_psu_temp=MAX_ZVS_PSU_TEMP,
        max_coolant_temp=MAX_COOLANT_TEMP,
    ).run())