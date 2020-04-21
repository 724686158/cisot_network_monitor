import time

from lib.time_units import TimeStamp


class TestPacket:
    def __init__(self, src_port):
        self._src_port = src_port

        current_time = time.time()
        self._send_ts = TimeStamp(current_time)

    STR_DELIMETER = ':'

    def __str__(self):
        return str(self._send_ts) + self.STR_DELIMETER + str(self._src_port)

    @classmethod
    def from_string(cls, raw_payload):
        string_packet = raw_payload.replace('\x00', '')
        ts_string, src_port_string = string_packet.split(cls.STR_DELIMETER, 2)
        pkt = TestPacket(int(src_port_string))
        pkt._send_ts = TimeStamp(ts_string)
        return pkt


class ReceivedTestPacket:
    def __init__(self, src_dpid, dst_dpid, send_ts):
        self.src_dpid = src_dpid
        self.dst_dpid = dst_dpid
        self.send_ts = send_ts
        self.receive_ts = TimeStamp(time.time())