import unittest

from lib.packets import TestPacket, ReceivedTestPacket
from lib.time_units import TimeStamp


class TestTestPacket(unittest.TestCase):
    def test__init__(self):
        pkt = TestPacket(12)

        self.assertRegex(str(pkt),
                         r'\d+\.\d{4}:12')  # for example 1586869012.1606:12

    def test_from_string(self):
        pkt1 = TestPacket.from_string('1586869012.1606:12')
        self.assertEqual(str(pkt1), '1586869012.1606:12')

        pkt2 = TestPacket.from_string('1586869012.1606:12\x00\x00')
        self.assertEqual(str(pkt2), '1586869012.1606:12')


class TestReceivedTestPacket(unittest.TestCase):
    def test__init__(self):
        rpkt = ReceivedTestPacket(1, 2, TimeStamp(1586959016.8374))
        self.assertIsInstance(rpkt.receive_ts, TimeStamp)


if __name__ == '__main__':
    unittest.main()
