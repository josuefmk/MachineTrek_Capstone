# Generated by Django 3.2.25 on 2024-10-06 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_auto_20241004_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1728181915.723309, max_length=100),
        ),
    ]
