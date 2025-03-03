# Generated by Django 5.1.2 on 2025-02-24 23:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_stocktimeseries_cumulated_quantity'),
        ('tickers', '0002_alter_ticker_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktimeseries',
            name='ticker',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='tickers.ticker', verbose_name='ticker'),
            preserve_default=False,
        ),
    ]
