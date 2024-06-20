from sdk import SDK100x
from pandas_ta import sma
from time import sleep

if __name__ == "__main__":
    dex = SDK100x()
    symbol = "solperp"

    length_dc = 90
    length_dc_sma= 60
    length_sma= 10

    while True:
        print("wait data...")
        # sleep(60)
        df = dex.get_candlestick_dataframe(symbol=symbol, interval="1h", length=length_dc+length_dc_sma)

        hh = df["h"].rolling(window=length_dc_sma, min_periods=1).max()
        ll = df["l"].rolling(window=length_dc_sma, min_periods=1).min()
        
        hh_sma = sma(hh, length_dc_sma)
        ll_sma = sma(ll, length_dc_sma)
        mm = (hh_sma + ll_sma) / 2

        close_sma = sma(df["c"], length = length_sma)  

        position_size = int(dex.get_positions(symbol)["quantity"])

        if position_size == 0:
            longCondition = dex.crossover(close_sma, hh)    
            shortCondition = dex.crossunder(close_sma, ll)

            balance = dex.get_actual_balance_by_symbol(symbol)

            if longCondition:
                amount = balance/10
                dex.open_market(symbol, amount, True)
            if shortCondition:
                amount = balance/10
                dex.open_market(symbol, amount, False)
        else:
            if position_size > 0:
                if float(dex.get_market_price(symbol)) > float(mm[len(mm)-1]):
                    dex.open_market(symbol, abs(position_size), True)
            elif position_size < 0:
                if float(dex.get_market_price(symbol)) < float(mm[len(mm)-1]):
                    dex.open_market(symbol, abs(position_size), True)
        print("sleep 1h ...")
        sleep(dex.seconds_until_next_hour())


