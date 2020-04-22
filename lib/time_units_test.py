import unittest

from lib.time_units import TimeStamp, TimeDelta


class TestTimeStamp(unittest.TestCase):
    def test__init__(self):
        # int arg
        with self.assertRaises(ValueError):
            TimeStamp(3)

        # ok
        TimeStamp(3.21)
        TimeStamp('3.21')

    def test__str__(self):
        ts1 = TimeStamp(3.21)
        self.assertEqual(str(ts1), '3.21')

        ts2 = TimeStamp('12.456')
        self.assertEqual(str(ts2), '12.456')

    def test__sub__(self):
        ts1 = TimeStamp(10.51)
        ts2 = TimeStamp(8.49)
        delta = ts1 - ts2

        self.assertEqual(delta.milliseconds(), 2020.0)


class TestTimeDelta(unittest.TestCase):
    def test_milliseconds(self):
        td = TimeDelta(2.1234567)
        self.assertEqual(td.milliseconds(), 2123.457)
        self.assertEqual(td.milliseconds(1), 2123.5)
        self.assertEqual(td.milliseconds(2), 2123.46)
        self.assertEqual(td.milliseconds(3), 2123.457)
        self.assertEqual(td.milliseconds(4), 2123.4567)
        self.assertEqual(td.milliseconds(5), 2123.45670)

    def test_seconds(self):
        td = TimeDelta(2.1234567)
        self.assertEqual(td.seconds(), 2.123)
        self.assertEqual(td.seconds(1), 2.1)
        self.assertEqual(td.seconds(2), 2.12)
        self.assertEqual(td.seconds(3), 2.123)
        self.assertEqual(td.seconds(4), 2.1235)
        self.assertEqual(td.seconds(5), 2.12346)


if __name__ == '__main__':
    unittest.main()
