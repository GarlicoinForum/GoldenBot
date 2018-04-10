import os
import time

def grab_chart():
    while True:
        os.system('chromium --headless --disable-gpu --screenshot "https://bitscreener.com/coins/garlicoin?timeframe=1d&chart_type=candle&chart_unit=usd&is_global=true" --window-size=1920,1080')
        os.system('convert screenshot.png -crop 1213x510+343+380 out.png')
        time.sleep(300)

grab_chart()
