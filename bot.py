import websocket, json, pprint, talib, sys
import config, api_requests, trade_book
from studies import rsi_study

SYMBOL = 'ethusdt'
INTERVAL = '1m'

# default socket-stream messages
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    print('recieved message')
    json_msg = json.loads(message)
    pprint.pprint(json_msg)



#######################################################################
# CANDLE WEB-SOCKET STREAM
#######################################################################
def on_candle_close(ws):
    trade_book.calculate_profit()
    print('closed connection')


def on_candle_open(ws):
    print('opened connection')
    # initialize your study here

    #initialize the rsi study
    rsi_study.init_study(SYMBOL, INTERVAL)

# custom message for candle socket stream
def on_candle_message(ws, message):
    print('recieved message')
    
    # get most recent candle
    json_msg = json.loads(message)
    candle = json_msg['k']

    #run your study here

    # run the rsi study
    rsi_study.run_study(candle)
    

# build a candle data stream
CANDLE_SOCKET = config.build_candle_socket(SYMBOL, INTERVAL)
print(CANDLE_SOCKET)

# build the websocket
ws_candle = websocket.WebSocketApp(CANDLE_SOCKET, on_open=on_candle_open, on_close=on_candle_close, on_message=on_candle_message)
ws_candle.run_forever()



