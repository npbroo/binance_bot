import talib, numpy, sys, time
from datetime import datetime
sys.path.append("..")
import api_requests, trade_book, plotly_chart

#SYMBOL and AMOUNT
TRADE_SYMBOL = ''
TRADE_QUANTITY = 0.05

#TTM SQUEEZE SETTINGS
BB_PERIOD = 20
BB_DEV = 2
BB_COLOR = 'blue'
KC_PERIOD = 20
KC_DEV = 1.5
KC_COLOR = 'red'

#internal variables
rolling_storage = {'highs':[], 'lows':[], 'closes':[]}
rolling_storage_cap = 200 #Must cap if you are syncing live data
in_position = False

def init_study(symbol, interval, back_test=None):
    # init ther trade book
    trade_book.init_trade_book()

    # set the trade symbol
    global TRADE_SYMBOL
    TRADE_SYMBOL = symbol.upper()

    if(back_test == None):
        hist_data = api_requests.get_candlestick_data(symbol=TRADE_SYMBOL, interval=interval, limit=30)

        # populate storage array with the closes, high, and low from historical candlestick data from the last 30 minutes
        global rolling_storage
        for candle in hist_data:
            rolling_storage['highs'].append(float(candle['h']))
            rolling_storage['lows'].append(float(candle['l']))
            rolling_storage['closes'].append(float(candle['c']))

def run_study(candle, avg_spread=None):

    # if candle is closed, then print the closing price
    if(candle['x']): 
        close = candle['c']
        #print('Candle closed at {}'.format(close))
        
        # add to storage
        global rolling_storage
        rolling_storage['highs'].append(float(candle['h']))
        rolling_storage['lows'].append(float(candle['l']))
        rolling_storage['closes'].append(float(candle['c']))

        # if the number stored is greater than the rolling storage cap, pop it off the list
        if(rolling_storage_cap != None):
            for key in rolling_storage:
                if(len(rolling_storage[key]) > rolling_storage_cap):
                    rolling_storage[key].pop(0)


        # get the bid/ask prices (either current or simulated)
        if(avg_spread == None):
            book_ticker = api_requests.get_book_ticker(TRADE_SYMBOL)
            bid_price = book_ticker['bidPrice']
            ask_price = book_ticker['askPrice']
        else: 
            bid_price = float(close) - avg_spread/2.0
            ask_price = float(close) + avg_spread/2.0
        
        # calculate ttm_squeeze
        indicators = {}
        # first calculate bollinger bands
        if( len(rolling_storage['closes']) > BB_PERIOD):
            # generate bollinger bands
            np_closes = numpy.array(rolling_storage['closes'])
            bb_upper, bb_middle, bb_lower = talib.BBANDS(np_closes, timeperiod=BB_PERIOD, nbdevup=BB_DEV, nbdevdn=BB_DEV, matype=0)
            indicators['bb_upper'] = {'data':bb_upper,'color':BB_COLOR}
            indicators['bb_middle'] = {'data':bb_middle,'color':BB_COLOR}
            indicators['bb_lower'] = {'data':bb_lower,'color':BB_COLOR}

        # then calculate keltner channels
        if( len(rolling_storage['closes']) > KC_PERIOD and len(rolling_storage['highs']) > KC_PERIOD and len(rolling_storage['lows']) > KC_PERIOD):
            # generate keltner channels
            np_highs = numpy.array(rolling_storage['highs'])
            np_lows = numpy.array(rolling_storage['lows'])
            np_closes = numpy.array(rolling_storage['closes'])
            sma = talib.SMA(np_closes, timeperiod=KC_PERIOD)
            atr = talib.ATR(np_highs, np_lows, np_closes, timeperiod=KC_PERIOD)
            kc_upper = sma + (atr * KC_DEV)
            kc_lower = sma - (atr * KC_DEV)
            indicators['kc_upper'] = {'data':kc_upper,'color':KC_COLOR}
            indicators['kc_lower'] = {'data':kc_lower,'color':KC_COLOR}


        return indicators
        
        '''
        d = {}
        d['x_list'] = bb_upper
        d['y_list'] = closes_times
        return d
        '''
        

        #plotly_chart.add_line_study(bb_upper, closes_times, 'BB_upper')