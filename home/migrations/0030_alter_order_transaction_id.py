# Generated by Django 5.1.1 on 2024-10-13 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0029_alter_order_transaction_id_alter_perfil_rut'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1728777770.639839, max_length=100),
        ),
    ]
