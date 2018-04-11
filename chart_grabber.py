import os
import time

def grab_chart():
    while True:
        os.system('chromium-browser --headless --disable-gpu --screenshot "https://bitscreener.com/coins/garlicoin?timeframe=1d&chart_type=candle&chart_unit=usd&is_global=true" --window-size=1920,1080')
        os.system('mv screenshot.png screenshot1.png')
        os.system('chromium-browser --headless --disable-gpu --screenshot "https://bitscreener.com/coins/garlicoin?timeframe=1w&chart_type=candle&chart_unit=usd&is_global=true" --window-size=1920,1080')
        os.system('mv screenshot.png screenshot2.png')
        os.system('chromium-browser --headless --disable-gpu --screenshot "https://bitscreener.com/coins/garlicoin?timeframe=1m&chart_type=candle&chart_unit=usd&is_global=true" --window-size=1920,1080')
        os.system('mv screenshot.png screenshot3.png')
        os.system('chromium-browser --headless --disable-gpu --screenshot "https://bitscreener.com/coins/garlicoin?timeframe=3m&chart_type=candle&chart_unit=usd&is_global=true" --window-size=1920,1080')
        os.system('mv screenshot.png screenshot4.png')
        os.system('convert screenshot1.png -crop 1213x510+343+380 1d.png')
        os.system('convert screenshot2.png -crop 1213x510+343+380 1w.png')
        os.system('convert screenshot3.png -crop 1213x510+343+380 1m.png')
        os.system('convert screenshot4.png -crop 1213x510+343+380 3m.png')
        time.sleep(300)

grab_chart()
