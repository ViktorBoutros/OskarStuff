import numpy as np
import pandas as pd
from defs import *
import json
from utils import any_in, all_in

# Constants
SL = -1
NILL = 0
TP1 = 1
TP2 = 2
TP3 = 3
CLOSE_VALUES = {
    1 : 'TP1',
    2 : 'TP2',
    3 : 'TP3',
    0 : 'Price',
    -1 : 'SL'
}
DISPLAY_CLOSE_VALUES = {
    1 : 'TP1',
    2 : 'TP2',
    3 : 'TP3',
    0 : 'None',
    -1 : 'SL'
}

def load_json(file):
    with open(file) as json_file:
        return json.load(json_file)

def make_trades(data):
    trades = []
    other = []
    for d in data:
        try: 
           msg = d['message']
        except:
            continue
        if any_in(msg, ANY_FILTER) and all_in(msg, ALL_FILTER2) and any_in(msg, list(PAIR_MAP.keys())):
            trades.append(d)
        else:
            other.append(d)
    return trades, other

def make_repliesMap(trades, other):
    repliesMap = dict()
    for trade in trades:
        replies = []
        for response in other:
            if response['reply_to'] is None:
                continue
            id = response['reply_to']['reply_to_msg_id']

            if id == trade['id']:
                replies.append(response['message'])
        repliesMap[trade['message']] = replies
    return repliesMap

def process_replies(replies):
    result = SL
    for reply in replies:
        if len(reply) < 3:
            continue
        if reply[:2] == 'TP':
            result = max(float(reply[2]), result)
            continue
        if reply[:2] == 'SL':
            return SL
        if len(reply) < 18:
            continue
        if reply[:12] == "Trade closed":
            if "@" in reply and reply[reply.index("@") +  2 : reply.index("@") +  4] == "TP": 
                return max(float(reply[reply.index("@") +  4]), result)
            else:
                return NILL
    return result
    
        
def get_close_value(trade, repliesMap):
    return process_replies(repliesMap[trade['message']])

def process_trade(trade, close_value):
    df = {}
    t = trade['message'].split(' ')
    SL_done = False
    if 'SL:' not in t:
        for k, word in enumerate(t):

            if "SL:" in word:
                df['SL'] = float(word[3:])
                i1 = k - 1
                SL_done = True

    df['Direction'] = t[1]
    df['Instrument'] = t[2]
    df['Price'] = float(t[t.index('@') + 1])

    if not SL_done:
        try:
            i1 = t.index('SL:') - 1 # exclusive
        except:
            print(t)

    i0 = t.index('TPs:') + 1 # inclusive
    k = 1
    for TP in t[i0:i1]:
        if TP.replace(".", "").isnumeric():
            df[f'TP{k}'] = float(TP)
            k += 1


    if not SL_done and t[i1 + 2].replace(".", "").isnumeric():
        df['SL'] = float(t[i1 + 2])

    df['Close Value'] = DISPLAY_CLOSE_VALUES[close_value]

    if 'SL' not in df:
        df['Cash Flow'] = 0
    else:
        df['Cash Flow'] = df[CLOSE_VALUES[close_value]] - df['Price'] if df['Direction'] == 'BUY' else -df[CLOSE_VALUES[close_value]] + df['Price']


    df['Cash Flow %'] = df['Cash Flow'] / df['Price']
    return df

def build_table(json_file):
    df = pd.DataFrame(columns=['Direction', 'Instrument', 'Price', 'SL', 'TP1', 'TP2', 'TP3', 'TP4', 'Close Value', 'Cash Flow', 'Cash Flow %'])

    data = load_json(json_file)

    trades, other = make_trades(data)

    repliesMap = make_repliesMap(trades, other)

    for trade in trades:
        close_value = get_close_value(trade, repliesMap)
        df = df.append(process_trade(trade, close_value), ignore_index=True)

    return df

def profit_per_instrument(df):
    return df.groupby(['Instrument'])['Cash Flow %'].mean()

if __name__ == "__main__":
    df = build_table("channel_messages.json")


