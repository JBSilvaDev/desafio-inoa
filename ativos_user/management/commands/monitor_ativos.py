# ativos_user/management/commands/monitor_ativos.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q

from ativos_user.models import AtivosUser
from ativos_user.views import get_stock_data # Reutilizar a função de busca da API

import time

class Command(BaseCommand):
    help = 'Monitora ativos de usuários e envia alertas por e-mail se os limites forem atingidos.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando monitoramento de ativos...'))
        
        ativos_para_monitorar = AtivosUser.objects.filter(
            Q(em_carteira=True) | Q(favorito=True)
        ).select_related('ativo', 'user') # Otimizar query

        for ativo_user in ativos_para_monitorar:
            self.stdout.write(f'Verificando ativo: {ativo_user.ativo.cod_ativo} para o usuário: {ativo_user.user.username}')
            
            # Se intervalo_verificacao for 0, não monitorar este ativo
            if ativo_user.intervalo_verificacao == 0:
                self.stdout.write(f'  - Ativo {ativo_user.ativo.cod_ativo} tem intervalo de verificação 0. Pulando monitoramento.')
                continue

            # Verificar se o intervalo de verificação já passou
            if ativo_user.last_alert_sent:
                time_since_last_alert = timezone.now() - ativo_user.last_alert_sent
                if time_since_last_alert.total_seconds() < (ativo_user.intervalo_verificacao * 60):
                    self.stdout.write(f'  - Intervalo de verificação para {ativo_user.ativo.cod_ativo} ainda não passou. Pulando.')
                    continue

            stock_data = get_stock_data(ativo_user.ativo.cod_ativo)

            if stock_data and stock_data.get('regularMarketPrice'):
                current_price = stock_data['regularMarketPrice']
                self.stdout.write(f'  - Preço atual de {ativo_user.ativo.cod_ativo}: {current_price}')

                alert_message = []
                send_alert = False

                # Verificar limite superior
                if ativo_user.limite_superior and current_price >= ativo_user.limite_superior:
                    alert_message.append(f"O preço de {ativo_user.ativo.cod_ativo} ({current_price}) atingiu ou ultrapassou o limite superior ({ativo_user.limite_superior}).")
                    send_alert = True

                # Verificar limite inferior
                if ativo_user.limite_inferior and current_price <= ativo_user.limite_inferior:
                    alert_message.append(f"O preço de {ativo_user.ativo.cod_ativo} ({current_price}) atingiu ou caiu abaixo do limite inferior ({ativo_user.limite_inferior}).")
                    send_alert = True
                
                if send_alert:
                    subject = f"Alerta de Preço para {ativo_user.ativo.cod_ativo}"
                    html_message = render_to_string('email_alert.html', {
                        'user': ativo_user.user,
                        'ativo': ativo_user.ativo,
                        'current_price': current_price,
                        'limite_superior': ativo_user.limite_superior,
                        'limite_inferior': ativo_user.limite_inferior,
                        'alert_message': "<br>".join(alert_message)
                    })
                    plain_message = strip_tags(html_message)
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to_email = ativo_user.user.email

                    try:
                        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
                        ativo_user.last_alert_sent = timezone.now()
                        ativo_user.save()
                        self.stdout.write(self.style.SUCCESS(f'  - Alerta enviado para {ativo_user.user.email} sobre {ativo_user.ativo.cod_ativo}.'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  - Erro ao enviar e-mail para {ativo_user.user.email}: {e}'))
                else:
                    self.stdout.write(f'  - Nenhum limite atingido para {ativo_user.ativo.cod_ativo}.')
            else:
                self.stdout.write(self.style.WARNING(f'  - Não foi possível obter o preço atual para {ativo_user.ativo.cod_ativo}.'))

        self.stdout.write(self.style.SUCCESS('Monitoramento de ativos concluído.'))