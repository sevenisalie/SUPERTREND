import ccxt
import pandas as pd
pd.set_option('display.max_rows', None)
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import matplotlib.pyplot as plt
import time
import os

api = os.getenv('API_KEY')
secret = os.getenv('SECRET')
password = os.getenv('PASSWORD')

data = ccxt.binance()

exchange = ccxt.coinbasepro()
exchange.apiKey = api
exchange.secret = secret
exchange.password = password
exchange.checkRequiredCredentials()


def trueRange(df):
    #Get the fuck outta unix time
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    

    #get previous days close in one simple trick
    df['pclose'] = df['close'].shift(1)

    #Get true range Max[h-l, abs(h-pc), abs(l-pc)]

    df['h-l'] = df['high'] - df['low']
    df['h-pc'] = abs(df['high'] - df['pclose'])
    df['l-pc'] = abs(df['low'] - df['pclose'])
    truerange = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
    return truerange

def averageTrueRange(df, period=7):
    #now get average true range TR / sma
    df['TR'] = trueRange(df)
    atr = df['TR'].rolling(period).mean()
    return atr

def supertrend(df, period=7, multiplier=2):
    # upper = ((high + low) / 2) + (multiplier * ATR)
    #lower = ((high + low) / 2) - (multiplier * ATR)
    df['ATR']=averageTrueRange(df, period)
    df['upper'] = ((df['high'] + df['low']) / 2) + (multiplier * df['ATR'])
    df['lower'] =  ((df['high'] + df['low']) / 2) - (multiplier * df['ATR'])
    df['up_trend'] = True  #just initializing the uptrend df column
 
    




    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upper'][previous]: #if the current close is above the upper band, this indicates a flip to uptrend.  aka df['up_trend] = true
            df['up_trend'][current] = True
        elif df['close'][current] < df['lower'][previous]: #else, the current close is below the upper band this indicates a downtrend aka 
            df['up_trend'][current] = False

        else:
            df['up_trend'][current] = df['up_trend'][previous]


        #logic for trailing stop
            if df['up_trend'][current] and df['lower'][current] < df['lower'][previous]:
                df['lower'][current] = df['lower'][previous]

            if not df['up_trend'][current] and df['upper'][current] > df['upper'][previous]:
                df['upper'][current] = df['upper'][previous]






    return df


def check_position():
    open = False
    if (exchange.has['fetchOrders']):
        orders = exchange.fetchOrders(symbol = 'MATIC/USD', since = None, limit =1, params = {})
        empty = []
        if orders == empty:
            open = False
            print("No open orders")
        else:
            open = True
            for order in orders:
                print(order['id'] + '   '  + order['info']['product_id'] + '    ' + order['info']['size'])
    return open


def sell_order(symbol, amount):
  sell = exchange.create_order(symbol=symbol, type="market", side='sell', amount=amount,)
  return sell

def buy_order(symbol, amount):
  buy = exchange.create_order(symbol=symbol, type="market", side="buy", amount=amount,)
  return buy

open = False

def signals(df):
    #get the current and previous trend value (T/F)
    current = len(df.index) - 1
    previous = current - 1
    direction = "sideways"
    global open
   
    #open_position = check_position()

    if not df['up_trend'][current] and not df['up_trend'][previous]:
        direction = "DOWN"
        if open:
            sell_order(symbol="MATIC/USD", amount=5)
            open = False  

    if df['up_trend'][current] and df['up_trend'][previous]:
        direction = "UP"
        if not open:
            buy_order(symbol="MATIC/USD", amount=5)
            open = True  

    #if current is true and previous is false, that means we just switched to an uptrend and should buy
    ###BUY####
    if df['up_trend'][current] and not df['up_trend'][previous]:
        print("BULL MODE ACTIVATED - BUY THIS SHIT")
        if not open:
            buy_order(symbol="MATIC/USD", amount=5)
            open = True
        else:
            print("open and trending")
            
    
    #if previous is true and current is false, we just switched to a downtrend and should sell
    ####SELL####
    if df['up_trend'][previous] and not df['up_trend'][current]:
        print("EAT MY BEAR SHIT - SELL THIS BAG")
        if open:
            sell_order(symbol="MATIC/USD", amount=5)
            open = False
        else:
            print("closed and trending")
           

    
    print(f"STILL TRENDING {direction}")

    print(superdf.tail(2))




while True:
    candles = data.fetch_ohlcv('MATIC/BUSD', timeframe='1m', limit=100)
    df = pd.DataFrame(candles[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    superdf = supertrend(df)
    signals(superdf)
    time.sleep(15)


"""PLOT
x = superdf['timestamp']
y = superdf['upper']
yy = superdf['lower']
plt.plot(x, y)
plt.plot(x, yy)
plt.show()
"""