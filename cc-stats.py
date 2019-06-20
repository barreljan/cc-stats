#!/usr/bin/python3.5
#
# Created 9-Feb 2019
# @author: bartjan@pc-mania.nl
# https://github.com/barreljan/cc-stats
# 
import requests
import sys
import smtplib
import collections
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

assets = {
    'XRP': 20.57,
    'STRAT': 29.99,
          }

smtpserver = 'smtp.somehost.com'
smtpport = 25
sender = 'noreply@yourdomain.org'
rcpt = 'john@doe.net'


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
allcrypto = collections.OrderedDict(sorted(allcrypto.items()))

msg = MIMEMultipart('alternative')
msg['Subject'] = 'Latest coin prices'
msg['From'] = sender
msg['To'] = rcpt

msgbody = """\
<html>
  <head></head>
  <body style="font-family: arial;font-style:normal;font-size:12px">
    <p>Crypto Summary</p>
    <table style="font-family: arial;font-style:normal;font-size:12px;text-align:left">
      <tr><th style="text-align:left">Coin</th><th style="text-align:left">Qty</th><th style="text-align:left">Price</th><th style="text-align:left">Totals (USD)</th></tr>
"""

totalval = 0
for coin, coinitems in allcrypto.items():
    price = coinitems['quote']['USD']['price']
    assetval = price*assets[coin]
    totalval += assetval
    msgbody += "      <tr><td>{0}</td><td>{1}</td><td>{2:.2f}</td><td>{3:.2f}</td></tr>\n".format(coin, assets[coin], price, assetval)

msgbody += "    </table>\n    <br>\n    <p>Total value: {}<p>\n  </body>\n</html>\n".format(round(totalval, 2))
msg.attach(MIMEText(msgbody, 'html'))

server = smtplib.SMTP(smtpserver, smtpport)
server.sendmail(sender, rcpt, msg.as_string())

