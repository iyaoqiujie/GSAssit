# Generated by Django 3.0.6 on 2020-06-28 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontact', '0015_auto_20200628_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactme',
            name='state',
            field=models.CharField(max_length=32, unique=True, verbose_name='添加渠道'),
        ),
    ]
