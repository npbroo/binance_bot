import api_requests, trade_book, chart, time, pprint, chart
from studies import rsi_study, ttm_sqz_study
from datetime import datetime

SYMBOL = 'ETHUSDT' # The ticker symbol to check
AVG_SPREAD = .50 # the average buy/ask spread (for calculating more accurate profits)
INTERVAL = '1m' # the ticker interval
TIME_SPAN = '6h' # the timespan of data to get
END_TIME = None

def run_algo_back_test(symbol, avg_spread, interval, time_span, end_time=None):
    
    # retrieve the historical data for this back test
    historical_data = api_requests.get_candlestick_data_series(symbol=symbol, interval=interval, time_span=time_span, end_time=end_time)
    data = historical_data
    # create new tradebook
    trade_book.init_trade_book()

    # initialize the study
    '''
    OTHER STUDIES:
    rsi_study.init_study(symbol, interval, back_test=True)
    '''
    ttm_sqz_study.init_study(symbol, interval, back_test=True)

    #initialize the chart
    chart.init_chart(historical_data)

    indicators = None
    #run the study candle by candle
    for candle in historical_data:

        #create the candle that mimics the one recieved from the websocket
        c = {}
        c['x'] = True
        c['h'] = candle[2]
        c['l'] = candle[3]
        c['c'] = candle[4]
        c['avg_spread'] = avg_spread
        c['T'] = candle[6]

        #run the study on each candle to test the strategy
        '''
        OTHER STUDIES:
        rsi_study.run_study(c, avg_spread=avg_spread)
        '''
        indicators = ttm_sqz_study.run_study(c, avg_spread=avg_spread)
    
    # add indicator studies to the chart
    for key in indicators:
        data = indicators[key]['data']
        color = indicators[key]['color']
        chart.add_line_study(data, key, color=color)
    
    # draw the chart
    chart.draw_chart()


run_algo_back_test(symbol=SYMBOL,  avg_spread=AVG_SPREAD, interval=INTERVAL, time_span=TIME_SPAN, end_time=END_TIME)

trade_book.calculate_profit()