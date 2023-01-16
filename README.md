# CC-Stats
## Crypto currency stats

A simple api call tool for getting a small amount of coin stats 
to send to your email box on a daily (or whatever you want) basis.

## Requirements
- Python 3.6 or higher
- A valid Pro account with an API key from coinmarketcap.com
- Crypto currency

## API Key
You can register yourself to https://pro.coinmarketcap.com for
a free key. You can spend up to 10k a month in requests.

## How to use

Copy the `cc-stat.yml_example` to `cc-stats.yml`.

In this `cc-stats.yml` file you can add your assets, as a simple list.
The assets needs to valid with coinmarketcap.com and need to be in
capital.

For the email part, of course, you need to correct the settings to
your need and situation. 

After that you can run it:

```
python3 cc-stats.py
```

Or to email:

```
python3 cc-stats.py -m
```

## Output
```
Latest coin prices

Coin        Qty     Price       Total (USD)
ETH         1       1586.11     1586.11
USDT        20.5    1.00        20.50

Total Value: 1606.61
```

Enjoy!
