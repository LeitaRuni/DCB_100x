from requests import get, post
from pandas import DataFrame, to_datetime
from decouple import config
from eth_utils import to_hex
from eth_account import Account
from eth_account.messages import encode_typed_data 
from time import time
from math import ceil
from datetime import datetime as dt, timedelta as td
import constants as CONST

class SDK100x:
    def __init__(self):
        self.PRICE_DECIMALS = 1e18
        self.url = "https://api.100x.finance/v1"
        self.domain = {
            "name": "100x",
            "version": "0.0.0",
            "chainId": 81457,
            "verifyingContract": "0x691a5fc3a81a144e36c6C4fBCa1fC82843c80d0d"
        }
        self.private_key = config("PRIVATE_KEY")
        self.account = Account.from_key(self.private_key)
        self.public_key = self.account.address
        self.sub_account_id = 0

    # POST #

    def open_market(self, symbol: str, quantity: int, isBuy: bool):
        if (isBuy):
            side = "asks"
        else:
            side = "bids"
        message = {
                "account": self.public_key,
                "subAccountId": self.sub_account_id,
                "productId": self.get_product(symbol)["id"],
                "isBuy": isBuy,
                "orderType": CONST.MARKET,
                "timeInForce": CONST.FOK,
                "expiration": int((time()+10) * 1000),
                "price": self.get_order_book(symbol)[side][1][0],
                "quantity": str(quantity),
                "nonce": int(time() * 1000)
        }

        full_message = {
            "primaryType": "Order",
            "types": {
                "EIP712Domain": CONST.EIP712_TYPES["EIP712Domain"],
                "Order": CONST.EIP712_TYPES["Order"],
            },
            "domain": self.domain,
            "message": message
        }

        signable_message = encode_typed_data(full_message=full_message)
        signed_message = Account.sign_message(signable_message, self.private_key)

        message["signature"] = to_hex(signed_message.signature)

        response = post(f"{self.url}/order", json=message)

        print(response.text)

    # GET #

    def get_list_products(self):
        url = f"{self.url}/products"
        headers = {"accept": "application/json"}
        return get(url, headers=headers).json()

    def get_product(self, symbol: str):
        url = f"{self.url}/products/{symbol}"
        headers = {"accept": "application/json"}
        return get(url, headers=headers).json()
    
    def get_candlestick(self, symbol: str, interval: str,limit: int, startTime: int, endTime: int):
        params = {
            "symbol": symbol, 
            "interval": interval, 
            "limit":limit, 
            "startTime": startTime, 
            "endTime": endTime
        }
        return get(f"{self.url}/uiKlines", params=params).json()

    def get_candlestick_dataframe(self, symbol: str, interval: str, length: int):
        endTime = int(time()*1000)
        startTime = int((endTime - (CONST.SECONDS_PER_TIMESTAMP[interval] * length*1000)))
        number_of_iterations = ceil(length/CONST.LIMITS_PER_TIMESTAMP[interval])
        all_data = []

        for i in range(number_of_iterations): 
            limit = CONST.LIMITS_PER_TIMESTAMP[interval]
            endTime = startTime + (limit * CONST.SECONDS_PER_TIMESTAMP[interval]*1000) 
            print(f"loading data {i}/{number_of_iterations}", "start", dt.fromtimestamp(startTime/1000), "end", dt.fromtimestamp(endTime/1000))
            data = self.get_candlestick( 
                symbol=symbol, 
                interval=interval, 
                limit=limit,
                startTime=startTime, 
                endTime=endTime
            )
            all_data += data
            startTime = endTime

        df = DataFrame(all_data)
        df["datetime"] = to_datetime(df["E"], unit="ms")
        df["o"] = df["o"].apply(lambda x: float(x) / 1e18) 
        df["h"] = df["h"].apply(lambda x: float(x) / 1e18) 
        df["l"] = df["l"].apply(lambda x: float(x) / 1e18) 
        df["c"] = df["c"].apply(lambda x: float(x) / 1e18) 
        return df
    
    def get_balance(self): 
        message = {
            "account": self.public_key,
            "subAccountId": self.sub_account_id
        }

        full_message = {
            "primaryType": "SignedAuthentication",
            "types": {
                "EIP712Domain": CONST.EIP712_TYPES["EIP712Domain"],
                "SignedAuthentication": CONST.EIP712_TYPES["SignedAuthentication"],
            },
            "domain": self.domain,
            "message": message
        }

        signable_message = encode_typed_data(full_message=full_message)
        signed_message = Account.sign_message(signable_message, self.private_key)
        message["signature"] = to_hex(signed_message.signature)

        return get(url=f"{self.url}/balances", params=message).json()[0]
    
    def get_positions(self, symbol: str): 
        message = {
            "account": self.public_key,
            "subAccountId": self.sub_account_id,
            "symbol": symbol
        }

        full_message = {
            "primaryType": "SignedAuthentication",
            "types": {
                "EIP712Domain": CONST.EIP712_TYPES["EIP712Domain"],
                "SignedAuthentication": CONST.EIP712_TYPES["SignedAuthentication"],
            },
            "domain": self.domain,
            "message": message
        }

        signable_message = encode_typed_data(full_message=full_message)
        signed_message = Account.sign_message(signable_message, self.private_key)
        message["signature"] = to_hex(signed_message.signature)

        return get(url=f"{self.url}/positionRisk", params=message).json()
    
    def get_market_price(self, symbol: str):
        return float(self.get_product(symbol)["markPrice"])/self.PRICE_DECIMALS
    
    def get_actual_balance(self):
        return float(self.get_balance()["quantity"])/self.PRICE_DECIMALS
    
    def get_actual_balance_by_symbol(self, symbol: str):
        balance = self.get_actual_balance()
        price = self.get_market_price(symbol)
        print(balance)
        print(price)
        return int(round(balance/price,2)*1e18)
    
    def get_order_book(self, symbol: str):
        url = f"{self.url}/depth?symbol={symbol}&granularity=10&limit=5"
        return get(url).json()
    
    # TRIGGER #

    def crossover(self, df_1, df_2):
        return True if df_1[len(df_1)-1]> df_2[len(df_2)-1] and df_1[len(df_1)-2]< df_2[len(df_2)-2] else False 

    def crossunder(self, df_1, df_2):
        return True if df_1[len(df_1)-1]< df_2[len(df_2)-1] and df_1[len(df_1)-2]> df_2[len(df_2)-2] else False 
    
    def seconds_until_next_hour(self):
        now = dt.now()
        next_hour = (now + td(hours=1)).replace(minute=0, second=0, microsecond=0)
        delta = next_hour - now
        return int(delta.total_seconds())
    

if __name__ == "__main__":
    dex = SDK100x()

    symbol = "ethperp"

    # a = dex.get_list_products()
    # for i in a:
        # print(i)

    # balance = dex.get_actual_balance_by_symbol(symbol)
    # amount = int(balance/2)
    # print(amount/1e18)
    # print(amount)
    # dex.open_market(symbol, amount, True)


    positions = dex.get_positions(symbol)
    if len(positions) == 0:
        position_size = 0
    else:
        position_size = int(positions[0]["quantity"])

    print(position_size)
    print(position_size/1e18)
    dex.open_market(symbol, abs(position_size), False)