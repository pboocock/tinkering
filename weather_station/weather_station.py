import datetime
import signal
import sys
import traceback
from urllib import urlencode
import urllib2

from sense_hat import SenseHat

from temp_manager import TempManager
from config import Constants


# Create images for upload success and failure
b = [0, 0, 255]  # blue
r = [255, 0, 0]  # red
e = [0, 0, 0]  # empty
w = [255, 255, 255] # white
dg = [0, 100, 0] # dark green

blue_check = [
    b, b, b, b, b, b, b, b,
    b, b, b, b, b, b, b, w,
    b, b, b, b, b, b, w, w,
    b, b, b, b, b, w, w, b,
    w, b, b, b, w, w, b, b,
    w, w, b, w, w, b, b, b,
    b, w, w, w, b, b, b, b,
    b, b, w, b, b, b, b, b,
]
red_x = [
    w, r, r, r, r, r, r, w,
    r, w, r, r, r, r, w, r,
    r, r, w, r, r, w, r, r,
    r, r, r, w, w, r, r, r,
    r, r, r, w, w, r, r, r,
    r, r, w, r, r, w, r, r,
    r, w, r, r, r, r, w, r,
    w, r, r, r, r, r, r, w,
]


def millibars_to_in(p):
    return p * 0.0295300


class Weather:
    def __init__(self):
        self.sense = SenseHat()
        self.sense.low_light = True
        self.temp_manager = TempManager(self.sense)

        self.current_minute = datetime.datetime.now().minute
        self.last_minute = datetime.datetime.now().minute
        self.current_second = datetime.datetime.now().second
        self.last_second = datetime.datetime.now().second

        self.sense.clear()
        self.sense.show_message("Starting up", text_colour=w, back_colour=b)
        self.sense.clear()

    def vanity_temp(self):
        self.sense.show_message(
            "Temp: {t} Humidity: {h} Pressure {p}".format(
                t=round(self.temp_manager.get_temp(), 0),
                h=round(self.sense.get_humidity(), 0),
                p=round(millibars_to_in(self.sense.get_pressure()), 2)
            )
        )

    def _upload(self):
        self.sense.show_message("Uploading", text_colour=w, back_colour=dg)
        weather_data = {
            "action": "updateraw",
            "ID": Constants.STATION_ID,
            "PASSWORD": Constants.STATION_PW,
            "dateutc": "now",
            "tempf": str(self.temp_manager.get_temp()),
            "humidity": str(self.sense.get_humidity()),
            "baromin": str(millibars_to_in(self.sense.get_pressure())),
        }
        upload_url = Constants.WU_URL + "?" + urlencode(weather_data)
        response = urllib2.urlopen(upload_url)
        html = response.read()
        if 'success' in html:
            self.sense.set_pixels(blue_check)
        else:
            print(html)
            self.sense.set_pixels(red_x)
        response.close()

    def _measure(self):
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
            self._upload()

        self.last_second = self.current_second
        self.last_minute = self.current_minute

    def _sigterm_handler(self, signal, frame):
        self.sense.show_message("SIGTERM", text_colour=w, back_colour=r)
        self.sense.clear()
        sys.exit(0)

    def run(self):
        while True:
            try:
                signal.signal(signal.SIGTERM, self._sigterm_handler)
                self._measure()
            except KeyboardInterrupt:
                self.sense.show_message("Bye", text_colour=w, back_colour=r)
                self.sense.clear()
                print("\nExiting application\n")
                sys.exit(0)


if __name__ == '__main__':
    try:
        weather_manager = Weather()
        weather_manager.run()
    except:
        print traceback.format_exc()

