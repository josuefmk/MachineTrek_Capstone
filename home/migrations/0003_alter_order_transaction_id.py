# Generated by Django 5.1.1 on 2024-09-16 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_comuna_loginform_modificarproductofrom_region_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1726518147.500682, max_length=100),
        ),
    ]
