#!/usr/bin/python3.5
#
# Created 9-Feb 2019
# @author: bartjan@pc-mania.nl
# https://github.com/barreljan/cc-stats
# 
import requests
import sys
import smtplib

assets = {
    'BTC': 2,
    'ETH': 1,
    'MNR': 10
          }


def sendmail(msg):
    msg = "Subject: Latest coin prices" + "\n\n" + msg
    server = smtplib.SMTP('smtp.somehost.com', 25)
    server.sendmail('noreply@yourdomain.org', 'john@doe.net', msg)


def cryptodata(assets):
    coins = str()
    for coin, qty in assets.items():
        if coins is "":
            coins += coin
        else:
            coins += ",{}".format(coin)

    link = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={}'.format(coins)
    api_key = 'your Coinmarketcap Pro key'
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }

    try:
        data = requests.get(link, headers=headers)
    except Exception:
        print("Could not connect")
        sys.exit(1)

    jdata = data.json()

    try:
        if jdata['data']:
            return jdata['data']
        elif not jdata['data']:
            raise KeyError('No data returned')
    except KeyError:
        print("API Call went wrong, no usable data returned")
        sys.exit(1)


# Run it
allcrypto = cryptodata(assets)

msg = "{0:8}{1:<8}\t{2}\t{3}\n".format("Coin", "Qty", "Price", "Totals (USD)")

for coin, coinitems in allcrypto.items():
    price = coinitems['quote']['USD']['price']
    assetval = price*assets[coin]
    msg += "{0:8}{1:<8}\t{2:.2f}:\t{3:.2f}\n".format(coin, assets[coin], price, assetval)

sendmail(msg)

