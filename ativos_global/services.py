import yfinance as yf
import requests
import urllib3

# Desabilitar avisos de SSL (MUITO INSEGURO - APENAS PARA DESENVOLVIMENTO/DEBUG)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey-patch requests para forçar verify=False (MUITO INSEGURO - APENAS PARA DESENVOLVIMENTO/DEBUG)
# Isso afeta todas as chamadas requests, incluindo as feitas internamente pelo yfinance
_original_get = requests.get
_original_post = requests.post
_original_request = requests.request

def _get_without_ssl_verify(url, **kwargs):
    kwargs['verify'] = False
    return _original_get(url, **kwargs)

def _post_without_ssl_verify(url, **kwargs):
    kwargs['verify'] = False
    return _original_post(url, **kwargs)

def _request_without_ssl_verify(method, url, **kwargs):
    kwargs['verify'] = False
    return _original_request(method, url, **kwargs)

requests.get = _get_without_ssl_verify
requests.post = _post_without_ssl_verify
requests.request = _request_without_ssl_verify

def get_stock_price(stock_code):
    """
    Fetches the last closing price for a given stock code.
    """
    try:
        ticker = yf.Ticker(f'{stock_code}.SA')
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
        ticker = yf.Ticker(f'{stock_code}.SA')
        df = ticker.history(period=period, interval=interval)
        return df.reset_index()
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão/SSL ao buscar histórico para {stock_code}: {e}")
    except Exception as e:
        print(f"Erro inesperado ao buscar histórico para {stock_code}: {e}")
        return None
