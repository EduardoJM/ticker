# Generated by Django 5.1.2 on 2025-02-24 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0003_stocktimeseries_alter_tradingnote_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocktimeseries',
            name='cumulated_quantity',
            field=models.IntegerField(default=0, verbose_name='quantity'),
            preserve_default=False,
        ),
    ]
