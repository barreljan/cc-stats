#!/usr/local/bin/python3.7
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

# Assets dict: TOKEN as Key, int as Value
# TOKEN must be the official token code used on the CMC website
assets = {
    'XRP': 20.57,
    'STRAT': 29.99
          }

to_mail = False
smtpserver = 'smtp.somehost.com'
smtpport = 25
sender = 'noreply@yourdomain.org'
rcpt = 'john@doe.net'


def argparse():
    global to_mail

    if len(sys.argv) >= 2:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print("Syntax is {0} -m or --mail\nDefault output is to screen\n".format(sys.argv[0]))
            sys.exit()
        elif sys.argv[1] == '-m' or sys.argv[1] == '--mail':
            to_mail = True


def cryptodata(_assets):
    # Generate a string of coins pieced together for the API call
    coins = str()
    for coin, qty in _assets.items():
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

    # Do the call
    try:
        data = requests.get(link, headers=headers)
    except Exception:
        print("Could not connect")
        sys.exit(1)

    # Return the data
    try:
        jdata = data.json()
        if jdata['data']:
            return jdata['data']
        elif not jdata['data']:
            raise KeyError('No data returned')
    except KeyError:
        print("API Call went wrong, no usable data returned")
        sys.exit(1)


def process_data():
    global to_mail

    # Retrieve coin info for the available assets
    allcrypto = cryptodata(assets)
    allcrypto = collections.OrderedDict(sorted(allcrypto.items()))

    # Generate the output
    emailmsg = MIMEMultipart('alternative')
    emailmsg['Subject'] = 'Latest coin prices'
    emailmsg['From'] = sender
    emailmsg['To'] = rcpt
    emailmsgbody = "<html>\n\t<head></head>\n\t<body style=\"font-family: arial;font-style:normal;font-size:12px\">\n"
    emailmsgbody += "\t\t<p>Crypto Summary</p>\n\t\t<table style=\"font-family: arial;font-style:normal;font-size:12px;"
    emailmsgbody += "text-align:left\">\n\t\t\t<tr><th style=\"text-align:left\">Coin</th><th "
    emailmsgbody += "text-align:left\">Qty</th><th style=\"text-align:left\">Price</th><th style=\"text-align:left\">"
    emailmsgbody += "(USD)</th></tr>\n"
    screenmsg = "{}\n\nCoin\t\tQty\t\tPrice\t\tTotal (USD)".format(emailmsg['Subject'])

    totalval = 0
    for coin, coinitems in allcrypto.items():
        price = coinitems['quote']['USD']['price']
        assetval = price*assets[coin]
        totalval += assetval
        emailmsgbody += "\t\t\t<tr><td>{0}</td><td>{1}</td><td>{2:.2f}</td><td>{3:.2f}</td></tr>\n"\
            .format(coin, assets[coin], price, assetval)
        screenmsg += "{0}\t\t{1}\t\t{2:.2f}\t\t{3:.2f}\n".format(coin, assets[coin], price, assetval)

    emailmsgbody += "\t\t</table>\n\t\t<br>\n\t\t<p>Total value: {}<p>\n\t</body>\n</html>\n".format(round(totalval, 2))
    emailmsg.attach(MIMEText(emailmsgbody, 'html'))
    screenmsg += "\nTotal Value: {}".format(round(totalval, 2))

    # Return output
    if to_mail:
        return emailmsg
    else:
        return screenmsg


if __name__ == '__main__':
    argparse()
    output = process_data()

    if to_mail:
        server = smtplib.SMTP(smtpserver, smtpport)
        server.sendmail(sender, rcpt, output.as_string())
    else:
        print(output)

