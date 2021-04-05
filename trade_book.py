import csv
from decimal import Decimal
#import numpy as np

def init_trade_book():
    with open('trade_history.csv','w',newline="") as File:
        writer = csv.writer(File)
        writer.writerow(['Date (GMT)', 'Symbol', 'Amount', 'Trade Type', 'Price'])

def write_trade(date, symbol, amount, trade_type, ticker_price):
    with open('trade_history.csv','a',newline="") as File:
        writer = csv.writer(File)
        writer.writerow([date, symbol, amount, trade_type, ticker_price])

def calculate_profit():
    with open('trade_history.csv', mode ='r') as File:
        print("\n")
        reader = csv.DictReader(File)
        total_profit = 0
        trade_profit = 0
        trades = []
        trade_num = 1
        for line in reader:

            if(line['Trade Type'] == 'BUY'):
                trade_profit -= Decimal(line['Price'])
            if(line['Trade Type'] == 'SELL'):
                trade_profit += Decimal(line['Price'])
                trades.append(trade_profit)
                print('Trade #{}: {}'.format(trade_num, trade_profit))
                total_profit += trade_profit
                trade_profit = 0
                trade_num += 1

        #print('Avg Trade: {}'.format(np.average(trades)))
        print('Total Profit: {}\n'.format(total_profit))

def return_book():
    with open('trade_history.csv', mode ='r') as File:
        book = csv.DictReader(File)
        return list(book)
