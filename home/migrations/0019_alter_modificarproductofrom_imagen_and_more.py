# Generated by Django 5.1.1 on 2024-09-25 19:28

import storages.backends.s3
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_alter_order_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modificarproductofrom',
            name='imagen',
            field=models.ImageField(default='default.jpg', storage=storages.backends.s3.S3Storage(), upload_to='productos/', verbose_name='imagen'),
        ),
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1727292513.465969, max_length=100),
        ),
        migrations.AlterField(
            model_name='producto',
            name='descuento',
            field=models.IntegerField(default=0, help_text='Ingrese el porcentaje de descuento. Ejemplo: 10%', null=True, verbose_name='descuento'),
        ),
        migrations.AlterField(
            model_name='productoimagen',
            name='imagen',
            field=models.ImageField(default='default.jpg', storage=storages.backends.s3.S3Storage(), upload_to='productos/', verbose_name='imagen'),
        ),
    ]
