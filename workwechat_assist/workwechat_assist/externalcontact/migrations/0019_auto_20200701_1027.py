# Generated by Django 3.0.6 on 2020-07-01 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontact', '0018_auto_20200630_1557'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactme',
            name='deleted',
        ),
        migrations.AddField(
            model_name='customerfollowuserrelationship',
            name='deleted',
            field=models.BooleanField(default=False, verbose_name='客户流失'),
        ),
    ]