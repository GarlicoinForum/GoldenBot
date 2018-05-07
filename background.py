import os
import time
import threading
import requests
import sqlite3

from bs4 import BeautifulSoup


class GraphThread(threading.Thread):
    def __init__(self, time_range):
        threading.Thread.__init__(self, target=grab_chart, args=(time_range,))
        self.start()

class ExchangeThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, target=grab_exchanges)
        self.start()


def grab_chart(time_range):
    sleeping_ranges = {"1d": 5 * 60,       # Updates every 5 minutes
                       "1w": 60 * 60,       # Updates every hour
                       "1m": 4 * 60 * 60,   # Updates every 4 hours
                       "3m": 11 * 60 * 60}  # Updates every 11 hours
    while True:
        with lock:  # Using lock to be sure that 2 chromium threads start at the same time because they both create a screenshot.png file
            os.system('chromium-browser --headless --disable-gpu --screenshot "https://bitscreener.com/coins/garlicoin?timeframe={}&chart_type=candle&chart_unit=usd&is_global=true" --window-size=1920,1080'.format(time_range))
            os.system('mv screenshot.png screenshot_{}.png'.format(time_range))
            os.system('convert screenshot_{0}.png -crop 1213x510+343+380 {0}.png'.format(time_range))
        time.sleep(sleeping_ranges[time_range])


def grab_exchanges():
    next_cleanup = int(time.time()) + 24 * 60 * 60
    while True:
        # Get exchanges' prices and store them in a database every minute
        d = {}

        try:
            ex = requests.get("https://coinmarketcap.com/currencies/garlicoin/#markets", timeout=10)
        except requests.Timeout:
            ex = None

        if ex:
            timestamp = int(time.time())
            soup = BeautifulSoup(ex.text, 'html.parser')
            table = soup.find('table', attrs={'id': 'markets-table'})
            table_body = table.find('tbody')

            rows = table_body.find_all('tr')
            for row in rows:
                p = row.find('span', class_="price")
                m = row.find_all("a")

                price = float(p.text.strip().replace("$", ""))
                name = "{0}_{1}".format(m[0].text, m[1].text)   # ie: name = "Trade Satoshi_GRLC/BTC"

                d[name] = price

            sql = "INSERT INTO `cmc_exchanges` "\
                  "(`timestamp`, `Trade Satoshi_GRLC/BTC`, `CoinFalcon_GRLC/BTC`, `CryptoBridge_GRLC/BTC`, `Nanex_GRLC/NANO`, " \
                  "`Trade Satoshi_GRLC/LTC`, `Trade Satoshi_GRLC/BCH`, `Trade Satoshi_GRLC/DOGE`, `Trade Satoshi_GRLC/USDT`, `CoinFalcon_GRLC/ETH`) " \
                  "VALUES " \
                  "('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')"
            sql = sql.format(timestamp, d["Trade Satoshi_GRLC/BTC"], d["CoinFalcon_GRLC/BTC"], d["CryptoBridge_GRLC/BTC"],
                             d["Nanex_GRLC/NANO"], d["Trade Satoshi_GRLC/LTC"], d["Trade Satoshi_GRLC/BCH"],
                             d["Trade Satoshi_GRLC/DOGE"],d["Trade Satoshi_GRLC/USDT"], d["CoinFalcon_GRLC/ETH"])

            with sqlite3.connect("db.sqlite3") as db:
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()

        # Once daily clean the old data (older than 7 days)
        if time.time() >= next_cleanup:
            timestamp = int(time.time())
            limit_timestamp = timestamp - 7 * 24 * 60 * 60
            sql = "DELETE FROM `cmc_exchanges` WHERE `timestamp` <= {}".format(limit_timestamp)

            with sqlite3.connect("db.sqlite3") as db:
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()
            next_cleanup = timestamp + 24 * 60 * 60

        # Sleep for a minute
        time.sleep(60)


lock = threading.Lock()

# Using threads so that time.sleep() doesn't stop all other updates
ExchangeThread()
for time_range in ["1d", "1w", "1m", "3m"]:
    GraphThread(time_range)
