# Generated by Django 3.0.6 on 2020-06-18 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0014_auto_20200618_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tagid',
            field=models.PositiveIntegerField(blank=True, verbose_name='标签ID'),
        ),
    ]
