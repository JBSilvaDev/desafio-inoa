# Generated by Django 5.0 on 2023-12-08 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos_global', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ativoslist',
            name='cod_ativo',
            field=models.CharField(max_length=5),
        ),
    ]
