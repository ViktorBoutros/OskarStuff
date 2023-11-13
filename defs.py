#____CONSTANTS____#
SLEEP = 10.0                
BUY = 1
SELL = -1
NONE = 0
ANY_FILTER = ['BUY ', 'SELL ']
ALL_FILTER1 = ['SL ', 'TP1 ', 'TP2 ', 'TP3 ']
ALL_FILTER2 = ['SL:', 'TPs:']
UNITS = 1
PAIR_MAP = {
      "GOLD" : "XAU_USD",
      "NATGAS" : "NATGAS_USD",
      "US30" : "US30_USD",
      "NASDAQ" : "NAS100_USD",
      "JP225" :  "JP225_USD",
      "USOIL" : "BCO_USD",
      "DAX40" : "DE30_EUR"
    }
TP1 = 1
TP2 = 2
TP3 = 3
NILL = 0
SL = -1
CLOSE_VALUES = {
    1 : 'TP1',
    2 : 'TP2',
    3 : 'TP3',
    0 : 'NILL',
    -1 : 'SL'
}

#____OANDA____#
OANDA_API_KEY = '7dc9e24b33a1c114e6e5a51f0b2cb3bf-d50750fa05f6cc8fc6e25fc1c596a4c2'
OANDA_ACCOUNT_ID = '101-004-26331293-001'
OANDA_URL = 'https://api-fxpractice.oanda.com/v3'
OANDA_SECURE_HEADER = {
    'Authorization': f'Bearer {OANDA_API_KEY}',
    'Content-Type': 'application/json'
}

#____TELEGRAM____#
TELEGRAM_API_KEY = "a339ccd5fdcc7542d6424053553fbd99" 
TELEGRAM_API_ID = "24542398"
TELEGRAM_APP_TITLE = "OskarsMessageParser"
TELEGRAM_SHORT_NAME = "OskarsMessageParser"
TELEGRAM_SESSION_NAME = 'MessageParser'

#____EMAIL_DETAILS____#
SENDER = 'tradingbot337@gmail.com'
PASSWORD = 'hvcp ivqh aqph adog'
RECIEVER = 'vibou11@gmail.com'





