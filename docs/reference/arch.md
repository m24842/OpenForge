# Architecture

## Overview
* [User Interface](#user-interface)
* [Heating](#heating)
* [Cooling](#cooling)
* [Control](#control)

## User Interface

### Components
* Toggle switch
* Rotary potentiometer 10kΩ (power dial)
* Emergency stop button
* 120V relay
* Red LED
* Green LED

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
4. Error: 🔴⚫️ (red on)
    * Furnace has entered an erroneous state. The system controller monitors temperatures of critical components and disables heating if temperature limits are exceeded.


## Heating

### Components
* Induction coil
* ZVS driver
* 3kW DC power supply (ZVS power supply)
* IC temperature sensor
* Bottom pour crucible
* Ceramic fiber insulation
* Fiber glass coil sheath

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
* 12V fans
* 12V pump
* 12V relay
* 12V power supply
* Radiator
* Thermocouple + amplifier
* Tubing
* Reservoir

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
* Microcontroller
* CAN transceiver
* Buck converter

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
