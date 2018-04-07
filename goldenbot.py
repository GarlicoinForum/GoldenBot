import discord
import requests
import asyncio
import configparser


conf = configparser.RawConfigParser()
conf.read("config.txt")

BOT_TOKEN = conf.get('goldenbot_conf', 'BOT_TOKEN')


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

            table = "```\n" \
                    "    1 ₲ = 1 ₲    |      USD      |      EUR      |      GBP      |      AUD\n" \
                    "-----------------|---------------|---------------|---------------|---------------\n" \
                    "  GRLC --> FIAT  |  $ {0}  |  {1} €  |  £ {2}  |  $ {3}\n" \
                    "-----------------|---------------|---------------|---------------|---------------\n" \
                    "  FIAT --> GRLC  |  ₲ {4}  |  ₲ {5}  |  ₲ {6}  |  ₲ {7}\n" \
                    "```".format(fstr(9, fiats[0]), fstr(9, fiats[1]), fstr(9, fiats[2]), fstr(9, fiats[3]),
                                 fstr(9, 1/fiats[0]), fstr(9, 1/fiats[1]), fstr(9, 1/fiats[2]), fstr(9, 1/fiats[3]))

            await client.send_message(message.channel, table)
        else:
            # Timeout
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")

    if message.content.startswith("!crypto"):
        # Get the GRLC price in BTC, ETH, LTC, NANO
        tmp = await client.send_message(message.channel, "Acquiring crypto rates from CoinMarketCap...")
        cryptos = get_cryptos()

        if cryptos:
            await client.edit_message(tmp, "Acquiring crypto rates from CoinMarketCap... Done!")

            table = "```\n" \
                    "    1 ₲ = 1 ₲    |      BTC      |      ETH      |      LTC      |     NANO\n" \
                    "-----------------|---------------|---------------|---------------|---------------\n" \
                    "  GRLC --> COIN  | ฿ {0} | Ξ {1} | Ł {2} | η {3}\n" \
                    "-----------------|---------------|---------------|---------------|---------------\n" \
                    "  COIN --> GRLC  | ₲ {4} | ₲ {5} | ₲ {6} | ₲ {7}\n" \
                    "```".format(fstr(11, cryptos[0]), fstr(11, cryptos[1]), fstr(11, cryptos[2]), fstr(11, cryptos[3]),
                                 fstr(11, 1/cryptos[0]), fstr(11, 1/cryptos[1]), fstr(11, 1/cryptos[2]), fstr(11, 1/cryptos[3]))

            await client.send_message(message.channel, table)
        else:
            # Timeout
            await client.edit_message(tmp, "Error : Couldn't reach CoinMarketCap (timeout)")

    if message.content.startswith("!gold"):
        # TODO: Get details for Garlicoin (graph last 24h ?)
        pass

    if message.content.startswith("!exchanges"):
        # TODO: Lists the exchanges rates for GRLC
        pass


client.run(BOT_TOKEN)
