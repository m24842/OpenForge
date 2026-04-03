from math import sqrt
from machine import ADC, Pin
import time

# Configuration
ADC_PIN = 26
VCC = 3.3
ADC_RES = 65535
SAMPLE_INTERVAL_MS = 1000

# Setup
adc = ADC(Pin(ADC_PIN))


def read_Vo():
    """Read ADC and convert raw value to voltage."""
    raw = adc.read_u16()
    return (raw / ADC_RES) * VCC


def Vo_to_celsius(v):
    """
    Convert LM19 Vout to Celsius.
    Datasheet formula: T = -1481.96 + sqrt(2.1962e6 + (1.8639 - V) / 3.88e-6)
    Valid range: -55°C to +130°C
    """
    try:
        return -1481.96 + sqrt(2.1962e6 + (1.8639 - v) / 3.88e-6)
    except ValueError:
        return float('nan')


def celsius_to_fahrenheit(c):
    """Convert Celsius to Fahrenheit."""
    return (c * 9 / 5) + 32


# Main Loop
print("LM19 Temperature Sensor - RP2040")
print(f"Reading from GPIO{ADC_PIN} every {SAMPLE_INTERVAL_MS}ms")
print("-" * 40)

while True:
    Vo = read_Vo()
    temp_c = Vo_to_celsius(Vo)

    if temp_c != temp_c:  # NaN check
        print(f"Vout: {Vo:.4f} V  |  Temp: OUT OF RANGE")
    else:
        temp_f = celsius_to_fahrenheit(temp_c)
        print(f"Vout: {Vo:.4f} V  |  Temp: {temp_c:.2f} °C  |  {temp_f:.2f} °F")

    time.sleep_ms(SAMPLE_INTERVAL_MS)