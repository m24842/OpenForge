# Usage

## Startup/Shutdown

### Startup Sequence
1. Disable heating using the [heating enable/disable switch](#heating-enabledisable-switch)
2. Set the [temperature dial](#temperature-dial) to the lowest setting
3. Plug in the control power supply (i.e. the PSU for the MCU and cooling)
4. Plug in the heating power supply (i.e. the PSU for the ZVS driver)
5. Reset the emergency stop button
6. Load the plugged crucible with metal
7. Situate/align the casting mold below the crucible
7. Enable heating using the [heating enable/disable switch](#heating-enabledisable-switch)
8. Set the crucible temperature using the [temperature dial](#temperature-dial)
9. Wait until furnace reaches [steady state](#furnace-operation-modes) or metal is visually molten
10. Pull the crucible plug using tongs to cast the molten metal

### Shutdown Sequence
1. Disable heating using the [heating enable/disable switch](#heating-enabledisable-switch)
2. Set the [temperature dial](#temperature-dial) to the lowest setting
3. Wait until fans shut off to ensure critical components are protected from overheating
3. Unplug in the heating power supply (i.e. the PSU for the ZVS driver)
4. Unplug in the control power supply (i.e. the PSU for the MCU and cooling)

## Temperature Control

<!-- TODO: add photo -->

### Temperature Dial:
  Crucible temperature can be adjusted down to 10% of the nominal temperature (see [Architecture](../reference/arch.md) for details). The nominal temperature of the crucible depends on the mains voltage level (i.e. 120VAC or 240VAC).

### Heating Enable/Disable Switch:
  Crucible heating can be disabled to bring the temperature down to room temperature using the heating enable/disable switch. This essentially cuts power to the induction coil as dicussed in [Architecture](../reference/arch.md).

### Furnace Operation Modes:
  The furnace operation mode is displayed using red and green LEDs (see [Architecture](../reference/arch.md) for more details). The four furnace states include:
  1. Idle: ⚫️⚫️ (both off)
      * Furnace heating is disabled
  2. Ramp: ⚫️🟢 (green on)
      * Furnace is enabled and temperature is __ramping__.
  3. Steady: ⚫️🟢 (green flashing)
      * Furnace is enabled and temperature is __steady__.
  4. Error: 🔴⚫️ (red on)
      * Furnace has entered an erroneous state.

## Safety

<!-- TODO: add photo -->

### Emergency Stop Button:
  In case of an emergency, power to the induction coil can be immediately terminated by pressing the e-stop button. Cooling will continue operating to protect critical system components.