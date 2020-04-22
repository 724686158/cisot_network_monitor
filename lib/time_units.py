
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