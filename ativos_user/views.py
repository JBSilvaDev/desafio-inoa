from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.messages import constants
from django.conf import settings
import requests
import json
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.core.cache import cache # Adicionado
from .utils.cache import cache_get_or_set # Adicionado

from .models import Ativo, AtivosUser, PrecoAtivo # Importar o novo modelo Ativo e PrecoAtivo
from .forms import AtivoUserForm

# Funções para buscar dados da API (adaptadas de ativos_global/services.py)
def get_stock_data(stock_code):
    api_key = settings.BRAPI_API_KEY
    url = f"https://brapi.dev/api/quote/{stock_code}" # Remover token da URL
    headers = {"Authorization": f"Bearer {api_key}"} # Adicionar Authorization header
    
    print(f"Chamando API para dados atuais: {url} com headers: {headers}") # Adicionar print da URL
    
    try:
        response = requests.get(url, headers=headers, verify=False) # Usar headers
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        if data and data['results']:
            stock_info = data['results'][0]
            return {
                'symbol': stock_info.get('symbol'),
                'shortName': stock_info.get('shortName'),
                'longName': stock_info.get('longName'),
                'currency': stock_info.get('currency'),
                'regularMarketPrice': stock_info.get('regularMarketPrice'),
                'regularMarketChange': stock_info.get('regularMarketChange'),
                'regularMarketChangePercent': stock_info.get('regularMarketChangePercent'),
                'regularMarketDayHigh': stock_info.get('regularMarketDayHigh'),
                'regularMarketDayLow': stock_info.get('regularMarketDayLow'),
                'regularMarketOpen': stock_info.get('regularMarketOpen'),
                'regularMarketPreviousClose': stock_info.get('regularMarketPreviousClose'),
                'regularMarketVolume': stock_info.get('regularMarketVolume'),
                'marketCap': stock_info.get('marketCap'),
                'logourl': stock_info.get('logourl'),
            }
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API para {stock_code}: {e}")
        return {'error': f"Erro ao buscar dados atuais da brapi para {stock_code}: {e}"}
    return {'error': f"Nenhum dado encontrado para {stock_code} na brapi."}

def get_stock_history(stock_code, range_param='1mo', interval_param='1d'):
    api_key = settings.BRAPI_API_KEY
    url = f"https://brapi.dev/api/quote/{stock_code}?range={range_param}&interval={interval_param}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print(f"Chamando API para histórico: {url} com headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Erro de decodificação JSON para {stock_code}. Resposta da API: {response.text}")
            return []
        
        if data and data.get('results') and data['results'][0].get('historicalDataPrice'):
            historical_data = data['results'][0]['historicalDataPrice']
            return [
                {'date': item['date'], 'close': item['close']}
                for item in historical_data if 'close' in item and 'date' in item
            ]
        else:
            error_message = f"Dados históricos vazios ou malformados para {stock_code}. Resposta da API: {data}"
            print(error_message)
            return {'error': error_message}
    except requests.exceptions.RequestException as e:
        error_message = f"Erro ao buscar histórico da API para {stock_code}: {e}"
        print(error_message)
        return {'error': error_message}
    return {'error': f"Nenhum dado histórico encontrado para {stock_code} na brapi."}

# --- Funções cacheadas para Alpha Vantage ---
def _av_build_quote(stock_code):
    return get_stock_data_alpha_vantage(stock_code)

def _av_build_history(stock_code, interval_param):
    return get_stock_history_alpha_vantage(stock_code, interval_param)

def av_get_quote_cached(stock_code, ttl=60):  # 60s para quote “atual”
    key = f"av:quote:{stock_code.upper()}"
    return cache_get_or_set(key, lambda: _av_build_quote(stock_code), ttl)[0]

def av_get_history_cached(stock_code, interval_param, ttl_map=None):
    if ttl_map is None:
        ttl_map = {"60min": 15*60, "1d": 60*60, "1wk": 2*60*60, "1mo": 6*60*60}
    ttl = ttl_map.get(interval_param, 60*60)
    key = f"av:hist:{stock_code.upper()}:{interval_param}"
    return cache_get_or_set(key, lambda: _av_build_history(stock_code, interval_param), ttl)[0]






@login_required(login_url='login')
def carteira(request): # Renomeado de favoritos para carteira
    user = request.user
    busca = request.GET.get('cod-ativo')
    
    # Filtrar apenas ativos que estão "em_carteira"
    if busca:
        ativos_list = AtivosUser.objects.filter(
            Q(ativo__cod_ativo__icontains=busca) | Q(ativo__nome_empresa__icontains=busca),
            user=user,
            em_carteira=True # Filtrar por em_carteira
        )
    else:
        ativos_list = AtivosUser.objects.filter(user=user, em_carteira=True) # Filtrar por em_carteira

    # Para cada ativo, crie uma instância do formulário
    for ativo in ativos_list:
        ativo.form = AtivoUserForm(instance=ativo)

    paginacao = Paginator(ativos_list, 10)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    
    return render(request, 'favoritos.html', {'ativos': ativos_por_pagina, "favorito": True}) # Renderizar o template 'favoritos.html' por enquanto

