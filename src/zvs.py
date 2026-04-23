try:
    from typing import List, Tuple
except ImportError:
    pass

import struct
import asyncio
from machine import Pin, ADC
from collections import deque
from configs import *
from canbus import Can, CanError, CanMsg, CanMsgFlag, CAN_SPEED, MASK, RXF

class ZVSController:
    """
    Controls the ZVS power and monitors ZVS power supply properties.
    
    Power supply CAN commands:
        - https://github.com/PurpleAlien/R48_Rectifier (MIT License)
        - https://endless-sphere.com/sphere/threads/emerson-vertiv-r48-series-can-programming.114785/post-1747656
    MCU CAN setup:
        - https://github.com/adafruit/Adafruit_CircuitPython_MCP2515 (MIT License)
    """
    
    DEFAULT_ID = const(0x0607FF83)
    READ_ID = const(0x06000783)
    
    def __init__(
        self,
        cache_len: int = 10,
        steady_thresh: Tuple[float, float] = STEADY_STATE_THRESH,
        temp_pin: int = ZVS_TEMP_PIN,
        spi_idx: int = CAN_SPI,
        sck_pin: int = CAN_SPI_SCK,
        mosi_pin: int = CAN_SPI_MOSI,
        miso_pin: int = CAN_SPI_MISO,
        cs_pin: int = CAN_CS,
    ):
        self._steady_thresh = steady_thresh
        self._state = {
            "enabled" : False,
            "v_out": deque([0.0], cache_len),
            "i_out": deque([0.0], cache_len),
            "i_lim": 0.0,
            "v_in": 0.0,
            "supply_temp": 0.0,
        }
        self._prev_i_lim = 0.0
        
        assert 26 <= temp_pin <= 29, "Temp pin must be ADC-capable GPIO26-29"
        self._temp_pin = ADC(Pin(temp_pin))

        # Initialize CAN communication with ZVS power supply
        self._can = Can(
            spi=spi_idx,
            sck=Pin(sck_pin),
            mosi=Pin(mosi_pin),
            miso=Pin(miso_pin),
            cs=Pin(cs_pin)
        )
        assert self._can.begin(bitrate=CAN_SPEED.CAN_125KBPS, mode="config") == CanError.ERROR_OK
        # Set up CAN filters
        for m in [MASK.MASK0, MASK.MASK1]:
            self._can.setFilterMask(m, True, 0x1FFFFFFF)
        for f in [RXF.RXF0, RXF.RXF1, RXF.RXF2, RXF.RXF3, RXF.RXF4, RXF.RXF5]:
            self._can.setFilter(f, True, 0x60F8003) # All property messages use arbitration ID: 0x60F8003
        self._can.setNormalMode()
        
        # Default state
        self.disable()
        self.disable_walk_in()
        self.fan_speed_auto()
        self.set_current_limit(0.0)
        self.set_voltage(58.5)
    
    @property
    def enabled(self) -> bool:
        return self._state.get("enabled", False)
    
    @property
    def v_out(self) -> float:
        return self._state.get("v_out", [0.0])[-1]
    
    @property
    def i_out(self) -> float:
        return self._state.get("i_out", [0.0])[-1]
    
    @property
    def i_lim(self) -> float:
        return self._state.get("i_lim", 0.0)
    
    @property
    def overload(self) -> bool:
        for i in self._state.get("i_out", [0.0]):
            if i == 0.0: return True
        return False

    @property
    def temp(self) -> float:
        # LM19 voltage to temperature conversion
        v = self._temp_pin.read_u16() * (3.3 / 65535)
        temp = -1481.96 + (2.1962e6 + (1.8639 - v) / 3.88e-6)**0.5
        return temp
    
    @property
    def supply_temp(self) -> float:
        return self._state.get("supply_temp", 0.0)

    @property
    def steady(self) -> bool:
        v_hist = self._state.get("v_out", [0.0])
        i_hist = self._state.get("i_out", [0.0])
        v_range = max(v_hist) - min(v_hist)
        i_range = max(i_hist) - min(i_hist)
        return v_range < self._steady_thresh[0] and i_range < self._steady_thresh[1]
    
    def _float_to_bytearray(self, f: float) -> bytearray:
        return bytearray(struct.pack('>f', f))
    
    def _send_msg(self, id: int, data: List[int]) -> bool:
        res = self._can.send(CanMsg(can_id=id, data=data, flags=CanMsgFlag.EFF))
        return res == CanError.ERROR_OK
    
    def _receive_msg(self) -> Tuple[bool, CanMsg]:
        res, msg = self._can.recv()
        return res == CanError.ERROR_OK, msg
    
    def _get_properties(self) -> dict:
        pids = {
            0x01: "v_out",
            0x02: "i_out",
            0x03: "i_lim",
            0x04: "supply_temp",
            0x05: "v_in",
        }
        # Request updates for each property
        for id in pids.keys():
            res = self._send_msg(self.READ_ID, [0x01, 0xF0, 0x00, id, 0x00, 0x00, 0x00, 0x00])
            if not res: continue
            while self._can.checkReceive():
                try:
                    res, msg = self._receive_msg()
                    if not res or len(msg.data) < 8 or msg.data[0] != 0x41: continue
                    p = pids[msg.data[3]]
                    pval = struct.unpack('>f', msg.data[4:8])[0]
                    if p == "v_out": self._state[p].append(pval)
                    elif p == "i_out": self._state[p].append(pval)
                    elif p == "i_lim": self._state[p] = pval
                    elif p == "supply_temp": self._state[p] = pval
                    elif p == "v_in": self._state[p] = pval
                except: pass
        return self._state
    
    async def start_update(self) -> None:
        asyncio.create_task(self._update_state())
    
    async def _update_state(self) -> None:
        """
        Periodically request updated properties from ZVS power supply.
        """
        while True:
            await asyncio.sleep(1.0)
            self._get_properties()
            print("vout", self._state["v_out"][-1], "iout", self._state["i_out"][-1], "i_lim", self._state["i_lim"], "supply_temp", self._state["supply_temp"], "v_in", self._state["v_in"])

    def enable(self) -> bool:
        self._state["enabled"] = True
        data = [0x03, 0xF0, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00]
        return self._send_msg(self.DEFAULT_ID, data)
    
    def disable(self) -> bool:
        self._state["enabled"] = False
        data = [0x03, 0xF0, 0x00, 0x30, 0x00, 0x01, 0x00, 0x00]
        return self._send_msg(self.DEFAULT_ID, data)

    def disable_walk_in(self) -> bool:
        data = [0x03, 0xF0, 0x00, 0x32, 0x00, 0x00, 0x00, 0x00]
        return self._send_msg(self.DEFAULT_ID, data)

    def fan_speed_auto(self) -> bool:
        data = [0x03, 0xF0, 0x00, 0x33, 0x00, 0x00, 0x00, 0x00]
        return self._send_msg(self.DEFAULT_ID, data)

    def set_current_limit(self, pct: float) -> bool:
        if pct != self._prev_i_lim:
            self._state["i_out"].clear()
        self._prev_i_lim = pct
        prange = (0.1, 1.21)
        translated_pct = pct * (prange[1] - prange[0]) + prange[0]
        b = self._float_to_bytearray(translated_pct)
        # 0x22 for temporary limit, 0x19 for permanent limit
        # Sending both commands back-to-back sets the limit immediately rather than after a 30s delay
        res = True
        for fixed in [0x22, 0x19]:
            data = [0x03, 0xF0, 0x00, fixed] + list(b)
            res &= self._send_msg(self.DEFAULT_ID, data)
        return res

    def set_voltage(self, v: float) -> bool:
        # Voltage range: 41.0V - 58.5V
        b = self._float_to_bytearray(v)
        # 0x21 for temporary voltage, 0x24 for permanent voltage
        # Sending both commands back-to-back sets the voltage immediately rather than after a 30s delay
        res = True
        for fixed in [0x21, 0x24]:
            data = [0x03, 0xF0, 0x00, fixed] + list(b)
            res &= self._send_msg(self.DEFAULT_ID, data)
        return res