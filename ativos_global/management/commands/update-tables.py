from django.core.management import BaseCommand
import csv
from django.conf import settings
import os
from ativos_global.models import AtivosList

class Command(BaseCommand):

  def handle(self, *args, **options):
    path = os.path.join(settings.BASE_DIR, settings.STATICFILES_DIRS,'acoesb3.csv')
    print(path)
    with open(path, newline='', encoding='utf-8') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(spamreader):
            if i != 0:
              att_ativo_list = AtivosList(
                 cod_ativo = row[0],
                 empresa_nome = row[1]
              )
              att_ativo_list.save()
