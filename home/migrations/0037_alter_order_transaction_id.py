# Generated by Django 5.1.1 on 2024-10-21 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0036_alter_order_transaction_id_arriendo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1729469571.295942, max_length=100),
        ),
    ]
