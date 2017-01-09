import datetime
import os
import sys
from urllib import urlencode
import urllib2

from sense_hat import SenseHat

from config import Constants



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


class Weather:
    def __init__(self):
        self.sense = SenseHat()
        self.temp_manager = TempManager(self.sense)

        self.current_minute = datetime.datetime.now().minute
        self.last_minute = datetime.datetime.now().minute
        self.current_second = datetime.datetime.now().second
        self.last_second = datetime.datetime.now().second

        self.sense.clear()
        self.sense.show_message(
            "Starting up",
            text_colour=[255, 255, 0],
            back_colour=[0, 0, 255]
        )

    def vanity_temp(self):
        self.sense.show_message(
            "Temp: {t} Humidity: {h} Pressure {p}".format(
                t=round(self.temp_manager.get_temp(), 0),
                h=round(self.sense.get_humidity(), 0),
                p=round(millibars_to_in(self.sense.get_pressure()), 2)
            )
        )

    def _upload(self):
        weather_data = {
            "action": "updateraw",
            "ID": Constants.STATION_ID,
            "PASSWORD": Constants.STATION_PW,
            "dateutc": "now",
            "tempf": str(self.temp_manager.get_temp()),
            "humidity": str(self.sense.get_humidity()),
            "baromin": str(millibars_to_in(self.sense.get_pressure())),
        }
        try:
            upload_url = Constants.WU_URL + "?" + urlencode(weather_data)
            with urllib2.urlopen(upload_url) as response:
                html = response.read()
                print("Server response:", html)
        except:
            print("Exception:", sys.exc_info()[0])

    def _measure_and_upload(self):
        self.current_second = datetime.datetime.now().second
        self.current_minute = datetime.datetime.now().minute

        if len(self.sense.stick.get_events()) > 0:
            self.vanity_temp()

        if (
            self.current_second % Constants.MEASUREMENT_INTERVAL == 0 and
            self.current_second != self.last_second
        ):
            self.temp_manager.get_temp()

        if (
            self.current_minute % Constants.UPLOAD_INTERVAL == 0 and
            self.current_minute != self.last_minute and
            Constants.WEATHER_UPLOAD
        ):
            self.sense.show_message(
                "Uploading to WUnderground",
                text_colour=[255, 255, 0],
                back_colour=[0, 0, 255]
            )
            self._upload()

        self.last_second = self.current_second
        self.last_minute = self.current_minute

    def run(self):
        while True:
            try:
                self._measure_and_upload()
            except KeyboardInterrupt:
                self.sense.show_message(
                    "Bye :(",
                    text_colour=[255, 255, 255],
                    back_colour=[255, 0, 0]
                )
                self.sense.clear()
                print("\nExiting application\n")


def main():
    weather_manager = Weather()
    weather_manager.run()


if __name__ == '__main__':
    try:
        main()
    except:
        print("Exception:", sys.exc_info()[0])

