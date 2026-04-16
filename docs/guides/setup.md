# Setup

## Overview
1. [Software](#software)
2. [Electrical](#electrical)
3. [Hardware](#hardware)

## Software
1. Follow [this tutorial](https://randomnerdtutorials.com/raspberry-pi-pico-vs-code-micropython/) to set up MicroPython on the microcontroller and the VSCode MicroPico extension
2. Open [src](../../src) in VSCode. MicroPico should automatically recognize it as a project.
3. Run the `Upload project to Pico` command to complete setup of the microcontroller

## Electrical
1. Following the [system schematic](../../pcb), assemble the electrical hardware. This can be done using PCBs or protoboards.
2. If making modifications to GPIO usage, make sure to update [configs.py](../../src/configs.py)

## Hardware
1. Following the [design files](../../cad), fabricate and assemble components for the furnace enclosure. Feel free to modify the enclosure design to better fit your needs.
2. Mount electrical hardware to the enclosure
