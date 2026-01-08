import requests
import pandas as pd
from datetime import datetime, timedelta
from django.conf import settings # Importar settings para acessar a chave da API

# URL base da API brapi.dev
BRAPI_BASE_URL = "https://brapi.dev/api"

# Função auxiliar para fazer requisições à API brapi.dev
def _fetch_brapi_data(endpoint, params=None):
    url = f"{BRAPI_BASE_URL}/{endpoint}"
    headers = {}
    # Adicionar a chave da API se estiver configurada
    api_key = getattr(settings, 'BRAPI_API_KEY', None)
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        # Usar verify=False conforme testado pelo usuário para contornar o problema SSL
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
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
    endpoint = f"quote/{stock_code}"
    data = _fetch_brapi_data(endpoint)

    if data and 'results' in data and data['results']:
        quote = data['results'][0]
        return quote.get('regularMarketPrice')
    return None

def get_stock_history(stock_code, period="1d", interval="15m"):
    """
    Fetches historical data for a given stock code using brapi.dev.
    """
    endpoint = f"quote/{stock_code}"
    
    params = {
        "range": "3mo", # Últimos 3 meses
        "interval": "1d" # Dados diários
    }
    data = _fetch_brapi_data(endpoint, params=params)

    if data and 'results' in data and data['results']:
        historical_data = data['results'][0].get('historicalDataPrice')
        if historical_data:
            df = pd.DataFrame(historical_data)
            df = df.rename(columns={
                'date': 'Datetime',
                'close': 'Close',
                'volume': 'Volume'
            })
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df = df[['Datetime', 'Close', 'Volume']]
            return df
    return None
