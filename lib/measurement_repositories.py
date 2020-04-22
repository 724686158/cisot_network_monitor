import time
import math

from lib.time_units import TimeStamp, TimeDelta
from lib.packets import ReceivedTestPacket


class DatapathTimings:
    def __init__(self):
        self._response_time = TimeDelta(0.0)
        self._send_ts = TimeStamp(0.0)

    def get_response_time(self):
        return self._response_time

    def write_send_time(self):
        self._send_ts = TimeStamp(time.time())

    def write_receive_time(self):
        receive_ts = TimeStamp(time.time())
        self._response_time = receive_ts - self._send_ts
        self._send_ts = TimeStamp(0.0)


class DatapathResponseTimeRepository:
    def __init__(self):
        self._timings = {}

    def write_send_time(self, dpid):
        self._timings.setdefault(dpid, DatapathTimings()).write_send_time()

    def write_receive_time(self, dpid):
        try:
            self._timings[dpid].write_receive_time()
        except KeyError:
            raise KeyError("dpid " + str(dpid) +
                           " is not in datapath time repository")

    def get_response_time(self, dpid):
        return self._timings.setdefault(dpid,
                                        DatapathTimings()).get_response_time()

    def __str__(self):
        s = ''
        for dpid in self._timings:
            s += '[{0}]\t{1} ms\n'.format(
                dpid, self._timings[dpid].get_response_time().milliseconds())
        return s


class LinkLatencyRepository:
    def __init__(self):
        self._latencies = {}

    def parse_test_packet(self, rpkt):
        src_dpid, dst_dpid = rpkt.src_dpid, rpkt.dst_dpid
        latency = rpkt.receive_ts - rpkt.send_ts
        self._latencies.setdefault(src_dpid, {})[dst_dpid] = latency

    def get_latency_between(self, dpid1, dpid2):
        return self._latencies.setdefault(dpid1, {}).setdefault(
            dpid2, TimeDelta(0.0))

    def __str__(self):
        repr = ''
        for dpid1 in self._latencies:
            for dpid2 in self._latencies[dpid1]:
                repr += "[{0}][{1}] -> {2}\n".format(
                    dpid1, dpid2, self._latencies[dpid1][dpid2].milliseconds())
        return repr


class BandwidthPortMeasurementData:
    def __init__(self, switch_uptime_sec, switch_uptime_nsec, bytes_received,
                 bytes_transferred):
        self._measurement_ts = TimeStamp(switch_uptime_sec +
                                         switch_uptime_nsec * 1e-9)
        self._bytes_through = bytes_received + bytes_transferred

    def __sub__(self, new):
        time_delta = (self._measurement_ts - new._measurement_ts).seconds()
        if time_delta == 0:
            return 0
        return (self._bytes_through - new._bytes_through) / time_delta


class BandwidthPortStatsRepository:
    def __init__(self):
        self._stats = {}
        self._last_measurement_data = {}

    def add_stats(self, dpid, port_no, measurement_data):
        last_measurement_data = self._last_measurement_data.setdefault(
            dpid, {}).setdefault(port_no, None)
        if not last_measurement_data:
            self._last_measurement_data[dpid][port_no] = measurement_data
            return
        self._stats.setdefault(
            dpid, {})[port_no] = measurement_data - last_measurement_data
        self._last_measurement_data[dpid][port_no] = measurement_data

    def get_stats(self, dpid, port_no):
        return self._stats.setdefault(dpid, {}).setdefault(port_no, 0.0)
