import time
from zvs import ZVSController

zvs = ZVSController()

if __name__ == "__main__":
    zvs.toggle_pwr(1)
    zvs.set_current_limit(0.5)
    time.sleep(2)
    zvs.set_current_limit(1.0)
    time.sleep(2)
    zvs.toggle_pwr(0)