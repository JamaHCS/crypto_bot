import sys
import json
import numpy as np
import pandas as pd

from market_maker.market_maker import OrderManager
#from urllib.request import urlopen
#from Index_HA import Pre_Indexado_HAOP

#First_HA_Openings = Pre_Indexado_HAOP.get_HA_OPEN_CANDLES()[0]
long_flag = False
short_flag = False
Parametro_SMA = 25
Quantity = 100  #USD


class CustomOrderManager(OrderManager):
    """A sample order manager for implementing your own custom strategy"""

    def place_orders(self) -> None:
        #Variables
        global long_flag
        global short_flag
        global Parametro_SMA
        buy_orders = []
        sell_orders = []
        ticker = self.exchange.get_ticker()


        #Obtener la base de datos del close, open, high y low del stock 

        Number_of_data = 50
        #data = pd.read_json('https://www.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol=XBT&count={N}&start=&reverse=true'.format(N=Number_of_data))
        data = pd.read_json('https://testnet.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol=XBT&count={N}&start=&reverse=true'.format(N=Number_of_data))
        
        temp = pd.to_datetime(data['timestamp'])
        data.drop(columns={'timestamp'},inplace=True)
        data.set_index(temp,inplace=True)
        data = data.reindex(index=data.index[::-1])

        #Cambiar el tipo de velas a heikin ashi

        data.drop(labels=['foreignNotional','turnover','lastSize','homeNotional','symbol'],axis=1,inplace=True)
        data['HA_close'] = (data['open']+data['high']+data['low']+data['close'])/4
        data['HA_open'] = 0
        data['HA_open'].iloc[0] = (data['open'].iloc[0] + data['close'].iloc[0])/2
        data['HA_high'] = 0
        data['HA_low']  = 0 


        for i in range(1,data.index.size):
            data['HA_open'].iloc[i] = round((data['HA_open'].iloc[i-1] + data['HA_close'].iloc[i-1])/2,2)


        for i in range(0,data.index.size):
            data['HA_high'].iloc[i] = max(data['high'].iloc[i],data['HA_open'].iloc[i],data['HA_close'].iloc[i])
            data['HA_low'].iloc[i] = min(data['low'].iloc[i],data['HA_open'].iloc[i],data['HA_close'].iloc[i])


        HA_Data = data
        HA_Data.drop(labels=['open','high','low','close','trades','volume','vwap'],axis=1,inplace=True)
        HA_Data.rename(columns={'HA_close':'close','HA_open':'open','HA_high':'high','HA_low':'low'},inplace=True)


        #Calcular las medias moviles simples de HA CLOSE y HA HIGH con un window de 25

        HA_Data['sma_High'] = HA_Data['high'].rolling(window = Parametro_SMA).mean()
        HA_Data['sma_Close'] = HA_Data['close'].rolling(window = Parametro_SMA).mean()
        
        print('----------------------------------------------------------------------------------------------------------')
        #print('{Pre Close}   |    {Open}    |   {PreHigh}  |   {PreLow}   | {PreHAClose} |  {HA Open}   |  {PreHAHigh} |')
        #print('{0:^14.2f}|{1:^14.2f}|{2:^14.2f}|{3:^14.2f}|{4:^14.2f}|{5:^14.2f}|{6:^14.2f}'.format(Close[days-2],Open[-1],High[-2],Low[-2],HA_Close[-2],HA_Open[-1],HA_High[-2]))
        
        
        print('SMA HIGH: {}'.format(HA_Data['sma_High'][-1]))
        print('PRICE: {}'.format(HA_Data['close'][-1]))
        print('SMA CLOSE: {}'.format(HA_Data['sma_Close'][-1]))
        
        
        
        #Realizar la logica de entradas y salidas al mercado

        if HA_Data['close'].iloc[i] > HA_Data['sma_High'].iloc[i] and not long_flag:
            # Go long 
            print('|o|o|o|o|o|o|o|o|o|o|o|o|o|o|o|')
            print('LONG ENTRY AT:', ticker["buy"])
            print('|o|o|o|o|o|o|o|o|o|o|o|o|o|o|o|')

            if short_flag:
                buy_orders.append({'price': ticker["buy"], 'orderQty': Quantity*2, 'side': "Buy"})
                self.converge_orders(buy_orders, sell_orders)

            else:
                buy_orders.append({'price': ticker["buy"], 'orderQty': Quantity, 'side': "Buy"})
                self.converge_orders(buy_orders, sell_orders)

            long_flag = True
            short_flag = False


        elif HA_Data['close'].iloc[i] < HA_Data['sma_Close'].iloc[i] and not short_flag:
            #Go short
            print('|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|')
            print('SHORT ENTRY AT:', ticker["buy"])
            print('|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|')

            if long_flag:
                #Significa que previamente habia un long abierto, se requiere cerrar dicha posicion y abrir un short (doble de orderQty)
                sell_orders.append({'price': ticker["buy"], 'orderQty': Quantity*2, 'side': "Sell"})
                self.converge_orders(buy_orders, sell_orders)

            else:
                sell_orders.append({'price': ticker["buy"], 'orderQty': Quantity, 'side': "Sell"})
                self.converge_orders(buy_orders, sell_orders)

            long_flag = False
            short_flag = True

        #---------------   GENERACION DE ORDENES   ----------------------
        
        print('Long: ', long_flag)
        print('Short: ', short_flag)

        



def run() -> None:
    order_manager = CustomOrderManager()

    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        order_manager.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

def max_value(a,b,c):
    if a > b and a > c:
        return a
    elif b > a and b > c:
        return b
    elif c > a and c > b:
        return c