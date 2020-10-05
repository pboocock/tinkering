import serial
import time
import datetime as dt

import adafruit_pm25
import matplotlib.pyplot as plt
import matplotlib.animation as animation


reset_pin = None
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)
pm25 = adafruit_pm25.PM25_UART(uart, reset_pin)


# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []


# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    # Read temperature (Celsius) from TMP102
    aqdata = pm25.read()


    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S'))
    ys.append(aqdata["pm25 standard"])

    if len(xs) > 500:
        xs.pop(0)

    if len(ys) > 500:
        ys.pop(0)

    # Limit x and y lists to 20 items
    xs = xs[-240:]
    ys = ys[-240:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('PM2.5 Readings')
    plt.ylabel('PM2.5')

try:
    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=5000)
    plt.show()
    print("did it")
except:
    print("error")

