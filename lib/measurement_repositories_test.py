import unittest

import time

from lib.measurement_repositories import DatapathResponseTimeRepository, LinkLatencyRepository
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


if __name__ == '__main__':
    unittest.main()