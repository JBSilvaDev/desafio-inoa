# Generated by Django 5.0 on 2023-12-15 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos_user', '0011_ativosuser_id_ativo_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ativosuser',
            name='cod_ativo',
            field=models.CharField(max_length=6),
        ),
    ]