@login_required(login_url='login')
def favoritos(request): # Nova view para favoritos
    user = request.user
    busca = request.GET.get('cod-ativo')
    
    # Filtrar apenas ativos que estão "favorito"
    if busca:
        ativos_list = AtivosUser.objects.filter(
            Q(ativo__cod_ativo__icontains=busca) | Q(ativo__nome_empresa__icontains=busca),
            user=user,
            favorito=True # Filtrar por favorito
        )
    else:
        ativos_list = AtivosUser.objects.filter(user=user, favorito=True) # Filtrar por favorito

    # Para cada ativo, crie uma instância do formulário
    for ativo in ativos_list:
        ativo.form = AtivoUserForm(instance=ativo)

    paginacao = Paginator(ativos_list, 10)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    
    return render(request, 'favoritos.html', {'ativos': ativos_por_pagina, "favorito": True}) # Renderizar o template 'favoritos.html' por enquanto

@login_required(login_url='login')
def home_ativos(request): # Nova view para a Home
    user = request.user
    busca = request.GET.get('cod-ativo')
    
    if busca:
        ativos_list = AtivosUser.objects.filter(
            Q(ativo__cod_ativo__icontains=busca) | Q(ativo__nome_empresa__icontains=busca),
            user=user,
        )
    else:
        ativos_list = AtivosUser.objects.filter(user=user) # Listar todos os ativos do usuário

    # Para cada ativo, crie uma instância do formulário
    for ativo in ativos_list:
        ativo.form = AtivoUserForm(instance=ativo)

    paginacao = Paginator(ativos_list, 10)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    
    return render(request, 'home_ativos.html', {'ativos': ativos_por_pagina})

def get_stock_data_alpha_vantage(stock_code):
    api_key = settings.ALPHA_VANTAGE_API_KEY
    # Adicionar sufixo .SA para ações brasileiras
    if not stock_code.endswith('.SA'):
        stock_code += '.SA'
        
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_code}&apikey={api_key}"
    print(f"Chamando API Alpha Vantage para dados atuais: {url}")
    
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()
        
        quote = data.get('Global Quote')
        if quote:
            return {
                'symbol': quote.get('01. symbol'),
                'regularMarketPrice': quote.get('05. price'),
                'regularMarketChange': quote.get('09. change'),
                'regularMarketChangePercent': quote.get('10. change percent'),
                'regularMarketVolume': quote.get('06. volume'),
            }
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da Alpha Vantage para {stock_code}: {e}")
    return None

