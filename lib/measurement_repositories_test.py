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
import unittest

import time

from lib.measurement_repositories import DatapathResponseTimeRepository, \
    LinkLatencyRepository, BandwidthPortMeasurementData, PlrPortMeasurementData, PortStatsRepository
from lib.packets import ReceivedTestPacket
from lib.time_units import TimeStamp


class TestDatapathResponseTimeRepository(unittest.TestCase):
    def test_get_response_time(self):
        repo = DatapathResponseTimeRepository()

        dpid = 1
        repo.write_send_time(dpid)
        repo.write_receive_time(dpid)

        error = 1.0  # ms
        self.assertLess(repo.get_response_time(dpid).milliseconds(), error)

    def test_write_receive_time__no_such_dpid(self):
        repo = DatapathResponseTimeRepository()

        with self.assertRaisesRegex(
                KeyError, r'dpid 1 is not in datapath time repository'):
            repo.write_receive_time(1)

    def test_get_response_time__no_such_dpid(self):
        repo = DatapathResponseTimeRepository()

        self.assertEqual(repo.get_response_time(1).milliseconds(), 0.0)


class TestLinkLatencyRepository(unittest.TestCase):
    def test_get_latency_between(self):
        repo = LinkLatencyRepository()
        rpkt = ReceivedTestPacket(1, 2, TimeStamp(1586869012.1606))

        self.assertEqual(repo.get_latency_between(1, 2).milliseconds(), 0.0)

        repo.parse_test_packet(rpkt)

        self.assertGreater(repo.get_latency_between(1, 2).milliseconds(), 0.0)

    def test_get_latency_between__no_such_dpid(self):
        repo = LinkLatencyRepository()

        self.assertEqual(repo.get_latency_between(1, 2).milliseconds(), 0.0)


class TestBandwidthPortMeasurementData(unittest.TestCase):
    def test__sub__(self):
        d1 = BandwidthPortMeasurementData(1, 842000000, 13, 16)
        d2 = BandwidthPortMeasurementData(2, 842000000, 20, 21)

        self.assertEqual(d2 - d1, 96.0)


class TestPlrPortMeasurementData(unittest.TestCase):
    def test__sub__(self):
        d1 = PlrPortMeasurementData(40, 60, 10, 5)
        d2 = PlrPortMeasurementData(80, 120, 20, 10)

        self.assertEqual(d2 - d1, 15.0)

        # no packets
        d1 = PlrPortMeasurementData(40, 60, 10, 5)
        d2 = PlrPortMeasurementData(40, 60, 10, 5)

        self.assertEqual(d2 - d1, 0.0)

        # no errors
        d1 = PlrPortMeasurementData(40, 60, 10, 5)
        d2 = PlrPortMeasurementData(80, 120, 10, 5)

        self.assertEqual(d2 - d1, 0.0)


class TestPortStatsRepository(unittest.TestCase):
    def test_add_stats__bandwidth(self):
        repo = PortStatsRepository()
        repo.add_stats(1, 2,
                       BandwidthPortMeasurementData(1, 842000000, 13, 16))
        repo.add_stats(1, 2,
                       BandwidthPortMeasurementData(2, 842000000, 20, 21))

        self.assertEqual(repo.get_stats(1, 2), 96.0)

        repo.add_stats(1, 2,
                       BandwidthPortMeasurementData(3, 842000000, 25, 39))
        self.assertEqual(repo.get_stats(1, 2), 184.0)

    def test_add_stats__plr(self):
        repo = PortStatsRepository()
        repo.add_stats(1, 2, PlrPortMeasurementData(40, 60, 10, 5))
        repo.add_stats(1, 2, PlrPortMeasurementData(80, 120, 20, 10))

        self.assertEqual(repo.get_stats(1, 2), 15.0)

        repo.add_stats(1, 2, PlrPortMeasurementData(100, 200, 20, 10))
        self.assertEqual(repo.get_stats(1, 2), 0.0)

    def test_add_stats__empty_stats(self):
        repo = PortStatsRepository()
        self.assertEqual(repo.get_stats(1, 2), 0.0)

        repo.add_stats(1, 2,
                       BandwidthPortMeasurementData(1, 842000000, 13, 16))
        self.assertEqual(repo.get_stats(1, 2), 0.0)


if __name__ == '__main__':
    unittest.main()