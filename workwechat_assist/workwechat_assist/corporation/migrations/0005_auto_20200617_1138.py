# Generated by Django 3.0.6 on 2020-06-17 03:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0004_auto_20200617_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='corporation.Department', verbose_name='父部门'),
        ),
    ]
