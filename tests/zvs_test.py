import time
from ..src.zvs import ZVSController

controller = ZVSController()

def _ensure_properties():
    for _ in range(2): props = controller._get_properties() # Ensure properties have time to be received
    return props

def test_get_properties():
    props = _ensure_properties()
    print("Properties:")
    for k, v in props.items():
        if k in ["v_out", "i_out"]: print(f"\t{k} = {v[-1]}")
        else: print(f"\t{k} = {v}")
    assert "v_out" in props, "v_out not in properties"
    assert "i_out" in props, "i_out not in properties"
    assert "i_lim" in props, "i_lim not in properties"
    assert "supply_temp" in props, "supply_temp not in properties"
    assert "v_in" in props, "v_in not in properties"
    print("PASSED test_get_properties")

def test_enable():
    controller.set_voltage(50)
    controller.enable()
    time.sleep(1)
    v_out = _ensure_properties()["v_out"][-1]
    assert abs(v_out - 50) < 2, f"Expected v_out to be about 50, but got {v_out}"
    print("PASSED test_enable")

def test_disable():
    controller.set_voltage(50)
    controller.disable()
    time.sleep(1)
    v_out = _ensure_properties()["v_out"][-1]
    assert v_out < 2, f"Expected v_out to be about 0, but got {v_out}"
    print("PASSED test_disable")

def test_set_current_limit():
    controller.enable()
    controller.set_current_limit(0.0)
    time.sleep(1)
    i_lim_0 = round(_ensure_properties()["i_lim"], 1)
    
    controller.set_current_limit(1.0)
    time.sleep(1)
    i_lim_1 = round(_ensure_properties()["i_lim"], 1)
    
    assert i_lim_1 > i_lim_0, f"Expected i_lim to increase, but got {i_lim_0} -> {i_lim_1}"
    print("PASSED test_set_current_limit")

def test_set_voltage():
    controller.enable()
    controller.set_voltage(50)
    time.sleep(1)
    v_out_0 = round(_ensure_properties()["v_out"], 0)
    
    controller.set_voltage(55)
    time.sleep(1)
    v_out_1 = round(_ensure_properties()["v_out"], 0)
    
    assert v_out_1 > v_out_0, f"Expected v_out to increase, but got {v_out_0} -> {v_out_1}"
    print("PASSED test_set_voltage")

test_get_properties()
test_enable()
test_disable()
test_set_current_limit()
test_set_voltage()