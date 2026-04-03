from .internal import (
    CAN,
    CAN_CLOCK,
    CAN_EFF_FLAG,
    CAN_ERR_FLAG,
    CAN_RTR_FLAG,
    CAN_SPEED,
    ERROR,
)

from machine import Pin
from .internal import *

class CanError:
    ERROR_OK = ERROR.ERROR_OK
    ERROR_FAIL = ERROR.ERROR_FAIL

class CanMsgFlag:
    RTR = CAN_ERR_FLAG
    EFF = CAN_EFF_FLAG

class CanMsg:
    def __init__(self, can_id = 0, data = None, flags = None):
        if flags:
            self.frame = CANFrame(can_id | flags, data)
        else:
            self.frame = CANFrame(can_id, data)
        self.is_remote_frame = self.frame.is_remote_frame
        self.is_extended_id = self.frame.is_extended_id
        self_id = self.frame.arbitration_id
        self.data = self.frame.data
        self.dlc = self.frame.dlc
    def _set_frame(self, frame):
        self.frame = frame
        self.is_remote_frame = self.frame.is_remote_frame
        self.is_extended_id = self.frame.is_extended_id
        self_id = self.frame.arbitration_id
        self.data = self.frame.data
        self.dlc = self.frame.dlc
    def _get_frame(self):
        return self.frame

class CAN_Wrapper(CAN):
    def __init__(self, spi: int, sck: Pin, mosi: Pin, miso: Pin, cs: Pin):
        super().__init__(SPI(idx=spi, sck=sck, mosi=mosi, miso=miso, cs=cs))
    
    def begin(self, bitrate: int = CAN_SPEED.CAN_125KBPS, canclock: int = CAN_CLOCK.MCP_16MHZ, mode: str = 'normal'):
        ret = self.reset()
        if ret != ERROR.ERROR_OK:
            return ret
        ret = self.setBitrate(bitrate, canclock)
        if ret != ERROR.ERROR_OK:
            return ret
        if mode == "normal": ret = self.setNormalMode()
        elif mode == "config": ret = self.setConfigMode()
        elif mode == "listen_only": ret = self.setListenOnlyMode()
        elif mode == "sleep": ret = self.setSleepMode()
        elif mode == "loopback": ret = self.setLoopbackMode()
        elif mode == "config": ret = self.setConfigMode()
        else: ret = ERROR.ERROR_FAILINIT
        return ret
    
    def init_mask(self, mask, is_ext_id, mask_id):
        ret = self.setFilterMask(mask + 1, is_ext_id, mask_id)
        if ret != ERROR.ERROR_OK:
            return ret
        ret = self.setNormalMode()
        return ret
    
    def init_filter(self, ft, is_ext_id, filter_id):
        ret = self.setFilter(ft, is_ext_id, filter_id)
        if ret != ERROR.ERROR_OK:
            return ret
        ret = self.setNormalMode()
        return ret
    
    def recv(self):
        error, frame = self.readMessage()
        msg = CanMsg()
        msg._set_frame(frame)
        return error, msg
    
    def send(self, msg: CanMsg):
        frame = msg._get_frame()
        error = self.sendMessage(frame)
        return error