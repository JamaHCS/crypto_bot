import sys
import json

from market_maker.market_maker import OrderManager
from urllib.request import urlopen
from Index_HA import Pre_Indexado_HAOP

First_HA_Openings = Pre_Indexado_HAOP.get_HA_OPEN_CANDLES()[0]
flag_long = False
flag_short = False

class CustomOrderManager(OrderManager):
    """A sample order manager for implementing your own custom strategy"""

    
    def place_orders(self) -> None:
        global flag_long
        global flag_short
        MA_High = 0
        MA_Close = 0
        periodo = 5

        A_OPEN = 0
        A_CLOSE = 0

        url1 = 'https://testnet.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol=XBT&count={stack}&start='.format(stack = periodo)
        url2 = '&reverse=true'

        ohcl = url1 + '0' + url2

        u = urlopen(ohcl).read().decode('utf8')
        data = json.loads(u)
        
        for stock in reversed(data):
            #print('symbol: {symbol} - open: {Open} - close: {close} - high: {high} - low: {low}'.format(symbol=stock['symbol'], Open=stock['open'], close=stock['close'], high=stock['high'], low=stock['low']))

            OPEN = stock['open']
            HIGH = stock['high']
            LOW = stock['low']
            CLOSE = stock['close']
            
            HA_CLOSE = (OPEN+HIGH+LOW+CLOSE)/4
            if A_OPEN == 0:
                HA_OPEN = First_HA_Openings

            else:
                HA_OPEN =  round((A_OPEN + A_CLOSE)/2,2)
            
            A_OPEN = HA_OPEN
            A_CLOSE = HA_CLOSE
            
            HA_HIGH = max(HIGH,HA_OPEN,HA_CLOSE)
            HA_LOW = min(LOW,HA_OPEN,HA_CLOSE)
            
            MA_High = HA_HIGH + MA_High
            MA_Close = HA_CLOSE + MA_Close

        #---------------   IMPRESION DE DATOS DE ESTRATEGIA   ----------------------

        #print('Candle OPEN: ', HA_OPEN)
        #print('Candle CLOSE: ', HA_CLOSE)
        print('Candle HIGH: ', HA_HIGH)
        MA_High = MA_High / periodo
        print('MA High: ', MA_High)
        MA_Close = MA_Close / periodo
        print('MA Close: ', MA_Close)

        #NO NECESARIO IMPRIMIR
       
        
        #print('Candle LOW: ', HA_LOW)
        
        
        buy_orders = []
        sell_orders = []
        ticker = self.exchange.get_ticker()

        if HA_CLOSE > MA_High and (not flag_long):
            print('LONG ENTRY AT:', ticker["buy"])
            flag_long = True
            flag_short = False
            
        if HA_CLOSE < MA_Close and (not flag_short):
            print('SHORT ENTRY AT:', ticker["buy"])
            flag_long = False
            flag_short = True

        buy_orders.append({'price': ticker["buy"]-150, 'orderQty': 100, 'side': "Buy"})
        sell_orders.append({'price': ticker["buy"]+150, 'orderQty': 100, 'side': "Sell"})
        



        print('FL: ', flag_long)
        print('FS: ', flag_short)

        # populate buy and sell orders, e.g.
        #buy_orders.append({'price': 9000, 'orderQty': 100, 'side': "Buy"})


        #sell_orders.append({'price': 11000, 'orderQty': 100, 'side': "Sell"})

        self.converge_orders(buy_orders, sell_orders)





def run() -> None:
    order_manager = CustomOrderManager()

    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        order_manager.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
