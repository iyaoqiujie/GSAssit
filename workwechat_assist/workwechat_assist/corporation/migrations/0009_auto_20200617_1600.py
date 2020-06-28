# Generated by Django 3.0.6 on 2020-06-17 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporation', '0008_auto_20200617_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corpapp',
            name='agent_id',
            field=models.CharField(max_length=32, verbose_name='企业微信AgentId'),
        ),
        migrations.AlterUniqueTogether(
            name='corpapp',
            unique_together={('corp', 'agent_id')},
        ),
    ]