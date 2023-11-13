import requests
import pandas as pd
from dateutil.parser import *
from defs import OANDA_ACCOUNT_ID, OANDA_URL, OANDA_SECURE_HEADER
import json
from log_wrapper import LogWrapper
from datetime import datetime

class OandaAPI():
    log = LogWrapper('Oanda Bot', datetime.now())

    def __init__(self):
        self.session = requests.Session()

    def make_request(self, url, params={}, added_headers=None, verb='get', data=None, code_ok=200):
        headers = OANDA_SECURE_HEADER

        if added_headers is not None:   
            for k in added_headers.keys():
                headers[k] = added_headers[k]
                
        try:
            response = None
            if verb == 'post':
                response = self.session.post(url,params=params,headers=headers,data=data)
            elif verb == 'put':
                response = self.session.put(url,params=params,headers=headers,data=data)
            else:
                response = self.session.get(url,params=params,headers=headers,data=data)

            status_code = response.status_code

            if status_code == code_ok:
                json_response = response.json()
                return status_code, json_response
            else:
                return status_code, None   

        except:
            self.log.logger.error("make_request() : ERROR")
            return 400, None   

    def fetch_instruments(self):
        url = f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/instruments"
        status_code, data = self.make_request(url)
        return status_code, data
    
    def get_instruments_df(self):
        status_code, data = self.fetch_instruments()
        if status_code == 200:
            df = pd.DataFrame.from_dict(data['instruments'])
            return df[['name', 'type', 'displayName', 'pipLocation', 'marginRate']]
        else:
            return None
    
    def close_trade(self, trade_id):
        url = f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/trades/{trade_id}/close"
        status_code, json_data = self.make_request(url, verb='put', code_ok=200)
        if status_code != 200:
            return False
        return True

    def set_sl_tp(self, price, order_type, trade_id):
        url = f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/orders"
        data = {
            "order": {
                "timeInForce": "GTC",
                "price": str(price), 
                "type": order_type,
                "tradeID": str(trade_id)
            }
        }
        status_code, json_data = self.make_request(url, verb='post', data=json.dumps(data), code_ok=201)

        if status_code != 201:
            self.log.logger.error(f'set_sl_tp() : ERROR placing {order_type}\n{status_code = }\n{json_data = }')
            return False
        return True

    def place_trade(self, pair, units, SL, TP):
        url = f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/orders"
        data = {
            "order": {
                "units": units,
                "instrument": pair,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }
        status_code, json_data = self.make_request(url, verb='post', data=json.dumps(data), code_ok=201)
        if status_code != 201:
            self.log.logger.error(f'place_trade() : ERROR placing trade with params:\n{pair = }, {units = }, {SL = }, {TP = }')
            return None
        ok = True
        trade_id = None
        if "orderFillTransaction" in json_data and "tradeOpened" in json_data["orderFillTransaction"]:
            trade_id = int(json_data["orderFillTransaction"]["tradeOpened"]["tradeID"])
            if trade_id is None:
                self.log.logger.error(f'place_trade() : Error retreiving tradeID.\n{json_data["orderFillTransaction"]["tradeOpened"]}')
                return None, False
            if SL != -1:
                SL_ok = self.set_sl_tp(SL, 'STOP_LOSS', trade_id)
                ok = ok if SL_ok else SL_ok
            if TP != -1:
                TP_ok = self.set_sl_tp(TP, 'TAKE_PROFIT', trade_id)
                ok = ok if TP_ok else TP_ok
        else:
            self.log.logger.error(f'place_trade() : Error in json_data.\nMissing "orderFillTransaction" and "tradeOpened"\n{json_data = }')
        return trade_id, ok



if __name__ == "__main__":
    api = OandaAPI()


    