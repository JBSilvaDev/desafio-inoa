from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from ativos_user.models import AtivosUser, PrecoAtivo
from ativos_global.services import get_stock_price
import time
from datetime import datetime

class Command(BaseCommand):
    help = 'Monitors stock prices and sends email notifications based on user-defined limits.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando o monitoramento de ativos...'))

        monitored_assets = AtivosUser.objects.all()
        self.stdout.write(f'Encontrado(s) {monitored_assets.count()} ativo(s) para monitorar.')

        for asset_user in monitored_assets:
            stock_code = asset_user.ativo.cod_ativo
            self.stdout.write(f'Verificando o ativo: {stock_code}')

            # Respeitar o intervalo de verificação definido pelo usuário
            last_check = PrecoAtivo.objects.filter(ativo=asset_user.ativo).order_by('-data_hora').first()
            if last_check:
                try:
                    now = timezone.now()
                except Exception as e:
                    # Fallback if timezone is not configured properly
                    now = datetime.now()

                if (now - last_check.data_hora).total_seconds() < asset_user.intervalo_verificacao * 60:
                    self.stdout.write(f'Intervalo de verificação para {stock_code} ainda não atingido. Pulando.')
                    continue

            current_price = get_stock_price(stock_code)

            if current_price is not None:
                # Salva o novo preço no histórico
                PrecoAtivo.objects.create(
                    ativo=asset_user.ativo,
                    preco=current_price
                )
                self.stdout.write(f'Preço atual de {stock_code}: {current_price}')

                # Verifica os limites
                if asset_user.limite_superior is not None and current_price > asset_user.limite_superior:
                    self.send_notification(
                        asset_user.user,
                        stock_code,
                        current_price,
                        asset_user.limite_superior,
                        'venda'
                    )
                
                if asset_user.limite_inferior is not None and current_price < asset_user.limite_inferior:
                    self.send_notification(
                        asset_user.user,
                        stock_code,
                        current_price,
                        asset_user.limite_inferior,
                        'compra'
                    )
            else:
                self.stdout.write(self.style.WARNING(f'Não foi possível obter o preço para {stock_code}.'))
            
            # Pausa para não sobrecarregar a API
            time.sleep(5) 

        self.stdout.write(self.style.SUCCESS('Monitoramento concluído.'))

    def send_notification(self, user, stock_code, current_price, limit, suggestion):
        subject = f'Alerta de {suggestion.capitalize()}: {stock_code}'
        message = (
            f'Olá {user.username},\n\n'
            f'O ativo {stock_code} atingiu o preço de R$ {float(current_price):.2f}, '
            f'cruzando o seu limite de {suggestion} de R$ {float(limit):.2f}.\n\n'
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
