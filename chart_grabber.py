import os
import time
import threading


class Thread(threading.Thread):
    def __init__(self, time_range):
        threading.Thread.__init__(self, target=grab_chart, args=(time_range,))
        self.start()


def grab_chart(time_range):
    sleeping_ranges = {"1d": 15 * 60,       # Updates every 15 minutes
                       "1w": 60 * 60,       # Updates every hour
                       "1m": 4 * 60 * 60,   # Updates every 4 hours
                       "3m": 11 * 60 * 60}  # Updates every 11 hours
    while True:
        with lock:  # Using lock to be sure that 2 chromium threads start at the same time because they both create a screenshot.png file
            os.system('chromium-browser --headless --disable-gpu --screenshot "https://bitscreener.com/coins/garlicoin?timeframe={}&chart_type=candle&chart_unit=usd&is_global=true" --window-size=1920,1080'.format(time_range))
            os.system('mv screenshot.png screenshot_{}.png'.format(time_range))
            os.system('convert screenshot_{0}.png -crop 1213x510+343+380 {0}.png'.format(time_range))
        time.sleep(sleeping_ranges[time_range])


lock = threading.Lock()

# Using threads so that time.sleep() doesn't stop all other updates
for time_range in ["1d", "1w", "1m", "3m"]:
    Thread(time_range)
