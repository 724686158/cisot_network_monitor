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
