from configs import *
from control import SystemController

controller = SystemController(
    dial_clk_pin=DIAL_CLK_PIN,
    dial_dt_pin=DIAL_DT_PIN,
    green_led_pin=GREEN_LED_PIN,
    red_led_pin=RED_LED_PIN,
    max_zvs_temp=MAX_ZVS_TEMP,
    max_zvs_supply_temp=MAX_ZVS_SUPPLY_TEMP,
    max_coolant_temp=MAX_COOLANT_TEMP,
)

if __name__ == "__main__":
    controller.run()