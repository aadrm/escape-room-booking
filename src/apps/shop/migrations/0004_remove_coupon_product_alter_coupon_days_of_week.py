# Generated by Django 4.2.3 on 2023-08-26 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_shopsettings_coupon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='product',
        ),
        migrations.AlterField(
            model_name='coupon',
            name='days_of_week',
            field=models.CharField(default='[0,1,2]', max_length=50),
        ),
    ]
