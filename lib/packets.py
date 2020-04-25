#
# Copyright (c) 2020 by Ilya Tsyganov, Ryazan State Radio Engineering University.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
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