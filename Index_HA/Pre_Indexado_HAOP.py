import json
from urllib.request import urlopen

n = 100
A_OPEN = 1
A_CLOSE = 1
HA_OPEN_LIST=[]
url1 = 'https://testnet.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol=XBT&count={stack}&start='.format(stack = n)
url2 = '&reverse=true'
ohcl = url1 + '0' + url2
u = urlopen(ohcl).read().decode('utf8')
data = json.loads(u)

for stock in reversed(data):
    
    OPEN = stock['open']
    HIGH = stock['high']
    LOW = stock['low']
    CLOSE = stock['close']
   
    HA_CLOSE = (OPEN+HIGH+LOW+CLOSE)/4
    HA_OPEN =  round((A_OPEN + A_CLOSE)/2,2)
    
    if n == 100:
        HA_OPEN =  (OPEN + CLOSE)/2

    HA_HIGH = max(HIGH,HA_OPEN,HA_CLOSE)
    HA_LOW = min(LOW,HA_OPEN,HA_CLOSE)
    
    A_OPEN = HA_OPEN
    A_CLOSE = HA_CLOSE
    #print('{num} - {symbol} - O: {Open} - H: {high} - L: {low} - C: {close} - HA_CLOSE: {HAC}'.format(symbol=stock['symbol'], num=n, Open=stock['open'], close=stock['close'], high=stock['high'], low=stock['low'], HAC = HA_CLOSE))    
    n = n-1
    #print('{num} - {symbol} - HO: {Open} - HHigh: {high} - HLow: {low} - HC: {close}'.format(symbol=stock['symbol'], num=n, Open=HA_OPEN, close=HA_CLOSE, high=HA_HIGH, low=HA_LOW))

    if n<5:
        HA_OPEN_LIST.append(HA_OPEN)
        
def get_HA_OPEN_CANDLES():
    return HA_OPEN_LIST

