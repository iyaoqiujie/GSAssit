# Generated by Django 3.0.6 on 2020-06-17 02:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0003_auto_20200617_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='创建时间'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='department',
            unique_together={('corp', 'name'), ('parent', 'order')},
        ),
    ]
