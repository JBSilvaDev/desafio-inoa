import yfinance as yf

def get_stock_price(stock_code):
    """
    Fetches the last closing price for a given stock code.
    """
    try:
        ticker = yf.Ticker(f'{stock_code}.SA')
        # Use '1d' period and a recent interval to get the latest data
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return data['Close'].iloc[-1]
    except Exception as e:
        print(f"Error fetching price for {stock_code}: {e}")
    return None

def get_stock_history(stock_code, period="1d", interval="15m"):
    """
    Fetches historical data for a given stock code.
    """
    try:
        ticker = yf.Ticker(f'{stock_code}.SA')
        df = ticker.history(period=period, interval=interval)
        return df.reset_index()
    except Exception as e:
        print(f"Error fetching history for {stock_code}: {e}")
        return None