def get_stock_history_alpha_vantage(stock_code, interval_param='60min'):
    api_key = settings.ALPHA_VANTAGE_API_KEY
    if not stock_code.endswith('.SA'):
        stock_code += '.SA'

    function_base = ''
    interval = ''
    
    # Mapeamento de funções e chaves de série temporal
    function_map = {
        '60min': {'function': 'TIME_SERIES_INTRADAY', 'interval': '60min', 'key_suffix': '(60min)', 'close_key': '4. close', 'volume_key': '5. volume', 'date_format': '%Y-%m-%d %H:%M:%S'},
        '1d': {'function': 'TIME_SERIES_DAILY', 'key_suffix': '(Daily)', 'close_key': '4. close', 'volume_key': '5. volume', 'date_format': '%Y-%m-%d'},
        '1wk': {'function': 'TIME_SERIES_WEEKLY', 'key_suffix': 'Weekly Time Series', 'close_key': '4. close', 'volume_key': '5. volume', 'date_format': '%Y-%m-%d'},
        '1mo': {'function': 'TIME_SERIES_MONTHLY', 'key_suffix': 'Monthly Time Series', 'close_key': '4. close', 'volume_key': '5. volume', 'date_format': '%Y-%m-%d'},
    }

    config = function_map.get(interval_param)
    if not config:
        return {'error': 'Intervalo de tempo inválido para Alpha Vantage.'}

    function_base = config['function']
    interval = config.get('interval', '')
    date_format = config['date_format']
    close_key = config['close_key']
    volume_key = config['volume_key']

    url = f"https://www.alphavantage.co/query?function={function_base}&symbol={stock_code}&apikey={api_key}"
    if interval:
        url += f"&interval={interval}"
    
    print(f"Chamando API Alpha Vantage para histórico ({function_base}): {url}")

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()

        print(f"Resposta completa da Alpha Vantage para {stock_code} ({function_base}): {json.dumps(data, indent=2)}")

        if 'Information' in data or 'Error Message' in data: # Modificado aqui
            # tenta fallback do cache para não quebrar a página
            key = f"av:hist:{stock_code.upper()}:{interval_param}"
            cached = cache.get(key)
            if cached:
                print(f"Retornando dados históricos do cache para {stock_code} ({interval_param}) devido a erro da API.")
                return cached
            error_message = f"Erro da API Alpha Vantage: {data.get('Information') or data.get('Error Message')}"
            print(error_message)
            return {'error': error_message}

        # Tentar encontrar a chave da série temporal
        time_series_key = None
        if function_base == 'TIME_SERIES_INTRADAY':
            time_series_key = f'Time Series ({interval})'
        elif 'DAILY' in function_base:
            time_series_key = 'Time Series (Daily)'
        elif 'WEEKLY' in function_base:
            time_series_key = 'Weekly Time Series'
        elif 'MONTHLY' in function_base:
            time_series_key = 'Monthly Time Series'
        
        if not time_series_key or time_series_key not in data:
            error_message = f"Nenhuma chave de série temporal encontrada na resposta da Alpha Vantage para {stock_code}. Resposta: {data}"
            print(error_message)
            return {'error': error_message}

        historical_data = data[time_series_key]
        
        parsed_data = []
        for date_str, item in historical_data.items():
            try:
                timestamp = int(datetime.strptime(date_str, date_format).timestamp())
                close_price = float(item[close_key])
                volume = int(item[volume_key])
                parsed_data.append({'date': timestamp, 'close': close_price, 'volume': volume})
            except (ValueError, KeyError) as e:
                print(f"Erro ao processar item de histórico para {stock_code} ({date_str}): {e}")
                continue
        
        # A API Alpha Vantage retorna os dados em ordem decrescente de data, precisamos inverter
        parsed_data.reverse()
        return parsed_data

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        error_message = f"Erro ao buscar ou processar histórico da Alpha Vantage para {stock_code}: {e}"
        print(error_message)
        return {'error': error_message}

@login_required(login_url='login')
def detalhes_ativo(request, ativo_user_id):
    ativo_user = get_object_or_404(AtivosUser, id=ativo_user_id, user=request.user)
    cod_ativo = ativo_user.ativo.cod_ativo
    
    api_source = request.GET.get('api', 'brapi')
    range_param = request.GET.get('range', '1mo')
    interval_param = request.GET.get('interval', '1d')

    if api_source == 'alpha':
        stock_data = av_get_quote_cached(cod_ativo, ttl=60)  # evita múltiplas chamadas
        historical_data_result = av_get_history_cached(cod_ativo, interval_param)
        
        if isinstance(historical_data_result, dict) and historical_data_result.get('error'):
            chart_data = {'error': historical_data_result['error']}
            historical_data = [] # Garante que historical_data seja uma lista
        else:
            historical_data = historical_data_result
            chart_data = {
                'x': [item['date'] for item in historical_data],
                'y': [item['close'] for item in historical_data],
                'title': f'Histórico de Preços de {cod_ativo}',
            }
    else: # Padrão é brapi
        stock_data_result = get_stock_data(cod_ativo)
        historical_data_result = get_stock_history(cod_ativo, range_param, interval_param)

        stock_data = None
        historical_data = []
        chart_data = {}

        if isinstance(stock_data_result, dict) and stock_data_result.get('error'):
            stock_data = {'error': stock_data_result['error']}
            chart_data = {'error': stock_data_result['error']} # Propaga o erro para o gráfico também
        else:
            stock_data = stock_data_result

        if isinstance(historical_data_result, dict) and historical_data_result.get('error'):
            historical_data = []
            chart_data = {'error': historical_data_result['error']} # Sobrescreve se houver erro no histórico
        else:
            historical_data = historical_data_result
            
            # Atualiza o preço da tabela com o último preço de fechamento do histórico para consistência
            if historical_data:
                latest_close_price = historical_data[-1]['close']
                if stock_data and not stock_data.get('error'): # Só atualiza se stock_data não tiver erro
                    stock_data['regularMarketPrice'] = latest_close_price
                elif not stock_data: # Se stock_data for None, cria um dicionário básico com o preço
                    stock_data = {'regularMarketPrice': latest_close_price}

            chart_data = {
                'x': [item['date'] for item in historical_data],
                'y': [item['close'] for item in historical_data],
                'title': f'Histórico de Preços de {cod_ativo}',
            }
        
        # Se não houver dados históricos e nenhum erro específico, ainda pode ser um erro
        if not historical_data and not chart_data.get('error'):
            chart_data = {'error': 'Não há dados históricos disponíveis para exibir o gráfico.'}


    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'chart_data': chart_data, 'stock_data': stock_data})

    form = AtivoUserForm(instance=ativo_user)

    context = {
        'ativo_user': ativo_user,
        'stock_data': stock_data,
        'chart_data_json': json.dumps(chart_data),
        'form': form,
        'api_source': api_source, # Passar a fonte da API para o template
    }
    return render(request, 'detalhes.html', context)

