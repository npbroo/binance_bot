import config_api_keys

# CUSTOM KEYS
API_KEY = config_api_keys.API_KEY # replace with your api key
SECRET_KEY = config_api_keys.SECRET_KEY # replace with your secret key

# API CONNECTION (rest server requests)
API_BASE = 'https://api.binance.com'

# WEBSOCKET CONNECTION (websocket streams)
SOCKET_BASE = 'wss://stream.binance.us:9443'

# candle socket endpoint
CANDLE_SOCKET_ENDPOINT = '/ws/{}@kline_{}'
#valid candlestick intervals: {1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M}
def build_candle_socket(symbol, interval):
    return SOCKET_BASE + CANDLE_SOCKET_ENDPOINT.format(symbol, interval)

# book stream socket endpoint
BOOK_SOCKET_ENDPOINT = '/ws/{}@bookTicker'
def build_book_socket(symbol):
    return SOCKET_BASE + BOOK_SOCKET_ENDPOINT.format(symbol)
