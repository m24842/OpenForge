# Architecture

## Overview

<p align="center">
  <img src="../../assets/system_block.svg" alt="OpenForge" width="90%">
</p>

* [User Interface](#user-interface)
* [Heating](#heating)
* [Cooling](#cooling)
* [Control](#control)

## User Interface

### Components
|Name|Suggested Part|
|:---|-------------:|
|Toggle switch|[Amazon link](https://a.co/d/08M4XrNV)|
|Rotary potentiometer 10kΩ (power dial)|[Amazon link](https://a.co/d/00b6DRkQ)|
|Emergency stop button|[Amazon link](https://a.co/d/0hutAWxC)|
|120V relay|[Amazon link](https://a.co/d/00kgoHyW)|
|Red LED|-|
|Green LED|-|

### Functionality
__Inputs__:
* User input
* [Control state](#control)

__Outputs__:
* ZVS enable/disable signal
* Power dial position
* LED control signals

The furnace user interface enables intuitive control of the crucible temperature and includes three main inputs: a __power dial__, __enable/disable switch__, and __e-stop button__.

The __power dial__ outputs an analog signal [0V, 3.3V] which is converted to a current limit percentage for the ZVS power supply by the microcontroller. Since the minimum current limiting for the ZVS power supply is 10% rather than 0%, the __enable/disable switch__ allows the output to be shut off completely and enter idle mode. Both setting the current limit and output enable/disable are accomplished using CAN commands supported by the ZVS power supply (see [zvs.py](../../src/zvs.py) for further details and references).

The __e-stop button__ allows immediate termination of ZVS operation by directly controlling a relay to cut off AC power to the ZVS power supply (i.e. bypassing the microcontroller).

The furnace operation mode is displayed using __red and green LEDs__. Each LED is driven independently by the microcontroller, allowing multiple states to be displayed using flash patterns. The four furnace states include:
1. Idle: ⚫️⚫️ (both off)
    * Furnace heating is disabled
2. Ramp: ⚫️🟢 (green on)
    * Furnace is enabled and temperature is __ramping__. Ramping is identified as a changing voltage/current being drawn by the ZVS driver.
3. Steady: ⚫️🟢 (green flashing)
    * Furnace is enabled and temperature is __steady__.
    Steadiness is identified as a roughly constant voltage/current being drawn by the ZVS driver.
4. Overload: 🔴⚫️ (red flashing)
    * Furnace power supply is __overloaded__. The power supply will throttle power unless the temperature setting is reduced (throttling reduces effective power significantly).
5. Error: 🔴⚫️ (red on)
    * Furnace has entered an erroneous state. The system controller monitors temperatures of critical components and disables heating if temperature limits are exceeded.


## Heating

### Components
|Name|Suggested Part|
|:---|-------------:|
|ZVS driver|[Amazon link](https://a.co/d/0dc9iLwj)|
|3kW DC power supply (ZVS power supply)|*included w/ ZVS driver|
|Induction coil|*included w/ ZVS driver|
|IC temperature sensor|[Digikey link](https://www.digikey.com/short/981h0vrd)|
|Bottom pour crucible|[Amazon link](https://a.co/d/0bnduDAu) *hole must be drilled|
|Bottom pour crucible plug|[Amazon link](https://a.co/d/034yB7Kj)|
|Ceramic fiber insulation|[Amazon link](https://a.co/d/070G24vb)|
|Fiber glass coil sheath|[Amazon link](https://a.co/d/0huBojl4)|

### Functionality
__Inputs__:
* [ZVS enable/disable CAN command](#control)
* [ZVS power supply current limit](#control)

__Outputs__:
* Induction coil power
* ZVS temperature
* ZVS power supply temperature
* ZVS power supply output voltage/current

Induction heating is accomplished using a __ZVS driver__. A __3kW power supply__ feeds the __ZVS driver__ to attain temperatures required for melting common engineering metals such as aluminum. The __induction coil__ is water cooled to enable long run times and optimal heating efficiency (see [Cooling](#cooling) for further details).

The __ZVS power supply__ supports CAN commands for adjusting operation parameters such as output voltage, current, fan speed, etc. (see [zvs.py](../../src/zvs.py) for further details and references). Only two parameters are dynamically controlled during furnace operation: _current limit_ and _output enable/disable_. These are transmitted from the microcontroller to the __ZVS power supply__ based on user inputs as discussed in [User Interface](#user-interface).

Additionally, the __ZVS power supply__ supports CAN commands for reading operation parameters. The most relevant values include output voltage, current, and temperature. These are used by the microcontroller to determine furnace operation modes and error conditions as discussed in [User Interface](#user-interface).


## Cooling

### Components
|Name|Suggested Part|
|:---|-------------:|
|12V fans|[Amazon link](https://a.co/d/06POpfxe)|
|12V pump|*included w/ ZVS driver|
|12V relay|[Amazon link](https://a.co/d/09bBEAkq)|
|12V power supply|[Amazon link](https://a.co/d/0fyLhfdB)|
|Radiator|[Amazon link](https://a.co/d/0c7LKzQl)|
|Thermocouple + amplifier|[Amazon link](https://a.co/d/0a98Mzv3)|
|Tubing|[Amazon link](https://a.co/d/06ERqqzK)|
|Hose clamps|-|
|Hose adapters|-|
|Reservoir|-|

### Functionality
__Inputs__:
* [Fans on/off signal](#control)

__Outputs__:
* Coolant temperature
* Coolant flow to induction coil

Cooling critical components of the furnace is accomplished using both air and water cooling. Specifically, the induction coil is water cooled while the electronics housing is air cooled. Additionally, __fans__ are installed on the coolant radiator to maintain a reasonable water temperature for circulating through the induction coil.

The __water pump__ is always running to allow for accurate measurements of nominal water temperature using a downstream thermocouple. Water temperature measurements are transmitted to the microcontroller for determining error conditions as discussed in [User Interface](#user-interface). On the other hand, __fans__ are controlled by the microcontroller through a relay. __Fans__ only run while heating is enabled or some temperature limit has been exceeded.


## Control

### Components
|Name|Suggested Part|
|:---|-------------:|
|Microcontroller (MCU)|[Adafruit link](https://www.adafruit.com/product/5724)|
|CAN transceiver|*onboard the MCU|
|Buck converter|[Amazon link](https://a.co/d/0ix6y9vt)|

### Functionality
__Inputs__:
* [ZVS temperature](#heating)
* [ZVS power supply temperature](#heating)
* [ZVS power supply output voltage/current](#heating)
* [Coolant temperature](#cooling)
* [ZVS enable/disable signal](#user-interface)
* [Power dial position](#user-interface)

__Outputs__:
* Fans on/off signal
* Control state
* ZVS enable/disable CAN command
* ZVS power supply current limit

System control is split into two components: __heating control__ and __cooling control__.

__Heating control__ involves setting the ZVS power supply current limit and output disable/enable based on user inputs and component temperature readings. ZVS power supply parameters directly match user inputs as long as no temperature limits have been exceeded. If an erroneous state is encountered, heating is disabled until the furnace returns to a valid state.

__Cooling control__ involves enabling/disabling the fans for the electronics and coolant radiator. Fans are only enabled while heating is enabled or some temperature limit has been exceeded.

Additionally, the system controller is responsible for updating the furnace state displayed by the [User Interface](#user-interface).

## Miscellaneous

### Components
|Name|Suggested Part|
|:---|-------------:|
|Aluminum sheet|[link](https://www.onlinemetals.com/en/buy/aluminum/0-063-aluminum-sheet-5052-h32/pid/7128) *24" X 48"|
|Door hinges|-|
|Fasteners|-|