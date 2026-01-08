from django.core.management import BaseCommand
import csv
from django.conf import settings
import os
from ativos_global.models import AtivosList

class Command(BaseCommand):
  help = 'Populates the AtivosList model from acoesb3.csv.'

  def handle(self, *args, **options):
    # Clear existing data to prevent duplicates on subsequent runs
    AtivosList.objects.all().delete()
    self.stdout.write(self.style.SUCCESS('Dados existentes de AtivosList limpos.'))

    csv_file_path = os.path.join(settings.BASE_DIR, 'setup', 'base', 'acoesb3.csv')
    
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for i, row in enumerate(spamreader):
                if i != 0: # Skip header row
                    AtivosList.objects.create(
                        cod_ativo = row[0],
                        nome_empresa = row[1] # Corrected field name
                    )
            self.stdout.write(self.style.SUCCESS('AtivosList populado com sucesso a partir de acoesb3.csv.'))
    except FileNotFoundError:
        self.stdout.write(self.style.ERROR(f'Erro: O arquivo CSV não foi encontrado em {csv_file_path}'))
    except Exception as e:
        self.stdout.write(self.style.ERROR(f'Ocorreu um erro ao popular AtivosList: {e}'))
