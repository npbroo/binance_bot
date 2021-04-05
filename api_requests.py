import time, json, hmac, hashlib, requests, pprint, datetime, math
from urllib.parse import urljoin, urlencode
import config

#list headers here
headers = {
    'X-MBX-APIKEY': config.API_KEY
}

#API request for order book ticker
def get_book_ticker(symbol):
    PATH = '/api/v3/ticker/bookTicker'
    params = {
        'symbol': symbol,
    }
    url = urljoin(config.API_BASE, PATH)
    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        return r.json()

def get_candlestick_data(symbol, interval, start_time=None, end_time=None, limit=None):
    PATH = '/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
    }
    if(start_time != None):
        params['startTime'] = start_time
    if(end_time != None):
        params['endTime'] = end_time
    if(limit != None):
        params['limit'] = limit
        if(limit > 1000):
            limit = 1000
    
    url = urljoin(config.API_BASE, PATH)
    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        return r.json()

def get_candlestick_data_series(symbol, interval, time_span, end_time=None, limit=1000):

    if(limit > 1000):
        limit = 1000

    if(end_time == None):
        end_time = int(datetime.datetime.now().replace(second=0, microsecond=0).timestamp())

    time_span_to_start_date = {
        '5m':end_time-300,
        '30m':end_time-1800,
        '1h':end_time-3600,
        '2h':end_time-7200,
        '6h':end_time-21600,
        '8h':end_time-28800,
        '12h':end_time-43200,
        '1d':end_time-86400,
        '3d':end_time-259200,
        '1w':end_time-604800,
        '2w':end_time-1209600,
        '1M':end_time-2628288,
        '3M':end_time-7890000,
        '6M':end_time-15780000,
        '1y':end_time-31536000,
        '3y':end_time-94608000,
    }

    start_date = time_span_to_start_date[time_span]
    
    interval_to_seconds = {
        '1m':60,
        '3m':180,
        '5m':300,
        '15m':900,
        '30m':1800,
        '1h':3600,
        '2h':7200,
        '4h':14400,
        '6h':21600,
        '8h':28800,
        '12h':43200,
        '1d':86400,
        '3d':259200,
        '1w':604800,
        '1M':2628288,
    }

    # calculate the new start date and end date for the current request timeframe

    temp_end_date = end_time
    temp_start_date = temp_end_date - limit*interval_to_seconds[interval]
    if(temp_start_date < start_date):
        limit = (temp_end_date - start_date) / interval_to_seconds[interval]
        limit = int(limit)

    #create a list to store all historical data
    all_data_sets = []
    all_data_sets += get_candlestick_data(symbol=symbol, interval=interval, end_time=temp_end_date*1000, limit=limit)

    # A cap on requests so you that you don't get near the max number of requests (1200/min)
    cap = 100
    num_requests = int(math.ceil((end_time-start_date)/interval_to_seconds[interval]/limit))
    time.sleep(1)
    print("requests: {}".format(num_requests))
    if (num_requests > cap):
        num_requests = cap

    for i in range(num_requests):
        temp_end_date = temp_end_date - limit*interval_to_seconds[interval]
        temp_start_date = temp_end_date - limit*interval_to_seconds[interval]
        if(temp_start_date < start_date):
            limit = (temp_end_date - start_date) / interval_to_seconds[interval]
            limit = int(limit)
        
        if(limit == 0):
            break
    
        data_set = get_candlestick_data(symbol=symbol, interval=interval, end_time=temp_end_date*1000, limit=limit)
        all_data_sets = data_set + all_data_sets

    return all_data_sets
