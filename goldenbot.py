import discord
import requests
import asyncio
import configparser
import os

from tabulate import tabulate
from bs4 import BeautifulSoup


conf = configparser.RawConfigParser()
conf.read("config.txt")

BOT_TOKEN = conf.get('goldenbot_conf', 'BOT_TOKEN')


async def convert_3(client, message, msg):
    # No rate given, get it from CoinMarketCap
    amount = float(msg[0].replace(",", ".")) # In case someone sends 10,2 GRLC instead of 10.2
    curr1 = msg[1]
    curr2 = msg[2]

    # FIAT -> FIAT
    if is_fiat(curr1) and is_fiat(curr2):
        # Get the exchange rate (using BTC as a middle value)
        fiat1_btc = await get_rate_crypto(client, message, "BTC", curr1, verbose=False)
        fiat2_btc = await get_rate_crypto(client, message, "BTC", curr2)

        if fiat1_btc and fiat2_btc:
            rate = fiat1_btc / fiat2_btc
            conv_amount = amount * rate
            await client.send_message(message.channel, "```{0} {1} = {2} {3:.6f} (rate: {4:.6f})```".format(curr1, msg[0], curr2, conv_amount, rate))

    # CRYPTO -> CRYPTO
    elif is_crypto(curr1) and is_crypto(curr2):
        # Get each crypto rate in BTC then calculate the rate
        crypto1_btc = await get_rate_crypto(client, message, curr1, "BTC", verbose=False)
        crypto2_btc = await get_rate_crypto(client, message, curr2, "BTC")

        if crypto1_btc and crypto2_btc:
            rate = crypto1_btc / crypto2_btc
            conv_amount = amount * rate
            await client.send_message(message.channel, "```{0} {1} = {2} {3:.6f} (rate: {4:.6f})```".format(curr1, msg[0], curr2, conv_amount, rate))

    # FIAT -> CRYPTO or CRYPTO -> FIAT
    elif is_crypto(curr1) or is_fiat(curr1) and is_crypto(curr2) or is_fiat(curr2):
        # Find the FIAT and ask CoinMarketCap for the crypto using the FIAT
        if is_crypto(curr1):
            fiat = curr2
            crypto = curr1
        else:
            fiat = curr1
            crypto = curr2

        rate = await get_rate_crypto(client, message, crypto, fiat)
        if rate:
            if fiat == curr1:
                conv_amount = amount / rate
                await client.send_message(message.channel, "```{0} {1} = {2} {3:.6f} (rate: {4:.6f})```".format(curr1, msg[0], curr2, conv_amount, 1/rate))
            else:
                conv_amount = amount * rate
                await client.send_message(message.channel, "```{0} {1} = {2} {3:.6f} (rate: {4:.6f})```".format(curr1, msg[0], curr2, conv_amount, rate))

    else:
        # One or both currencies aren't known
        await client.send_message(message.channel, "One (or both) currency entered is not supported.")


async def convert_4(client, message, msg):
    try:
        float(msg[3].replace(",", "."))
    except ValueError:
        # The rate isn't a numeric value, so we use CoinMarketCap instead
        await convert_3(client, message, msg)
    else:
        # Make the calculation using the given rate
        amount = float(msg[0].replace(",", ".")) # In case someone sends 10,2 GRLC instead of 10.2
        curr1 = msg[1]
        curr2 = msg[2]
        rate = float(msg[3].replace(",", ".")) # In case someone sends 0,02 instead of 0.02

        conv_amount = amount * rate
        await client.send_message(message.channel, "```{0} {1} = {2} {3:.6f} (rate: {4:.6f})```".format(curr1, msg[0], curr2, conv_amount, rate))


def is_fiat(name):
    # TODO: put the tuple in the config file
    if name in ("USD", "EUR", "GBP", "AUD"):
        return True
    else:
        return False


def is_crypto(name):
    # TODO: put the tuple in the config file
    if name in ("GRLC", "BTC", "ETH", "LTC", "NANO"):
        return True
    else:
        return False


