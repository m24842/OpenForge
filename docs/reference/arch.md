# Architecture

## Overview

Intro, background, broad description...

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

Technical details...


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

Technical details...


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

Technical details...


## Control

### Components
* Microcontroller
* CAN transceiver
* Buck converter

### Functionality
__Inputs__:
* [ZVS temperature](#heating)
* [ZVS power supply temperature](#heating)
* [Coolant temperature](#cooling)
* [ZVS enable/disable signal](#user-interface)
* [Power dial position](#user-interface)

__Outputs__:
* Fans on/off signal
* Control state
* ZVS enable/disable CAN command
* ZVS power supply current limit

Technical details...
