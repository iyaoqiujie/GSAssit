# Generated by Django 3.0.6 on 2020-07-13 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialImage',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('pic', models.ImageField(blank=True, null=True, upload_to='Material/image/%y/%d/', verbose_name='图片')),
                ('wechat_url', models.URLField(blank=True, null=True, verbose_name='企业微信图片URL')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '图片信息',
                'verbose_name_plural': '图片信息',
                'db_table': 'MaterialImage',
            },
        ),
        migrations.CreateModel(
            name='MaterialTemp',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('media_type', models.CharField(choices=[('image', '图片'), ('voice', '语音'), ('video', '视频'), ('file', '文件')], default='image', max_length=8, verbose_name='媒体文件类型')),
                ('media_file', models.FileField(blank=True, null=True, upload_to='Material/temp/%y/%d/', verbose_name='媒体文件')),
                ('media_id', models.CharField(blank=True, max_length=64, null=True, verbose_name='企业微信文件标识')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '临时素材',
                'verbose_name_plural': '临时素材',
                'db_table': 'MaterialTemp',
            },
        ),
    ]