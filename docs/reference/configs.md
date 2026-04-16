# Configuration

> __Note__: All configurations are located in [configs.py](../../src/configs.py). Default values are provided.

> __Note__: Pinouts (and other details) for the RP2040 CAN Bus Feather can be found [here](https://learn.adafruit.com/adafruit-rp2040-can-bus-feather/pinouts).

## User Interface Configurations
* `GREEN_LED_PIN`, `RED_LED_PIN`: Any two GPIO pins can be used
* `DIAL_PIN`: Any ADC capable GPIO pin can be used (i.e. GPIO 26-29)
* `SWITCH_PIN`: Any GPIO pin can be used
* `DIAL_ALPHA`: Determines the smoothing factor for translating dial position to heating power. Values closer to 1.0 reduce smoothing while values closer 0.0 increase smoothing.
* `STEADY_STATE_THRESH`: Determines the maximum deviations in output voltage and current to still be considered steady state. Makes no impact to the heating process, only status visualization.

## ZVS Driver Configurations
* `CAN_SPI`: This should not be changed from 1 since the RP2040 CAN Bus Feather has its CAN transceiver connected to SPI1
* `CAN_SPI_SCK`: Any SCK1 capable GPIO pin can be used (i.e. GPIO 10, 14, or 26)
* `CAN_SPI_MOSI`: Any TX1 capable GPIO pin can be used (i.e. GPIO 11, 15, or 27)
* `CAN_SPI_MISO`: Any RX1 capable GPIO pin can be used (i.e. GPIO 8, 12, or 28)
* `CAN_CS`: This should not be changed from GPIO 19 since CAN_CS is tied to it
* `ZVS_TEMP_PIN`: Any ADC capable GPIO pin can be used (i.e. GPIO 26-29)

## Cooling Configurations
* `COOLING_RELAY_PIN`: Any GPIO pin can be used
* `COOLING_TEMP_SPI`: This should not be changed from 0 since SPI1 is being used for CAN
* `COOLING_TEMP_SCK`: Any SCK0 capable GPIO pin can be used (i.e. GPIO 2 or 6)
* `COOLING_TEMP_MISO`: Any RX0 capable GPIO pin can be used (i.e. GPIO 0 or 4)
* `COOLING_TEMP_CS`: Any CSn0 capable GPIO pin can be used (i.e. GPIO 1 or 5)

## Control Configurations
* `MAX_ZVS_TEMP`: In celsius, determines a condition for which the system cuts power to the ZVS driver
* `MAX_ZVS_PSU_TEMP`: In celsius, determines a condition for which the system cuts power to the ZVS driver
* `MAX_COOLANT_TEMP`: In celsius, determines a condition for which the system cuts power to the ZVS driver
