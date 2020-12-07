#!/usr/local/bin/python3.7
#
# Created 9-Feb 2019
# Update 16-11-2020
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
    'XRP': 21.57,
    'STRAT': 29.99
}

to_mail = False

SMTP_SERVER = "smtp.somehost.com"
SMTP_PORT = 25
SENDER = "noreply@yourdomain.org"
RCPT = "john@doe.net"
API_KEY = "your Coinmarketcap Pro key"


def argparse():
    global to_mail

    if len(sys.argv) >= 2:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print(f"Syntax is {sys.argv[0]} -m or --mail\nDefault output is to screen\n")
            sys.exit()
        elif sys.argv[1] == '-m' or sys.argv[1] == '--mail':
            to_mail = True


def get_crypto_data(_assets):
    """
    Function to make the request to the remote server with given assets.

    :param _assets: dict containing assets
    :return: json
    """
    # Generate a string of coins pieced together for the API call
    coins = ",".join(assets)

    link = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={coins}"
    headers = {
        'X-CMC_PRO_API_KEY': API_KEY,
        'Accept': 'application/json'
    }

    # Do the call
    try:
        data = requests.get(link, headers=headers)
    except (requests.ConnectionError, requests.ConnectTimeout, requests.TooManyRedirects, requests.HTTPError):
        raise SystemExit("Could not connect")

    # Return the data
    try:
        jdata = data.json()
        if jdata['status']['error_code'] == 400:
            raise KeyError(jdata['status']['error_message'])
        else:
            return jdata['data']
    except KeyError as e:
        raise SystemExit(f"API Call went wrong, no usable data returned: {e}")


def process_data():
    """
    Function to present the data in a formatted manner, either on screen or via (html) email.
    """
    global to_mail

    # Retrieve coin info for the available assets
    all_crypto = get_crypto_data(assets)
    all_crypto = collections.OrderedDict(sorted(all_crypto.items()))

    # Generate the output
    email_msg = MIMEMultipart('alternative')
    email_msg['Subject'] = "Latest coin prices"
    email_msg['From'] = SENDER
    email_msg['To'] = RCPT
    email_msg_body = """
        <html>\n\t<head></head>\n\t<body style=\"font-family: arial;font-style:normal;font-size:12px\">\n
        \t\t<p>Crypto Summary</p>\n\t\t<table style=\"font-family: arial;font-style:normal;font-size:12px;
        text-align:left\">\n\t\t\t<tr><th style=\"text-align:left\">Coin</th><th 
        text-align:left\">Qty</th><th style=\"text-align:left\">Price</th><th style=\"text-align:left\">
        Totals (USD)</th></tr>\n"""
    screen_msg = f"{email_msg['Subject']}\n\nCoin\t\tQty\t\tPrice\t\tTotal (USD)\n"

    total_value = 0
    for coin, coin_items in all_crypto.items():
        price = coin_items['quote']['USD']['price']
        asset_value = price * assets[coin]
        total_value += asset_value
        email_msg_body += f"""
            \t\t\t<tr><td>{coin}</td><td>{assets[coin]}</td><td>{price:.2f}</td><td>{asset_value:.2f}</td></tr>\n"""
        screen_msg += f"{coin}\t\t{assets[coin]}\t\t{price:.2f}\t\t{asset_value:.2f}\n"

    email_msg_body += f"\t\t</table>\n\t\t<br>\n\t\t<p>Total value: {round(total_value, 2)}<p>\n\t</body>\n</html>\n"
    email_msg.attach(MIMEText(email_msg_body, 'html'))
    screen_msg += f"\nTotal Value: {round(total_value, 2)}"

    # Return output
    if to_mail:
        return email_msg
    else:
        return screen_msg


if __name__ == '__main__':
    argparse()
    output = process_data()

    if to_mail:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.sendmail(SENDER, RCPT, output.as_string())
    else:
        print(output)

