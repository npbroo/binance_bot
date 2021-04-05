import talib, numpy, sys, time
from datetime import datetime
sys.path.append("..")
import api_requests, trade_book

#CALCULATE THE RSI
in_position = False
RSI_PERIOD = 14
RSI_OVERBOUGHT = 80
RSI_OVERSOLD = 20
TRADE_SYMBOL = ''
TRADE_QUANTITY = 0.05
closes = []

def init_study(symbol, interval, back_test=None):
    # init ther trade book
    trade_book.init_trade_book()

    # set the trade symbol
    global TRADE_SYMBOL
    TRADE_SYMBOL = symbol.upper()

    if(back_test == None):
        # populate closes array with historical data from the last 15 minutes
        global closes

        hist_data = api_requests.get_candlestick_data(symbol=TRADE_SYMBOL, interval=interval, limit=20)
        for candle in hist_data:
            #print('open: {} close: {}'.format(candle[0], candle[4]))
            closes.append(float(candle[4]))
        
    

def run_study(candle, avg_spread=None):

    # if candle is closed, then print the closing price
    if(candle['x']): 
        close = candle['c']
        print('Candle closed at {}'.format(close))
        
        # add to closes list
        global closes
        closes.append(float(close))

        # only need to store the last 20 or so closes in memory
        if(len(closes) > 20):
            closes.pop(0)

        #get current bid/ask prices
        if(avg_spread == None):
            book_ticker = api_requests.get_book_ticker(TRADE_SYMBOL)
            bid_price = book_ticker['bidPrice']
            ask_price = book_ticker['askPrice']
        else: 
            bid_price = float(close) - avg_spread/2.0
            ask_price = float(close) + avg_spread/2.0
        
        if( len(closes) > RSI_PERIOD):
            # calculate rsi
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            current_rsi = rsi[-1]
            print('RSI is {}'.format(current_rsi))

            # get time of the timestamp
            unix_time = candle['T']/1000
            #ts = datetime.utcfromtimestamp(unix_time).strftime("%x %X")
            ts = datetime.fromtimestamp(unix_time).strftime("%x %X")
            
            global in_position
            if(current_rsi > RSI_OVERBOUGHT):
                
                if(in_position):
                    # sell the coin
                    print('SELL! SELL! SELL! SELL!')
                    sell_str = '{} GMT - Sell {} of {} for {}.'.format(ts, str(TRADE_QUANTITY), TRADE_SYMBOL, str(bid_price))
                    print(sell_str)

                    # write trade to trade book
                    trade_book.write_trade(ts, TRADE_SYMBOL, str(TRADE_QUANTITY), 'SELL', str(bid_price))

                    # close position
                    in_position = False

                    #put binance sell logic here
                else:
                    print("It is overbought, but you don't own any. Nothing to do.")

            if(current_rsi < RSI_OVERSOLD):
                if(in_position):
                    print('It is oversold, but you already own it. Nothing to do.')
                else:
                    #buy the coin
                    print('BUY! BUY! BUY! BUY!')
                    buy_str = '{} GMT - Buy {} of {} for {}.'.format(ts, str(TRADE_QUANTITY), TRADE_SYMBOL, str(ask_price))
                    print(buy_str)

                    # write trade to trade book
                    trade_book.write_trade(ts, TRADE_SYMBOL, str(TRADE_QUANTITY), 'BUY', str(ask_price))

                    # open position
                    in_position = True

                    #put binance order logic here