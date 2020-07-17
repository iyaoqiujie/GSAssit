from django.db import models
from workwechat_assist.corporation.models import Corporation, Member
import logging
import os
import uuid
from datetime import datetime

myLogger = logging.getLogger('WWAssist.moment')

# Create your models here.


def user_directory_path(instance, filename):
    ext = filename.split('.').pop()
    random_name = uuid.uuid3(uuid.NAMESPACE_URL, filename)
    filename = '{0}.{1}'.format(random_name, ext)
    today = datetime.today()

    return 'Moment/member_{0}/{1}/{2}/{3}/{4}'.format(instance.member.id, today.year, today.month, today.day, filename)


class Moment(models.Model):
    CATEGORY_CHOICES = (
        ('image', '图文'),
        ('link', '链接'),
        ('video', '视频')
    )
    id = models.BigAutoField(primary_key=True)
    member = models.ForeignKey(Member, related_name='moments', null=True, on_delete=models.SET_NULL,
                               verbose_name='发表成员')
    category = models.CharField(verbose_name='类型', max_length=8, choices=CATEGORY_CHOICES, default='image')
    text = models.CharField(verbose_name='文字内容', max_length=512, blank=True)
    image = models.ImageField(verbose_name='图片', upload_to=user_directory_path, null=True, blank=True)
    link = models.URLField(verbose_name='链接', null=True, blank=True)
    video = models.FileField(verbose_name='视频', upload_to=user_directory_path, null=True, blank=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        db_table = 'Moment'
        verbose_name = '朋友圈信息'
        verbose_name_plural = verbose_name

