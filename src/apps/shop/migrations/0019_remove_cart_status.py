# Generated by Django 4.2.3 on 2024-01-03 11:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0018_order_is_cancelled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='status',
        ),
    ]