@require_POST
@login_required
def update_ativo_config(request, ativo_id):
    ativo_user = get_object_or_404(AtivosUser, id=ativo_id, user=request.user)
    form = AtivoUserForm(request.POST, instance=ativo_user)
    
    if form.is_valid():
        form.save()

        if not ativo_user.favorito and not ativo_user.em_carteira:
            ativo_user.delete()
            messages.add_message(request, constants.SUCCESS, f'Ativo {ativo_user.ativo.cod_ativo} removido do monitoramento.')
        else:
            messages.add_message(request, constants.SUCCESS, f'Configurações do ativo {ativo_user.ativo.cod_ativo} atualizadas com sucesso.')
    else:
        messages.add_message(request, constants.ERROR, 'Erro ao atualizar configurações do ativo.')
        
    return redirect('ativos_user:carteira')

    return redirect('ativos_user:carteira')

@require_POST
@login_required
def excluir_ativo(request, ativo_user_id):
    ativo_user = get_object_or_404(AtivosUser, id=ativo_user_id, user=request.user)
    senha_confirmacao = request.POST.get('senha_confirmacao')

    if not request.user.check_password(senha_confirmacao):
        messages.add_message(request, constants.ERROR, 'Senha incorreta. O ativo não foi excluído.')
        return redirect('ativos_user:home_ativos')

    # Armazenar o ativo_obj antes de excluir ativo_user
    ativo_obj = ativo_user.ativo
    cod_ativo = ativo_obj.cod_ativo

    # Excluir o AtivosUser
    ativo_user.delete()
    messages.add_message(request, constants.SUCCESS, f'Ativo {cod_ativo} removido do seu monitoramento.')

    # Verificar se o Ativo associado ainda tem outras referências
    # Se não houver mais AtivosUser ou PrecoAtivo associados a este Ativo, excluí-lo também
    if not AtivosUser.objects.filter(ativo=ativo_obj).exists() and \
       not PrecoAtivo.objects.filter(ativo=ativo_obj).exists():
        ativo_obj.delete()
        messages.add_message(request, constants.INFO, f'Ativo {cod_ativo} (global) também foi removido do banco de dados.')

    return redirect('ativos_user:home_ativos')

@require_POST
@login_required
def add_manual_asset(request):
    cod_ativo = request.POST.get('cod_ativo').upper()
    nome_empresa = request.POST.get('nome_empresa')
    user = request.user

    favorito = request.POST.get('favorito') == 'on'
    em_carteira = request.POST.get('em_carteira') == 'on'

    if not cod_ativo or not nome_empresa:
        messages.add_message(request, constants.ERROR, 'Código do ativo e nome da empresa não podem ser vazios.')
        return redirect('ativos_user:carteira')

    # Criar ou obter o novo modelo Ativo
    ativo_obj, created_ativo = Ativo.objects.get_or_create(
        cod_ativo=cod_ativo,
        defaults={'nome_empresa': nome_empresa}
    )
    if not created_ativo and ativo_obj.nome_empresa != nome_empresa:
        ativo_obj.nome_empresa = nome_empresa
        ativo_obj.save()

    # Tenta encontrar ou criar o ativo na lista de monitoramento do usuário
    ativo_user, created_user = AtivosUser.objects.get_or_create(
        user=user,
        ativo=ativo_obj,
        defaults={'favorito': favorito, 'em_carteira': em_carteira}
    )

    if created_user:
        messages.add_message(request, constants.SUCCESS, f'O ativo {cod_ativo} foi adicionado à sua lista de monitoramento.')
    else:
        if ativo_user.favorito != favorito or ativo_user.em_carteira != em_carteira:
            ativo_user.favorito = favorito
            ativo_user.em_carteira = em_carteira
            ativo_user.save()
            messages.add_message(request, constants.SUCCESS, f'O status do ativo {cod_ativo} foi atualizado.')
        else:
            messages.add_message(request, constants.INFO, f'O ativo {cod_ativo} já estava na sua lista de monitoramento com os mesmos status.')
    
    return redirect('ativos_user:carteira')
