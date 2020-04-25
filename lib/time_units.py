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

class TimeDelta:
    def __init__(self, delta_in_seconds):
        self._delta_in_seconds = delta_in_seconds

    def milliseconds(self, ndigits=3):
        return round(self._delta_in_seconds * 1000, ndigits)

    def seconds(self, ndigits=3):
        return round(self._delta_in_seconds, ndigits)

    def __str__(self):
        return str(self._delta_in_seconds)


class TimeStamp:
    def __init__(self, seconds):
        if isinstance(seconds, float):
            self._seconds = TimeStamp._normalize(seconds)
            return

        if isinstance(seconds, str):
            self._seconds = TimeStamp._normalize(float(seconds))
            return
        
        raise ValueError('seconds must be float or string')

    @staticmethod
    def _normalize(t):
        k = 10000
        return int(t * k) / k

    def __str__(self):
        return str(self._seconds)

    def __sub__(self, other):
        return TimeDelta(self._seconds - other._seconds)