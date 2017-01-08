import os
import time

from sense_hat import SenseHat


def millibars_to_in(p):
    return p * 0.0295300


# use moving average to smooth readings
class TempManager:
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


def main():
    sense = SenseHat()
    temp_manager = TempManager(sense)
    sense.show_message("Starting up", text_colour=[255, 255, 0], back_colour=[0, 0, 255])
    while True:
        # event = sense.stick.wait_for_event()
        # if event.direction == 'push':
        sense.show_message(
            "Temp: {t} Humidity: {h} Pressure {p}".format(
                t=round(temp_manager.get_temp(), 0),
                h=round(sense.get_humidity(), 0),
                p=round(millibars_to_in(sense.get_pressure()), 2)
            )
        )


if __name__ == '__main__':
    main()
