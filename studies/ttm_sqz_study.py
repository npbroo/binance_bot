import talib, numpy, sys, time
from datetime import datetime
sys.path.append("..")
import api_requests, trade_book, chart

#SYMBOL and AMOUNT
TRADE_SYMBOL = ''
TRADE_QUANTITY = 0.05

#TTM SQUEEZE SETTINGS
BB_PERIOD = 20 #the rolling period required to calculate the bollinger bands
BB_DEV = 2 # the deviation of the bollinger bands
KC_PERIOD = 20 # the rolling period required to calculate the keltner channels
KC_DEV = 1.5 # the deviation of the keltner channels
MOM_PERIOD = 20 # the rolling period required to calculate the moving average
MOM_MA_PERIOD = 9 # sensitivity to buying and selling
SQZ_PERIOD = 5 # the amount of periods the Bollinger bands must be inside the keltner channels for it to be considered a 'squeeze'
SHORT = True # can the bot sell to open?

#TTM BACKTEST VISUAL SETTINGS
BB_COLOR = 'blue'
KC_COLOR = 'red'
MOM_COLOR = 'green'
MOM_MA_COLOR = 'purple'


#internal variables
rolling_storage = {'highs':[], 'lows':[], 'closes':[]}
rolling_storage_cap = None # Must cap if you are syncing live data
in_long_position = False
in_short_position = False
sqz_on = False
sqz_len = 0

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
        bb_on = len(rolling_storage['closes']) > BB_PERIOD
        if(bb_on):
            # generate bollinger bands
            np_closes = numpy.array(rolling_storage['closes'])
            bb_upper, bb_middle, bb_lower = talib.BBANDS(np_closes, timeperiod=BB_PERIOD, nbdevup=BB_DEV, nbdevdn=BB_DEV, matype=0)
            indicators['bb_upper'] = {'data':bb_upper,'color':BB_COLOR, 'subplot':'TTM'}
            indicators['bb_middle'] = {'data':bb_middle,'color':BB_COLOR, 'subplot':'TTM'}
            indicators['bb_lower'] = {'data':bb_lower,'color':BB_COLOR, 'subplot':'TTM'}

        # calculate keltner channels
        kc_on = len(rolling_storage['closes']) > KC_PERIOD and len(rolling_storage['highs']) > KC_PERIOD and len(rolling_storage['lows']) > KC_PERIOD
        if(kc_on):
            # generate keltner channels
            np_highs = numpy.array(rolling_storage['highs'])
            np_lows = numpy.array(rolling_storage['lows'])
            np_closes = numpy.array(rolling_storage['closes'])
            sma = talib.SMA(np_closes, timeperiod=KC_PERIOD)
            atr = talib.ATR(np_highs, np_lows, np_closes, timeperiod=KC_PERIOD)
            kc_upper = sma + (atr * KC_DEV)
            kc_lower = sma - (atr * KC_DEV)
            indicators['kc_upper'] = {'data':kc_upper,'color':KC_COLOR, 'subplot':'TTM'}
            indicators['kc_lower'] = {'data':kc_lower,'color':KC_COLOR, 'subplot':'TTM'}

        mom_on = len(rolling_storage['closes']) > MOM_PERIOD
        mom_ma_on = len(rolling_storage['closes']) > MOM_PERIOD + MOM_MA_PERIOD
        if(mom_on):
            np_closes = numpy.array(rolling_storage['closes'])
            mom = talib.MOM(np_closes, MOM_PERIOD)
            indicators['mom'] = {'data':mom,'color':MOM_COLOR, 'subplot':'MOM'}
            if(mom_ma_on):
                mom_ma = talib.MA(mom, MOM_MA_PERIOD)
                indicators['mom_ma'] = {'data':mom_ma,'color':MOM_MA_COLOR, 'subplot':'MOM'}

        global sqz_on, sqz_len, in_long_position, in_short_position, SHORT
        unix_time = candle['T']/1000 
        ts = datetime.fromtimestamp(unix_time).strftime("%x %X")
        if(bb_on and kc_on and mom_ma_on):
            if(bb_upper[-1] < kc_upper[-1] and bb_lower[-1] > kc_lower[-1]):
                sqz_on = True
                sqz_len += 1
                #print('{}: Squeeze is on. Len: {}'.format(ts, sqz_len))
            else:
                sqz_on = False
                if(sqz_len > SQZ_PERIOD and in_long_position == False and in_short_position == False):
                    if(mom_ma[-1] > mom_ma[-2]): 
                        # take a long position 
                        buy_str = '{} GMT - Buy (to open) {} of {} for {}.'.format(ts, str(TRADE_QUANTITY), TRADE_SYMBOL, str(ask_price))
                        print(buy_str)
                        # write trade to trade book
                        trade_book.write_trade(ts, TRADE_SYMBOL, str(TRADE_QUANTITY), 'BUY', str(ask_price))
                        in_long_position= True
                    elif(mom_ma[-1] < mom_ma[-2] and SHORT):
                        #take a short position 
                        sell_str = '{} GMT - Sell (to open) {} of {} for {}.'.format(ts, str(TRADE_QUANTITY), TRADE_SYMBOL, str(bid_price))
                        print(sell_str)
                        # write trade to trade book
                        trade_book.write_trade(ts, TRADE_SYMBOL, str(TRADE_QUANTITY), 'SELL', str(bid_price))
                        in_short_position= True

                # reset squeeze length
                sqz_len = 0

        # if in a long position
        if(in_long_position):
            if(mom_ma[-1] < mom_ma[-2]):
                # sell your long positon
                sell_str = '{} GMT - Sell (to close) {} of {} for {}.'.format(ts, str(TRADE_QUANTITY), TRADE_SYMBOL, str(bid_price))
                print(sell_str)
                # write trade to trade book
                trade_book.write_trade(ts, TRADE_SYMBOL, str(TRADE_QUANTITY), 'SELL', str(bid_price))
                # leave position 
                in_long_position = False 

        # if in a short position
        if(in_short_position):
            if(mom_ma[-1] > mom_ma[-2]):
                # sell your long positon
                buy_str = '{} GMT - Buy (to close) {} of {} for {}.'.format(ts, str(TRADE_QUANTITY), TRADE_SYMBOL, str(bid_price))
                print(buy_str)
                # write trade to trade book
                trade_book.write_trade(ts, TRADE_SYMBOL, str(TRADE_QUANTITY), 'BUY', str(bid_price))
                # leave position 
                in_short_position = False 
                
        return indicators