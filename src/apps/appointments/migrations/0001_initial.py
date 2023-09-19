# Generated by Django 4.2.3 on 2023-09-13 08:10

import apps.appointments.models.appointments_settings
import common.days_of_week_mixin
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentsSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prevent_bookings_after_date', models.DateField(default=apps.appointments.models.appointments_settings.default_prevent_bookings_after_date, verbose_name='Prevent bookings after date')),
                ('prevent_bookings_after_days', models.PositiveSmallIntegerField(default=90, verbose_name='Prevent bookings after days')),
                ('buffer_in_minutes', models.PositiveSmallIntegerField(default=180, verbose_name='Buffer in minutes')),
                ('parallel_slot_frame_in_minutes', models.PositiveSmallIntegerField(default=0, verbose_name='Consider parallel other slots that start within this number of minutes from each other')),
                ('adjacent_slot_frame_in_minutes', models.PositiveSmallIntegerField(default=0, verbose_name='Consider adjacent other slots that end within this amount of minutes from the start of each other')),
            ],
            options={
                'verbose_name_plural': ' Settings',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('is_active', models.BooleanField(default=False, verbose_name='Active')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('photo_alt', models.CharField(blank=True, max_length=128, null=True, verbose_name='Alt text')),
                ('theme_colour', models.CharField(default='999999', max_length=6, verbose_name='Colour Hexagesimal')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('days_of_week', models.CharField(max_length=50)),
                ('start_time', models.TimeField()),
                ('duration_minutes', models.PositiveSmallIntegerField(default=60)),
                ('buffer_minutes', models.PositiveSmallIntegerField(default=30)),
                ('repeat_times', models.IntegerField(default=1, help_text='The number of slots to be created each day', verbose_name='Repeat times')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appointments.room', verbose_name='Room')),
            ],
            bases=(models.Model, common.days_of_week_mixin.DaysOfWeekMixin),
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField(verbose_name='Start')),
                ('duration', models.PositiveSmallIntegerField(default=60, verbose_name='Duration')),
                ('buffer', models.PositiveSmallIntegerField(default=30, verbose_name='Buffer')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('appointment_end', models.DateTimeField(blank=True, editable=False, null=True)),
                ('block_end', models.DateTimeField(blank=True, editable=False, null=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appointments.room', verbose_name='Room')),
                ('schedule', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='slots', related_query_name='slots', to='appointments.schedule', verbose_name='Schedule')),
            ],
            options={
                'ordering': ['room', 'start'],
            },
        ),
    ]
