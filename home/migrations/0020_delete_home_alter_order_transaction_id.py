# Generated by Django 5.1.1 on 2024-09-28 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_alter_modificarproductofrom_imagen_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Home',
        ),
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=1727553498.702869, max_length=100),
        ),
    ]
