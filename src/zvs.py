import struct
import asyncio
from collections import deque
from machine import Pin, ADC
from canbus import Can, CanError, CanMsg, CanMsgFlag, CAN_SPEED
from configs import *

class ZVSController:
    
    DEFAULT_ID = 0x0607FF83
    READ_ID = 0x06000783
    
    def __init__(
        self,
        cache_len=10,
        steady_thresh=STEADY_STATE_THRESH,
        temp_pin=ZVS_TEMP_PIN,
    ):
        self._steady_thresh = steady_thresh
        self._state = {
            "enabled" : False,
            "v_out": deque([0.0], maxlen=cache_len),
            "i_out": deque([0.0], maxlen=cache_len),
            "i_lim": 0.0,
            "v_in": 0.0,
            "supply_temp": 0.0,
        }
        
        assert 26 <= temp_pin <= 29, "Temp pin must be ADC-capable GPIO26-29"
        self._temp_pin = ADC(Pin(temp_pin))
        
        self._can = Can(spics=19) # CAN_CS -> GPIO19
        self._irq = Pin(22, Pin.IN) # CAN_INTERRUPT -> GPIO22
        self._recv_event = asyncio.Event()
        self._irq.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: self._recv_event.set())
        asyncio.create_task(self._update_state())
        assert self._can.begin(bitrate=CAN_SPEED.CAN_125KBPS) == CanError.ERROR_OK
    
    @property
    def enabled(self):
        return self._state.get("enabled", False)
    
    @property
    def v_out(self):
        return self._state.get("v_out", [0.0])[-1]
    
    @property
    def i_out(self):
        return self._state.get("i_out", [0.0])[-1]
    
    @property
    def i_lim(self):
        return self._state.get("i_lim", 0.0)
    
    @property
    def temp(self):
        return self._temp_pin.read() * (3.3 / 4095) * 100
    
    @property
    def supply_temp(self):
        return self._state.get("supply_temp", 0.0)

    @property
    def steady(self):
        v_hist = self._state.get("v_out", [0.0])
        i_hist = self._state.get("i_out", [0.0])
        v_range = max(v_hist) - min(v_hist)
        i_range = max(i_hist) - min(i_hist)
        return v_range < self._steady_thresh[0] and i_range < self._steady_thresh[1]
    
    def _float_to_bytearray(self, f):
        return bytearray(struct.pack('<f', f))
    
    def _send_msg(self, id, data):
        res = self._can.send(CanMsg(can_id=id, data=data, flags=CanMsgFlag.EFF))
        return res == CanError.ERROR_OK
    
    async def _update_state(self):
        while True:
            await asyncio.sleep(0.1)
            read_all = [0x00, 0xF0, 0x00, 0x80, 0x46, 0xA5, 0x34, 0x00]
            self._send_msg(self.READ_ID, read_all)
            new_properties = {}
            while len(new_properties) < 5:
                await self._recv_event.wait()
                self._recv_event.clear()
                if self._can.checkReceive():
                    res, msg = self._can.recv()
                    if all([
                        res == CanError.ERROR_OK,
                        msg.dlc >= 8,
                        msg.data[0] == 0x41
                    ]):
                        val = struct.unpack('>f', msg.data[4:8])[0]
                        match msg.data[3]:
                            case 0x01: new_properties["v_out"].append(val)
                            case 0x02: new_properties["i_out"].append(val)
                            case 0x03: new_properties["i_lim"] = val
                            case 0x04: new_properties["supply_temp"] = val
                            case 0x05: new_properties["v_in"] = val
            self._state.update(new_properties)
    
    def enable(self):
        if self.enabled: return
        else: self._state["enabled"] = True
        b = self._float_to_bytearray(0)
        data = [0x03, 0xF0, 0x00, 0x32, 0x00, 0x01, 0x00, 0x00, *b]
        self._send_msg(self.DEFAULT_ID, data)
    
    def disable(self):
        if not self.enabled: return
        else: self._state["enabled"] = False
        data = [0x03, 0xF0, 0x00, 0x32, 0x00, 0x00, 0x00, 0x00]
        self._send_msg(self.DEFAULT_ID, data)

    def set_current_limit(self, pct):
        prange = (0.1, 1.21)
        translated_pct = int(pct * (prange[1] - prange[0]) / prange[0])
        b = self._float_to_bytearray(translated_pct)
        data = [0x03, 0xF0, 0x00, 0x22, *b]
        self._send_msg(self.DEFAULT_ID, data)
