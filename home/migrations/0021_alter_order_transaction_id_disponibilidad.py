# Generated by Django 5.1.1 on 2024-09-30 19:43

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_delete_home_alter_order_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1727725430.764027, max_length=100),
        ),
        migrations.CreateModel(
            name='Disponibilidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateTimeField(default=django.utils.timezone.now, verbose_name='fecha inicio')),
                ('fecha_termino', models.DateTimeField(default=django.utils.timezone.now, verbose_name='fecha termino')),
                ('Producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disponibilidades', to='home.producto')),
            ],
        ),
    ]
