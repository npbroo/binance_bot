from datetime import datetime
import trade_book, api_requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from pprint import pprint

#define variable
#fig = None
go_data = None
go_subplot_data = None
df = None
title = ''

# quick print chart method
def print_chart(data):
    #initialize the chart
    init_chart(data)
    #annotate and draw the chart
    draw_chart()

# initialize the chart 
def init_chart(data, name):
    global title
    title = name
    
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
    global title, go_data, go_subplot_data

    # if there are sub plots to draw    
    if(go_subplot_data != None):
        subplot_keys = list(go_subplot_data.keys())
        num_plots = len(subplot_keys) + 1
        row_widths = [.7]
        # draw the subplots
        for plot in subplot_keys:
            row_widths.insert(0, 0.2)
        print(num_plots)
        fig = make_subplots(rows=num_plots, cols=1, shared_xaxes=True, vertical_spacing=0.03, subplot_titles=[title] + subplot_keys, row_width=row_widths)
        
        # draw the main plot
        for plot in go_data:
            fig.add_trace(plot, row=1, col=1)
    
        count = 1
        for key in go_subplot_data:
            count += 1
            for subplot in go_subplot_data[key]:
                fig.add_trace(subplot, row=count, col=1)
        
        fig.update_xaxes(title_text='Time', row=num_plots, col=1)
        fig.update_yaxes(title_text='Price($)', row=1, col=1)
    
    # if there are no subplots to draw
    else:
        fig = go.Figure(data=go_data)
        fig.update_layout(title_text=title, title_x=0.5)
        fig.update_xaxes(title_text='Time')
        fig.update_yaxes(title_text='Price $')

    # annotate the chart
    annotate_chart(fig)
    
    fig.layout.xaxis.rangeslider.visible = False
    fig.show()

def annotate_chart(fig):
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


# add indicators using this method (must be called after initializing and before drawing)
def add_line_study(y_list, name, color, subplot=None):

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

    if(subplot != None):
        insert_study(go_layer, subplot)
    else:
        go_data = go_data + go_layer

def insert_study(go_layer, subplot):
    global go_subplot_data
    if(go_subplot_data == None):
        go_subplot_data = {}
        go_subplot_data[subplot] = go_layer
    else:
        if (subplot in go_subplot_data):
            go_subplot_data[subplot] += go_layer
        else:
            go_subplot_data[subplot] = go_layer