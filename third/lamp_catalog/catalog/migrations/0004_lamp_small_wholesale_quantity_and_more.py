# Generated by Django 5.1.7 on 2025-05-19 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_lamp_large_wholesale_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lamp',
            name='small_wholesale_quantity',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество для мелкого опта'),
        ),
        migrations.AlterField(
            model_name='lamp',
            name='large_wholesale_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена крупного опта'),
        ),
        migrations.AlterField(
            model_name='lamp',
            name='large_wholesale_quantity',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Количество для крупного опта'),
        ),
        migrations.AlterField(
            model_name='lamp',
            name='small_wholesale_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена мелкого опта'),
        ),
    ]
