# Generated by Django 5.1.1 on 2024-10-13 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0030_alter_order_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1728779533.17345, max_length=100),
        ),
    ]
