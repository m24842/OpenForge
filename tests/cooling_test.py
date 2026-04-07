import time
from ..src.cooling import CoolingController

controller = CoolingController()

def test_temp():
    temp = controller.temp
    assert temp != -1, "Error reading coolant temperature"
    print(f"Current coolant temperature: {temp}°C")
    assert 20 <= temp <= 30, "Coolant temperature out of expected range (20-30°C)"
    print("PASSED test_temp")

def test_relay():
    print("Fans and pump should turn ON")
    controller.enable()
    time.sleep(3)
    print("Fans and pump should turn OFF")
    controller.disable()
    time.sleep(3)
    print("PASSED test_relay")

test_temp()
test_relay()