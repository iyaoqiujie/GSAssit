# Generated by Django 3.0.6 on 2020-06-21 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('externalcontact', '0013_auto_20200621_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactme',
            name='config_id',
            field=models.CharField(blank=True, max_length=64, verbose_name='联系我配置Id'),
        ),
    ]
