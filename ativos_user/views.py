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
    return None

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
            print(f"Dados históricos vazios ou malformados para {stock_code}. Resposta da API: {data}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar histórico da API para {stock_code}: {e}")
    return []

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

    function = ''
    interval = ''
    adjusted = False
    time_series_key_map = {}

    if 'min' in interval_param:
        function = 'TIME_SERIES_INTRADAY'
        interval = interval_param
        time_series_key_map[function] = f'Time Series ({interval_param})'
    elif interval_param == '1d':
        function = 'TIME_SERIES_DAILY'
        adjusted = True # Tentaremos usar o ajustado
        time_series_key_map[function] = 'Time Series (Daily)'
        time_series_key_map['TIME_SERIES_DAILY_ADJUSTED'] = 'Time Series (Daily)' # Caso a função seja explicitamente ajustada
    elif interval_param == '1wk':
        function = 'TIME_SERIES_WEEKLY'
        adjusted = True # Tentaremos usar o ajustado
        time_series_key_map[function] = 'Weekly Time Series'
        time_series_key_map['TIME_SERIES_WEEKLY_ADJUSTED'] = 'Weekly Adjusted Time Series'
    elif interval_param == '1mo':
        function = 'TIME_SERIES_MONTHLY'
        adjusted = True # Tentaremos usar o ajustado
        time_series_key_map[function] = 'Monthly Time Series'
        time_series_key_map['TIME_SERIES_MONTHLY_ADJUSTED'] = 'Monthly Adjusted Time Series'
    else:
        return {'error': 'Intervalo de tempo inválido para Alpha Vantage.'}

    url = f"https://www.alphavantage.co/query?function={function}&symbol={stock_code}&apikey={api_key}"
    if function == 'TIME_SERIES_INTRADAY':
        url += f"&interval={interval}"
    elif adjusted: # Para funções diárias, semanais e mensais, se quisermos ajustado, usamos a função _ADJUSTED
        url = f"https://www.alphavantage.co/query?function={function}_ADJUSTED&symbol={stock_code}&apikey={api_key}"
        function = function + '_ADJUSTED' # Atualiza a função para corresponder à URL

    print(f"Chamando API Alpha Vantage para histórico: {url}")

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        data = response.json()

        if 'Information' in data:
            error_message = f"Erro da API Alpha Vantage: {data['Information']}"
            print(error_message)
            return {'error': error_message}
        if 'Error Message' in data:
            error_message = f"Erro da API Alpha Vantage: {data['Error Message']}"
            print(error_message)
            return {'error': error_message}

        time_series_key = time_series_key_map.get(function)
        if not time_series_key or time_series_key not in data:
            # Tenta encontrar a chave de forma mais genérica se o mapeamento falhar
            time_series_key = next((key for key in data if 'Time Series' in key or 'Daily' in key or 'Weekly' in key or 'Monthly' in key), None)
            if not time_series_key:
                error_message = f"Nenhuma chave de série temporal encontrada na resposta da Alpha Vantage para {stock_code}. Resposta: {data}"
                print(error_message)
                return {'error': error_message}

        historical_data = data[time_series_key]
        
        close_key = '5. adjusted close' if adjusted and any('5. adjusted close' in item for item in historical_data.values()) else '4. close'
        
        # Determinar o formato da data com base na função
        date_format = '%Y-%m-%d %H:%M:%S' if 'INTRADAY' in function else '%Y-%m-%d'

        parsed_data = []
        for date_str, item in historical_data.items():
            try:
                timestamp = int(datetime.strptime(date_str, date_format).timestamp())
                close_price = float(item[close_key])
                parsed_data.append({'date': timestamp, 'close': close_price})
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
        stock_data = get_stock_data_alpha_vantage(cod_ativo)
        historical_data_result = get_stock_history_alpha_vantage(cod_ativo, interval_param)
        
        if isinstance(historical_data_result, dict) and 'error' in historical_data_result:
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
        stock_data = get_stock_data(cod_ativo)
        historical_data = get_stock_history(cod_ativo, range_param, interval_param)
        chart_data = {
            'x': [item['date'] for item in historical_data],
            'y': [item['close'] for item in historical_data],
            'title': f'Histórico de Preços de {cod_ativo}',
        }

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
