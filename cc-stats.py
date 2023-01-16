#!/bin/env python3
"""
 @author: bartjan@pc-mania.nl
 https://github.com/barreljan/cc-stats
"""
import requests
import sys
import argparse
import os
import smtplib
import collections
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from yaml import load, dump
from yaml import Loader, Dumper

path = os.path.dirname(__file__)
if not path:
    path = "."

try:
    if os.path.exists(f'{path}/cc-stats.yml'):
        stream = open(f'{path}/cc-stats.yml', 'r')
        config = load(stream, Loader=Loader)
        stream.close()
    else:
        raise SystemExit('No \'cc-stats.yml\' found, exiting...')

    assets = config['assets']
    smtp_server = config['email_settings']['smtp_server']
    smtp_port = config['email_settings']['smtp_port']
    sender = config['email_settings']['sender']
    rcpt = config['email_settings']['rcpt']
    api_key = config['cmc']['api_key']
except KeyError:
    raise SystemExit('There is something wrong with the config\nSee the \'cc-stats.yml_example\'')


def parse_args():
    """
    Parses the given arguments and returns the class object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mail', dest='to_mail', action='store_true',
                        help='Sends the result in a (HTML) email')

    return parser.parse_args()


def get_crypto_data(_assets: dict) -> dict:
    """
    Function to make the request to the remote server with given assets.

    :param _assets: dict containing assets
    :return: dict 
    """
    # Generate a string of coins pieced together for the API call
    coins = ','.join(assets)

    link = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={coins}'
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }

    # Do the call
    try:
        data = requests.get(link, headers=headers)
    except (requests.ConnectionError, requests.ConnectTimeout, requests.TooManyRedirects, requests.HTTPError):
        raise SystemExit('Could not connect')

    # Return the data
    try:
        jdata = data.json()
        if jdata['status']['error_code'] == 400:
            raise KeyError(jdata['status']['error_message'])
        else:
            return jdata['data']
    except KeyError as e:
        raise SystemExit(f'API Call went wrong, no usable data returned: {e}')


def report_data(data) -> tuple:
    """
    Function to present the data in a formatted manner, either on screen or via (html) email.

    :param data: dict
    :returns tuple: ('string with email message', 'string with screen message')
    """

    # Generate the output
    email_msg = MIMEMultipart('alternative')
    email_msg['Subject'] = "Latest coin prices"
    email_msg['From'] = sender
    email_msg['To'] = rcpt
    email_msg_body = """
        <html>\n\t<head></head>\n\t<body style=\"font-family: arial;font-style:normal;font-size:12px\">\n
        \t\t<p>Crypto Summary</p>\n\t\t<table style=\"font-family: arial;font-style:normal;font-size:12px;
        text-align:left\">\n\t\t\t<tr><th style=\"text-align:left\">Coin</th><th 
        text-align:left\">Qty</th><th style=\"text-align:left\">Price</th><th style=\"text-align:left\">
        Totals (USD)</th></tr>\n"""
    email_subject = email_msg['Subject']
    screen_msg = f'{email_subject}\n\nCoin\t\tQty\t\tPrice\t\tTotal (USD)\n'

    total_value = 0
    for coin, coin_items in data.items():
        price = coin_items['quote']['USD']['price']
        asset_value = price * assets[coin]
        total_value += asset_value
        email_msg_body += f"""
            \t\t\t<tr><td>{coin}</td><td>{assets[coin]}</td><td>{price:.2f}</td><td>{asset_value:.2f}</td></tr>\n"""
        screen_msg += f"{coin}\t\t{assets[coin]}\t\t{price:.2f}\t\t{asset_value:.2f}\n"

    email_msg_body += f"\t\t</table>\n\t\t<br>\n\t\t<p>Total value: {round(total_value, 2)}<p>\n\t</body>\n</html>\n"
    email_msg.attach(MIMEText(email_msg_body, 'html'))
    screen_msg += f'\nTotal Value: {round(total_value, 2)}'

    # Return output
    return email_msg, screen_msg


if __name__ == '__main__':
    options = parse_args()

    # Retrieve coin info for the available assets and sort them
    all_crypto = get_crypto_data(assets)
    all_crypto = collections.OrderedDict(sorted(all_crypto.items()))

    # Get the report(s)
    email_message, screen_message = report_data(data=all_crypto)

    # Provide report
    if options.to_mail:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.sendmail(sender, rcpt, email_message.as_string())
    else:
        print(screen_message)

