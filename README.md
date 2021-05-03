# SUPERTREND
a trading bot yo.  dont judge, this thing is clever enough.


STRATEGY:
moving average bands using +ATR and -ATR to create a trend filter.  Long signal created from previous close touching top band, indicating an uptrend.  
Short signal created when previous close touches bottom band, indicating a trend reversal.

To install:

git clone https://github.com/sevenisalie/SUPERTREND.git

ENV VARIABLES:
api = #this is your brokers api key
secret = #brokers api secret
password = #brokers api password (not every broker has this)