async def get_rate_crypto(client, message, crypto, fiat="USD", verbose=True):
    # TODO: put the dict in the config file
    # Somehow https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=BTC doesn't give an error!
    crypto_name = {"GRLC": "garlicoin",
                   "BTC": "bitcoin",
                   "ETH": "ethereum",
                   "LTC": "litecoin",
                   "NANO": "nano"}
    try:
        if verbose:
            tmp = await client.send_message(message.channel, "Acquiring rates from CoinMarketCap...")
        datas = requests.get("https://api.coinmarketcap.com/v1/ticker/{0}/?convert={1}".format(crypto_name[crypto], fiat), timeout=10)
        if verbose:
            await client.edit_message(tmp, "Acquiring rates from CoinMarketCap... Done!")
    except requests.Timeout:
        if verbose:
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")
        return None

    datas = datas.json()[0]

    return float(datas["price_{}".format(fiat.lower())])


def get_fiats():
    try:
        usd_eur = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/?convert=EUR", timeout=10)
        gbp = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/?convert=GBP", timeout=10)
        aud = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/?convert=AUD", timeout=10)
    except requests.Timeout:
        return None

    usd_eur = usd_eur.json()[0]
    gbp = gbp.json()[0]
    aud = aud.json()[0]

    return float(usd_eur["price_usd"]), float(usd_eur["price_eur"]), float(gbp["price_gbp"]), float(aud["price_aud"])


def get_cryptos():
    try:
        grlc_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/", timeout=10)
        eth_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/ethereum/", timeout=10)
        ltc_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/litecoin/", timeout=10)
        nano_btc = requests.get("https://api.coinmarketcap.com/v1/ticker/nano/", timeout=10)
    except requests.Timeout:
        return None

    grlc_btc = grlc_btc.json()[0]
    eth_btc = eth_btc.json()[0]
    ltc_btc = ltc_btc.json()[0]
    nano_btc = nano_btc.json()[0]

    grlc_btc = float(grlc_btc["price_btc"])
    grlc_eth = grlc_btc / float(eth_btc["price_btc"])
    grlc_ltc = grlc_btc / float(ltc_btc["price_btc"])
    grlc_nano = grlc_btc / float(nano_btc["price_btc"])

    return grlc_btc, grlc_eth, grlc_ltc, grlc_nano


def fstr(max_size, value):
    # Get the len of the integer part
    i_part = len(str(int(value)))
    f_part = max_size - i_part - 1

    formater = "{" + ":.{}f".format(f_part) + "}"

    return formater.format(value)


