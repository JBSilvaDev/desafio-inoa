from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from ativos_user.models import AtivosUser, PrecoAtivo
from ativos_global.services import get_stock_price
import time
from datetime import datetime

class Command(BaseCommand):
    help = 'Monitors stock prices and sends email notifications based on user-defined limits.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando o monitoramento de ativos...'))

        monitored_assets = AtivosUser.objects.filter(em_carteira=True)

        for asset in monitored_assets:
            self.stdout.write(f'Verificando o ativo: {asset.cod_ativo}')

            # Respeitar o intervalo de verificação definido pelo usuário
            last_check = PrecoAtivo.objects.filter(codigo_ativo=asset).order_by('-timestamp').first()
            if last_check and (datetime.now(last_check.timestamp.tzinfo) - last_check.timestamp).total_seconds() < asset.intervalo_verificacao * 60:
                self.stdout.write(f'Intervalo de verificação para {asset.cod_ativo} ainda não atingido. Pulando.')
                continue

            current_price = get_stock_price(asset.cod_ativo)

            if current_price is not None:
                # Salva o novo preço no histórico
                PrecoAtivo.objects.create(
                    codigo_ativo=asset,
                    preco=current_price,
                    timestamp=datetime.now()
                )
                self.stdout.write(f'Preço atual de {asset.cod_ativo}: {current_price}')

                # Verifica os limites
                if asset.limite_superior is not None and current_price > asset.limite_superior:
                    self.send_notification(
                        asset.user_id,
                        asset.cod_ativo,
                        current_price,
                        asset.limite_superior,
                        'venda'
                    )
                
                if asset.limite_inferior is not None and current_price < asset.limite_inferior:
                    self.send_notification(
                        asset.user_id,
                        asset.cod_ativo,
                        current_price,
                        asset.limite_inferior,
                        'compra'
                    )
            else:
                self.stdout.write(self.style.WARNING(f'Não foi possível obter o preço para {asset.cod_ativo}.'))
            
            # Pausa para não sobrecarregar a API
            time.sleep(5) 

        self.stdout.write(self.style.SUCCESS('Monitoramento concluído.'))

    def send_notification(self, user, stock_code, current_price, limit, suggestion):
        subject = f'Alerta de {suggestion.capitalize()}: {stock_code}'
        message = (
            f'Olá {user.username},\n\n'
            f'O ativo {stock_code} atingiu o preço de R$ {current_price:.2f}, '
            f'cruzando o seu limite de {suggestion} de R$ {limit:.2f}.\n\n'
            f'Esta é uma sugestão de {suggestion}.\n\n'
            'Atenciosamente,\nEquipe de Monitoramento de Ativos'
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            self.stdout.write(self.style.SUCCESS(
                f'Notificação de {suggestion} enviada para {user.email} sobre o ativo {stock_code}.'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Falha ao enviar e-mail para {user.email}: {e}'
            ))
