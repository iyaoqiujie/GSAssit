# Generated by Django 3.0.6 on 2020-06-17 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0012_auto_20200617_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='open_userid',
            field=models.CharField(blank=True, max_length=64, verbose_name='成员OpenID'),
        ),
    ]
