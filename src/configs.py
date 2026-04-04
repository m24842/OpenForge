######################
# ======= UI ======= #
######################
GREEN_LED_PIN = 24
RED_LED_PIN = 25
DIAL_PIN = 27
SWITCH_PIN = 4
DIAL_ALPHA = 0.1
STEADY_STATE_THRESH = 1, 1 # Volts, Amps

######################
# ====== ZVS ======= #
######################
CAN_SPI = 1
CAN_SPI_SCK = 14
CAN_SPI_MOSI = 15
CAN_SPI_MISO = 8
CAN_CS = 19 # CAN_CS -> GPIO19
ZVS_TEMP_PIN = 26

######################
# ==== Cooling ===== #
######################
COOLING_RELAY_PIN = 1
COOLING_TEMP_SPI = 0
COOLING_TEMP_SCK = 2
COOLING_TEMP_MISO = 0
COOLING_TEMP_CS = 5

######################
# ==== Control ===== #
######################
MAX_ZVS_TEMP = 85 # Celsius
MAX_ZVS_SUPPLY_TEMP = 85 # Celsius
MAX_COOLANT_TEMP = 60 # Celsius
