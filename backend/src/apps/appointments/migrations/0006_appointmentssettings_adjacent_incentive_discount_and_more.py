# Generated by Django 4.2.3 on 2024-01-25 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0005_remove_slot_is_enabled_slot_availability'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentssettings',
            name='adjacent_incentive_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Parallel incentive discount in euro'),
        ),
        migrations.AddField(
            model_name='appointmentssettings',
            name='parallel_incentive_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=3, verbose_name='Parallel incentive discount in euro'),
        ),
    ]
