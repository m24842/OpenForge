import struct
from machine import Pin
from queue import Queue
from canbus import Can, CanError, CanMsg, CanMsgFlag, CAN_SPEED

def float_to_bytearray(f):
    return bytearray(struct.pack('<f', f))

class ZVSController:
    def __init__(self):
        self.can = Can()
        self.irq = Pin(22, Pin.IN)
        self.recv_queue = Queue()
        self.irq.irq(trigger=Pin.IRQ_FALLING, handler=self.recv_response)
        assert self.can.begin(bitrate=CAN_SPEED.CAN_125KBPS) == CanError.ERROR_OK
    
    def send_cmd(self, data):
        res = self.can.send(CanMsg(can_id=0x0607FF83, data=data, flags=CanMsgFlag.EFF))
        return res == CanError.ERROR_OK

    def recv_response(self, pin):
        if self.can.checkReceive():
            res, msg = self.can.recv()
            if res == CanError.ERROR_OK:
                self.recv_queue.put((msg.can_id, msg.data.hex()))
    
    def toggle_pwr(self, enable):
        if not enable:
            data = [0x03, 0xF0, 0x00, 0x32, 0x00, 0x00, 0x00, 0x00]
        else:
            b = float_to_bytearray(0)
            data = [0x03, 0xF0, 0x00, 0x32, 0x00, 0x01, 0x00, 0x00, *b]
        self.send_cmd(data)
    
    def set_current_limit(self, pct, fixed=True):
        prange = (0.1, 1.21)
        translated_pct = int(pct * (prange[1] - prange[0]) / prange[0])
        b = float_to_bytearray(translated_pct)
        p = 0x22 if not fixed else 0x19
        data = [0x03, 0xF0, 0x00, p, *b]
        self.send_cmd(data)
