import time
from ..src.ui import UI

ui = UI()

def test_status():
    ui.set_status(ui.IDLE)
    print("IDLE: green and red LEDs should be off")
    time.sleep(3)
    
    ui.set_status(ui.RAMP)
    print("RAMP: green LED should be on, red LED should be off")
    time.sleep(3)
    
    ui.set_status(ui.STEADY)
    print("STEADY: green LED should be flashing, red LED should be off")
    time.sleep(3)
    
    print("PASSED test_status")

def test_switch():
    start_state = ui._switch_state
    next_state = "ON" if not start_state else "OFF"
    print(f"Toggle the switch {next_state} to proceed")
    while ui._switch_state == start_state: time.sleep(0.1)
    print("PASSED test_switch")

def test_dial():
    start_value = round(ui._dial_value, 1)
    time.sleep(1)
    assert round(ui._dial_value, 1) == start_value
    print(f"Turn the dial to change the value from {start_value}")
    while round(ui._dial_value, 1) == start_value: time.sleep(0.1)
    print("PASSED test_dial")

test_status()
test_switch()
test_dial()