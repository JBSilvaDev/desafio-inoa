# Generated by Django 5.0 on 2023-12-07 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos_user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodigoAtivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=5)),
                ('favorito', models.BooleanField()),
            ],
        ),
        migrations.RemoveField(
            model_name='ativosuser',
            name='favorito',
        ),
        migrations.RemoveField(
            model_name='ativosuser',
            name='codigo_ativo',
        ),
        migrations.AddField(
            model_name='ativosuser',
            name='codigo_ativo',
            field=models.ManyToManyField(to='ativos_user.codigoativo'),
        ),
    ]