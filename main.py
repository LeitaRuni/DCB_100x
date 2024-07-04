from sdk import SDK100x
from pandas_ta import sma
from time import sleep

if __name__ == "__main__":
    dex = SDK100x()
    symbol = "ethperp"

    length_dc = 15
    length_dc_sma = 15
    length_sma= 5

    while True:
        try:
            # print("wait data...")
            # sleep(60)
            df = dex.get_candlestick_dataframe(symbol=symbol, interval="15m", length=length_dc+length_dc_sma)

            hh = df["h"].rolling(window=length_dc_sma, min_periods=1).max()
            ll = df["l"].rolling(window=length_dc_sma, min_periods=1).min()
            
            hh_sma = sma(hh, length_dc_sma)
            ll_sma = sma(ll, length_dc_sma)
            mm = (hh_sma + ll_sma) / 2

            close_sma = sma(df["c"], length = length_sma)  

            print("high line", hh_sma[len(hh_sma)-1])
            print("mid line", mm[len(mm)-1])
            print("low line", ll_sma[len(ll_sma)-1])
            print("close_sma", close_sma[len(close_sma)-1])

            positions = dex.get_positions(symbol)
            
            if len(positions) == 0:
                position_size = 0
            else:
                position_size = int(positions[0]["quantity"])

            if position_size == 0:
                # longCondition = dex.crossover(close_sma, hh)    
                # shortCondition = dex.crossunder(close_sma, ll)
                longCondition = close_sma[len(close_sma)-1] > hh[len(hh)-1]    
                shortCondition = close_sma[len(close_sma)-1] < mm[len(ll)-1]    

                balance = dex.get_actual_balance_by_symbol(symbol)

                if longCondition:
                    amount = int(balance/2)
                    dex.open_market(symbol, amount, True)
                if shortCondition:
                    amount = int(balance/2)
                    dex.open_market(symbol, amount, False)
            else:
                if position_size > 0:
                    if float(dex.get_market_price(symbol)) < float(mm[len(mm)-1]):
                        dex.open_market(symbol, abs(position_size), False)
                elif position_size < 0:
                    if float(dex.get_market_price(symbol)) > float(mm[len(mm)-1]):
                        dex.open_market(symbol, abs(position_size), True)
            # sleep_time = dex.seconds_until_next_hour() 
            sleep_time = dex.seconds_until_next_15_min_frame()
            print(f"sleep {sleep_time} ...")
            sleep(sleep_time)
        except:
            print("global error...")
            sleep(60)
