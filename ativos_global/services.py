import requests
import pandas as pd
from datetime import datetime, timedelta

# URL base da API brapi.dev
BRAPI_BASE_URL = "https://brapi.dev/api"

# Função auxiliar para fazer requisições à API brapi.dev
def _fetch_brapi_data(endpoint, params=None):
    url = f"{BRAPI_BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Levanta um HTTPError para códigos de status de erro (4xx ou 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao buscar dados da brapi.dev em {url}: {e}")
    except Exception as e:
        print(f"Erro inesperado ao processar dados da brapi.dev em {url}: {e}")
    return None

def get_stock_price(stock_code):
    """
    Fetches the last closing price for a given stock code using brapi.dev.
    """
    # brapi.dev não precisa de .SA
    endpoint = f"quote/{stock_code}"
    data = _fetch_brapi_data(endpoint)

    if data and 'results' in data and data['results']:
        # A API retorna uma lista de resultados, pegamos o primeiro para a cotação atual
        quote = data['results'][0]
        return quote.get('regularMarketPrice')
    return None

def get_stock_history(stock_code, period="1d", interval="15m"):
    """
    Fetches historical data for a given stock code using brapi.dev.
    brapi.dev uses 'interval' (1d, 5d, 1wk, 1mo, 3mo) and 'range' (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max).
    We need to map yfinance's period/interval to brapi.dev's range/interval.
    For simplicity, let's fetch 1 day of 15-minute data if possible, or 1 month of daily data.
    """
    # brapi.dev não precisa de .SA
    endpoint = f"quote/{stock_code}"
    
    # Mapeamento simplificado para brapi.dev
    # brapi.dev historical data is usually daily. For intraday, it's more complex or not directly available in free tier.
    # Let's adjust to get daily historical data for a reasonable period.

    # Para o gráfico, vamos buscar o histórico diário do último mês.
    # O endpoint /quote/{ticker} já retorna historicalDataPrice.
    params = {
        "range": "1mo", # Último mês
        "interval": "1d" # Dados diários
    }
    data = _fetch_brapi_data(endpoint, params=params)

    if data and 'results' in data and data['results']:
        historical_data = data['results'][0].get('historicalDataPrice')
        if historical_data:
            df = pd.DataFrame(historical_data)
            # Renomear colunas para corresponder ao formato esperado pelo Plotly/view
            df = df.rename(columns={
                'date': 'Datetime',
                'close': 'Close',
                'volume': 'Volume'
            })
            # Converter 'Datetime' para o formato de data/hora
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            # Filtrar para garantir que temos apenas os dados necessários
            df = df[['Datetime', 'Close', 'Volume']]
            return df
    return None