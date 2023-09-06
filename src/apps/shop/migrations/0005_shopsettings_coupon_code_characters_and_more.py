# Generated by Django 4.2.3 on 2023-08-27 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_remove_coupon_product_alter_coupon_days_of_week'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopsettings',
            name='coupon_code_characters',
            field=models.CharField(default='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', help_text='Any lower case letters will be capitalized', max_length=64, verbose_name='Characters to be used in coupon creation'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='product_included',
            field=models.ManyToManyField(blank=True, related_name='product_include', to='shop.product', verbose_name='include products'),
        ),
    ]
