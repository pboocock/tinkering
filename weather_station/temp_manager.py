import os


class TempManager:
    """
    Manages a moving average of temperature readings from the Sense HAT.

    The Sense HAT's temperature readings aren't accurate on their own because
    of the CPU temp. This takes a reading of the CPU temp to help normalize the
    temperature, and then calculates a moving average so that the readings
    are smoothed.
    """
    def __init__(self, sense, n=3):
        self.sense = sense
        self.temp_list = []
        self.n = n

    @staticmethod
    def cpu_temp():
        return float(
            os.popen('vcgencmd measure_temp').readline().replace(
                "temp=", ""
            ).replace("'C\n", "")
        )

    @staticmethod
    def c_to_f(t):
        return (t * 1.8) + 32

    def _smooth(self, t):
        self.temp_list.insert(0, t)
        if len(self.temp_list) > self.n:
            self.temp_list.pop()
        return sum(self.temp_list) / len(self.temp_list)

    def get_temp(self, c=False):
        t = (
                self.sense.get_temperature_from_humidity() +
                self.sense.get_temperature_from_pressure()
            ) / 2
        t_corr = t - (
            (self.cpu_temp() - t) / 1.5
        )
        if c:
            return self._smooth(t_corr)
        else:
            return self.c_to_f(self._smooth(t_corr))


