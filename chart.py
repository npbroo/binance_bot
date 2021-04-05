from datetime import datetime
import trade_book, api_requests
import plotly.graph_objects as go
import pandas as pd
from pprint import pprint

#define variable
#fig = None
go_data = None
df = None

# quick print chart method
def print_chart(data):
    #initialize the chart
    init_chart(data)
    #annotate and draw the chart
    draw_chart()

# initialize the chart 
def init_chart(data):
    global df
    columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_vol', 'number_of_trades', 'taker_buy_base_asset_vol', 'taker_buy_quote_asset_vol', 'ignore']
    df = pd.DataFrame(data, columns=columns)
    # convert times to correct time
    df['open_time'] = pd.to_datetime(df['open_time']/1000 - 14400, unit='s') 
    df['close_time'] = pd.to_datetime(df['close_time']/1000 - 14400, unit='s')

    global go_data
    go_data = [
        go.Candlestick(
            name='Candlesticks',
            x=df['close_time'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
        )
    ]
     
# annotate and draw the chart
def draw_chart():
    global go_data
    fig = go.Figure(data=go_data)

    # get chart and annotate with buy/ sell points
    book = trade_book.return_book()
    for row in book:
        date = datetime.strptime(row['Date (GMT)'], "%x %X")
        price = row['Price']
        if(row['Trade Type'] == 'BUY'):
            fig.add_annotation(
                x=date, y=price, text='BUY: {}'.format(price), ax=-10, ay=50,
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, bgcolor="green", opacity=0.8
            )
        if(row['Trade Type'] == 'SELL'):
            fig.add_annotation(
                x=date, y=price, text='SELL: {}'.format(price), ax=10, ay=-50,
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, bgcolor="red", opacity=0.8
            )
    
    fig.layout.xaxis.rangeslider.visible = False
    fig.update_xaxes(title_text='Time')
    fig.update_yaxes(title_text='Price $')
    fig.show()


# add indicators using this method (must be called after initializing and before drawing)
def add_line_study(y_list, name, color='blue'):

    global go_data
    global df

    go_layer = [
        go.Scatter(
            x=df['close_time'][-len(y_list):],
            y=y_list, 
            name=name, 
            line={'color': color}
        )
    ]

    go_data = go_data + go_layer

