# CC-Stats
## Crypto currency stats

A simple api call tool for getting a small amount of coin stats 
to send to your email box on a daily (or whatever you want) basis.

## Requirements
- Python 3.x (Developped in 3.7, tested in 3.5)
- Modules requests, sys, smtplib
- A valid Pro account with a key from Coinmarketcap
- Crypto currency

## API Key
You can register yourself to https://pro.coinmarketcap.com for
a free key. You can spend up to 10k a month in requests.
Use the key in the 'api_key' variable.

## Currency
Based on your assets, you can add keys and values to the 'assets'
 dict. The key must be matching to the actual coin code used at
Coinmarketcap. The value is your actual number of coins.

## Output
```
Coin    Qty     Price       Totals (USD)
BTC     2       3651.62:    7303.24
ETH     1       117.69 :    117.69
```

Enjoy!
