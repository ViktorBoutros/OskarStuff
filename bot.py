from log_wrapper import LogWrapper
from oanda_api import OandaAPI
from defs import *
from datetime import datetime
from telethon import TelegramClient, events
from utils import any_in, all_in


class TradingBot():
    
    def __init__(self):    
        self.start_time = datetime.now()
        self.log = LogWrapper(f"Bot", datetime.today())
        self.trade_log = LogWrapper(f"Trade Messages", self.start_time)
        self.nontrade_log = LogWrapper(f"Other Messages", self.start_time)
        self.trade_pairs = PAIR_MAP.values()
        self.oanda_api = OandaAPI()
        self.trades = {}

    def log_message(self, msg):
        self.log.logger.debug(msg) 

    def log_error(self, msg):
        self.log.logger.error(msg)
    
    def log_warning(self, msg):
        self.log.logger.warning(msg)
        open_trades, ok = self.oanda_api.open_trades()
        if ok == False:
            subject = "WARNING: CANNOT CLOSE TRADES"
            body = f"Failed to fetch open trades {pairs_to_close}"
            self.log_error(f"{subject}\n{body}")
            send_email(subject, body)
            return
        
        ids_to_close = [x.trade_id for x in open_trades if x.instrument in pairs_to_close]
        self.log_message(f"close_trades() pairs_to_close:{pairs_to_close} ")
        self.log_message(f"close_trades() open_trades:{open_trades} ")
        self.log_message(f"close_trades() ids_to_close:{ids_to_close} ")
        
        for t in ids_to_close:
            ok = self.api.close_trade(t)
            if ok == False:
                subject = "WARNING: CANNOT CLOSE TRADE"
                body = f"Failed to close trade {t}"
                self.log_error(f"{subject}\n{body}")
                send_email(subject, body)
            else:
                self.log_message(f"close_trades() Closed {t}")

    def create_trade(self, t):
        self.log_message(f'create_trade(): Starting with {t = }')
        trade_id, ok = self.oanda_api.place_trade(t['pair'], t['units'], t['SL'], t['TP'])
        if trade_id is not None:
            self.log_message(f"Opened trade {trade_id} : {t}")
            if not ok:
                self.log_error(f'Error placing TP or SL\n{ok = }')
        else:
            self.log_error(f"Error. FAILED to open trade.")
        return trade_id

    def parse_message(self, s):
        self.log_message(f'parsing msg {s = }')
        lines = s.split("\n")
        if len(lines) == 1:
            line = s.split(' ')
        else:
            self.log_error(f'Error getting 2 lines: {lines = }\n{s = }')
            return None
        trade = {}
        if "BUY" in line:
            trade['units'] = UNITS
        elif "SELL" in line:
            trade['units'] = -UNITS
        else:
            self.log_error(f'Error fetching units:\n{line = }')
            return None
        found = False
        for key in PAIR_MAP.keys():
            if key in line:
                trade['pair'] = PAIR_MAP[key]
                found = True
        if not found:
            self.log_error(f'Error fetching pair:\n{line = }\n{PAIR_MAP = }')
            return None
        idx = None
        tp = 'TPs:'
        try:
            if tp not in line:
                self.log_error(f'Error fetching TP. <{tp}> not in line.\n{line = }')
                return None
            idx = line.index(tp) + 1
            trade['TP'] = float(line[idx])
        except:
            self.log_error(f'Error fetching TP.\n{line = }\n{idx = }\n{line[idx] = }')
            return None
        idx = None
        sl = 'SL:'
        try:
            if sl not in line:
                self.log_error(f'Error fetching SL. <{sl}> not in line.\n{line = }')
                return None
            idx = line.index(sl) + 1
            trade['SL'] = float(line[idx])
        except:
            self.log_error(f'Error fetching SL.\n{line = }\n{idx = }\n{line[idx] = }')
            return None
        if trade['pair'] is None or trade['units'] is None or trade['TP'] is None or trade['SL'] is None:
            self.log_error(f'Message parsing failed.\n{trade = }')
            return None
        self.log_message(f'Message parsing successful.\n{trade = }')
        return trade
  
                


if __name__ == "__main__":
    print('Start')
    b = TradingBot()
    client = TelegramClient(TELEGRAM_SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_KEY)

    #____Unit_tests______
    b.log_message('Starting Tests...')
    test = '🆕 BUY JP225 @ 31500 / TPs: 31700 - 31900 - 32100 / SL: 31300'
    trade = b.parse_message(test)
    assert(trade['pair'] == 'JP225_USD')
    assert(trade['units'] == 1)
    assert(trade['SL'] == 31300)
    assert(trade['TP'] == 31700)

    test = '🆕 SELL USOIL @ 81.50 / TPs: 80.00 - 79.00 - 77.50 / SL: 83.00'
    trade = b.parse_message(test)
    assert(trade['pair'] == 'BCO_USD')
    assert(trade['units'] == -1)
    assert(trade['SL'] == 83.00)
    assert(trade['TP'] == 80.00)
    b.log_message('All tests passed!\n')
    #_____________________
    print('Tests passed. Awaiting messages...')
    
    @client.on(events.NewMessage)
    async def my_event_handler(event):
        b.log_message(f'Recieved message: {event.raw_text}')
        is_msg2 = any_in(event.raw_text, ANY_FILTER) and all_in(event.raw_text, ALL_FILTER2) and any_in(event.raw_text, list(PAIR_MAP.keys()))
        if is_msg2:
            print('Trade recieved')
            b.log_message(f'Creating trade...')
            trade = b.parse_message(event.raw_text)
            if trade is None:
                b.log_error(f'Error. FAILED trade parsing of string\n{event.raw_text = }')
                b.nontrade_log.logger.warning(event.raw_text)
                print('Fail')
            else:
                b.log_message(f'Placing trade: {trade}')
                if b.create_trade(trade) is None:
                    b.log_error(f'Error. Failed creating the trade\n{trade = }')
                    b.trade_log.logger.error(f'FAIL: {event.raw_text}\n{trade}')
                    print('Fail')
                else:
                    b.log_message(f'Successfully placed trade\n{trade = }')
                    b.trade_log.logger.debug(f'SUCCESS: {event.raw_text}\n{trade}')
                    print('Success')
        else:
            b.nontrade_log.logger.debug(event.raw_text)
    client.start()
    client.run_until_disconnected()  

