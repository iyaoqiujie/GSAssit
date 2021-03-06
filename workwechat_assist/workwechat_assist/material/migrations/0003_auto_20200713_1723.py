# Generated by Django 3.0.6 on 2020-07-13 09:23

from django.db import migrations, models
import workwechat_assist.material.models


class Migration(migrations.Migration):

    dependencies = [
        ('material', '0002_auto_20200713_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='materialimage',
            name='pic',
            field=models.ImageField(blank=True, null=True, upload_to=workwechat_assist.material.models.user_directory_path, verbose_name='图片'),
        ),
        migrations.AlterField(
            model_name='materialtemp',
            name='media_file',
            field=models.FileField(blank=True, null=True, upload_to=workwechat_assist.material.models.user_directory_path, verbose_name='媒体文件'),
        ),
    ]
