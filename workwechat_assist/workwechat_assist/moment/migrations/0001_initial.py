# Generated by Django 3.0.6 on 2020-07-16 07:30

from django.db import migrations, models
import django.db.models.deletion
import workwechat_assist.moment.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('corporation', '0016_auto_20200618_1331'),
    ]

    operations = [
        migrations.CreateModel(
            name='Moment',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(choices=[('image', '图文'), ('link', '链接'), ('video', '视频')], default='image', max_length=8, verbose_name='类型')),
                ('text', models.CharField(blank=True, max_length=512, verbose_name='文字内容')),
                ('image', models.ImageField(blank=True, null=True, upload_to=workwechat_assist.moment.models.user_directory_path, verbose_name='图片')),
                ('link', models.URLField(blank=True, null=True, verbose_name='链接')),
                ('video', models.FileField(null=True, upload_to=workwechat_assist.moment.models.user_directory_path, verbose_name='视频')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moments', to='corporation.Member', verbose_name='发表成员')),
            ],
            options={
                'verbose_name': '朋友圈信息',
                'verbose_name_plural': '朋友圈信息',
                'db_table': 'Moment',
            },
        ),
    ]
