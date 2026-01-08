import yfinance as yf
import requests

def get_stock_price(stock_code):
    """
    Fetches the last closing price for a given stock code.
    """
    try:
        ticker = yf.Ticker(f'{stock_code}.SA') # Remover 'session=session'
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return data['Close'].iloc[-1]
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/SSL ao buscar preço para {stock_code}: {e}")
    except Exception as e:
        print(f"Erro inesperado ao buscar preço para {stock_code}: {e}")
    return None

def get_stock_history(stock_code, period="1d", interval="15m"):
    """
    Fetches historical data for a given stock code.
    """
    try:
        ticker = yf.Ticker(f'{stock_code}.SA') # Remover 'session=session'
        df = ticker.history(period=period, interval=interval)
        return df.reset_index()
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/SSL ao buscar histórico para {stock_code}: {e}")
    except Exception as e:
        print(f"Erro inesperado ao buscar histórico para {stock_code}: {e}")
        return None
