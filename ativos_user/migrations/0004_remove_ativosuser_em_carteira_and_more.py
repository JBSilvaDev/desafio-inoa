# Generated by Django 5.0 on 2023-12-07 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos_user', '0003_remove_ativosuser_codigo_ativo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ativosuser',
            name='em_carteira',
        ),
        migrations.AddField(
            model_name='codigoativo',
            name='em_carteira',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]