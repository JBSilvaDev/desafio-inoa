# Generated by Django 5.0 on 2023-12-06 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AtivosList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_ativo', models.CharField(max_length=4)),
                ('empresa_nome', models.CharField(max_length=100)),
            ],
        ),
    ]