client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as {} <@{}>'.format(client.user.name, client.user.id))
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith("!fiat"):
        # Get the GRLC price in USD, EUR, GBP & AUD
        tmp = await client.send_message(message.channel, "Acquiring fiat rates from CoinMarketCap...")
        fiats = get_fiats()
        if fiats:
            await client.edit_message(tmp, "Acquiring fiat rates from CoinMarketCap... Done!")
            symbols = [("USD", "$"), ("EUR", "€"), ("GBP", "£"), ("AUD", "$")]
            data = [[symbols[i][0], "{0} {1}".format(symbols[i][1],fstr(9, fiats[i])), "₲ {}".format(fstr(9, 1/fiats[i]))] for i in range(4)]
            table = tabulate(data, headers=["", "Garlicoin", "Fiat"])

            await client.send_message(message.channel, "```{}```".format(table))
        else:
            # Timeout
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")


    if message.content.startswith("!crypto"):
        # Get the GRLC price in BTC, ETH, LTC, NANO
        tmp = await client.send_message(message.channel, "Acquiring crypto rates from CoinMarketCap...")
        cryptos = get_cryptos()

        if cryptos:
            await client.edit_message(tmp, "Acquiring crypto rates from CoinMarketCap... Done!")
            symbols = [("BTC", "฿"), ("ETH", "Ξ"), ("LTC", "Ł"), ("NANO", "η")]
            data = [[symbols[i][0], "{0} {1}".format(symbols[i][1],fstr(10, cryptos[i])), "₲ {}".format(fstr(10, 1/cryptos[i]))] for i in range(4)]
            table = tabulate(data, headers=["", "Garlicoin", "Crypto"])

            await client.send_message(message.channel, "```{}```".format(table))
        else:
            # Timeout
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")


    if message.content.startswith("!graph"):
        msg = message.content.replace("!graph ", "").split(" ")
        if os.path.isfile("{}.png".format(msg[0])):
            await client.send_file(message.channel,"{}.png".format(msg[0]))
        else:
            await client.send_message(message.channel, "Error: Unable to grab chart.")

    if message.content.startswith("!conv"):
        # !conv [amount] [currency1] [currency2] [rate (optional)] --> [currency1] [amount] = [currency2] [converted amount] ([rate])
        msg = message.content.replace("!conv ", "").split(" ")

        try:
            # Check if the amount sent by the user is a number
            float(msg[0].replace(",", "."))
        except ValueError:
            # The amount isn't a numeric value
            await client.send_message(message.channel, "Error: Unable to get the amount to convert.")

        else:
            # Show a custom message if currency1 == currency2
            if msg[1] == msg[2]:
                await client.send_message(message.channel, "```{0} {1} = {0} {1}```".format(msg[1], msg[0]))

            # Check if there is a rate
            elif len(msg) == 3:
                await convert_3(client, message, msg)

            elif len(msg) == 4:
                await convert_4(client, message, msg)

            else:
                # Not enough parameters sent
                await client.send_message(message.channel, "Not enough parameters given : `!conv [amount] [currency1] [currency2] [rate (optional)]`")


    if message.content.startswith("!exchange"):
        data = []
        tmp = await client.send_message(message.channel, "Acquiring exchange rates from CoinMarketCap...")
        try:
            ex = requests.get("https://coinmarketcap.com/currencies/garlicoin/#markets", timeout=10)
        except requests.Timeout:
            ex = None

        if ex:
            await client.edit_message(tmp, "Acquiring exchange rates from CoinMarketCap... Done!")
            soup = BeautifulSoup(ex.text, 'html.parser')
            table = soup.find('table', attrs={'id': 'markets-table'})
            table_body = table.find('tbody')

            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])

            data = [[x[0], x[1], x[2], x[3], x[4]] for x in data] # Remove columns
            table = tabulate(data, headers=["No", "Exchange", "Pair", "Volume", "Price"])
            await client.send_message(message.channel, "```{}```".format(table))
        else:
            # Timeout
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")

    if message.content.startswith("!network"):
        tmp = await client.send_message(message.channel, "Acquiring data from CMC/garli.co.in...")
        try:
            price = requests.get("https://api.coinmarketcap.com/v1/ticker/garlicoin/", timeout=10)
            diff = requests.get("https://garli.co.in/api/getdifficulty", timeout=10)
            blocks = requests.get("https://garli.co.in/api/getblockcount", timeout=10)
            hrate = requests.get("https://garli.co.in/api/getnetworkhashps", timeout=10)
            supply = requests.get("https://garli.co.in/ext/getmoneysupply", timeout=10)
        except requests.Timeout:
            price = None

        if price is not None:
            await client.edit_message(tmp, "Acquiring data from CMC/garli.co.in... Done!")
            price = round(float(price.json()[0]["price_usd"]),6)
            diff = round(diff.json(),2)
            blocks = blocks.json()
            hrate = round(float(hrate.json())/10e8,2) #Convert to GH/s
            supply = round(supply.json())

            table = tabulate([[price,diff,blocks,hrate,supply]], headers=["Price (USD)","Difficulty","Block","Hashrate (GH/s)","Supply"])
            await client.send_message(message.channel, "```{}```".format(table))
        else:
            await client.edit_message(tmp, "Error : Couldn't reach CMC/garli.co.in (timeout)")

    if message.content.startswith("!help"):
        help_text = "<@{}>, I'm GoldenBot, I'm here to assist you during your trades!\n\n```" \
                    "!fiat     : Show the current price of GRLC in USD, EUR, GBP and AUD\n" \
                    "!crypto   : Show the current price of GRLC in BTC, ETH, LTC and NANO\n" \
                    "!exchange : Show the current rates in each exchanges\n" \
                    "!conv     : Convert an amount of one currency to another one using optionally the given rate\n" \
                    "            Usage: !conv [amount] [cur1] [cur2] [rate (optional)]\n" \
                    "            [cur1] and [cur2] can be : USD, EUR, GBP, AUD, GRLC, BTC, ETH, LTC or NANO\n" \
                    "!help     : Show a list of commands and what they do```".format(message.author.id)
        await client.send_message(message.channel, help_text)


client.run(BOT_TOKEN)
