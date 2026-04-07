# Configuration

### _Reference_
* All configurations located in [configs.py](../../src/configs.py)
* Pinouts for the RP2040 CAN Bus Feather can be found [here](https://learn.adafruit.com/adafruit-rp2040-can-bus-feather/pinouts)

### User Interface Configurations
* __Status LED pins__: Any two GPIO pins can be used
* __Dial pin__: Any ADC capable GPIO pin can be used (i.e. GPIO 26-29)
* __Switch pin__: Any GPIO pin can be used
* __Dial alpha__: Determines the smoothing factor for translating dial position to heating power. Values closer to 1.0 reduce smoothing while values closer 0.0 increase smoothing.
* __Steady state threshold__: Determines the maximum deviations in output voltage and current to still be considered steady state. Makes no impact to the heating process, only status visualization.

### ZVS Driver Configurations
* __CAN SPI index__: This should not be changed from 1 since the RP2040 CAN Bus Feather has its CAN transceiver connected to SPI1
* __CAN SPI SCK pin__: Any SCK1 capable GPIO pin can be used (i.e. GPIO 10, 14, or 26)
* __CAN SPI MOSI pin__: Any TX1 capable GPIO pin can be used (i.e. GPIO 11, 15, or 27)
* __CAN SPI MISO pin__: Any RX1 capable GPIO pin can be used (i.e. GPIO 8, 12, or 28)
* __CAN CS pin__: This should not be changed from GPIO 19 since CAN_CS is tied to it
* __ZVS temp pin__: Any ADC capable GPIO pin can be used (i.e. GPIO 26-29)

### Cooling Configurations
* __Cooling relay pin__: Any GPIO pin can be used
* __Cooling temp SPI index__: This should not be changed from 0 since SPI1 is being used for CAN
* __Cooling temp SPI SCK pin__: Any SCK0 capable GPIO pin can be used (i.e. GPIO 2 or 6)
* __Cooling temp SPI MISO pin__: Any RX0 capable GPIO pin can be used (i.e. GPIO 0 or 4)
* __Cooling temp SPI CS pin__: Any CSn0 capable GPIO pin can be used (i.e. GPIO 1 or 5)

### Control Configurations
* __Maximum ZVS temp__: In celsius, determines a condition for which the system cuts power to the ZVS driver
* __Maximum ZVS power supply temp__: In celsius, determines a condition for which the system cuts power to the ZVS driver
* __Maximum coolant temp__: In celsius, determines a condition for which the system cuts power to the ZVS driver
