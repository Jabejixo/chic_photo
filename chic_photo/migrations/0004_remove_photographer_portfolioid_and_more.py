# Generated by Django 5.0.2 on 2024-02-20 06:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chic_photo', '0003_remove_order_status_order_serviceid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photographer',
            name='portfolioID',
        ),
        migrations.AddField(
            model_name='photodirectory',
            name='photographer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='chic_photo.photographer'),
        ),
        migrations.AlterField(
            model_name='photographer',
            name='schedule',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='photographer',
            name='skills',
            field=models.TextField(blank=True, null=True),
        ),
    ]
