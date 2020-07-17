from django.db import models
from workwechat_assist.corporation.models import Corporation, CorpApp
import os
import uuid
import mimetypes
from datetime import datetime
from workwechat_assist.utils.workwechat_sdk import WorkWechat
from config.settings.base import AGENT_ID, AGENT_NAME
import logging

myLogger = logging.getLogger('WWAssist.material')

# Create your models here.


def user_directory_path(instance, filename):
    ext = filename.split('.').pop()
    random_name = uuid.uuid3(uuid.NAMESPACE_URL, filename)
    filename = '{0}.{1}'.format(random_name, ext)
    today = datetime.today()

    return 'Material/corp_{0}/{1}/{2}/{3}/{4}'.format(instance.corp.id, today.year, today.month, today.day, filename)


class MaterialImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='materialImages', null=True, on_delete=models.SET_NULL,
                             verbose_name='所属企业')
    pic = models.ImageField(verbose_name='图片', upload_to=user_directory_path, null=True, blank=True)
    wechat_url = models.URLField(verbose_name='企业微信图片URL', null=True, blank=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def send2workwechat(self):
        if not self.pic:
            myLogger.error('No pic found')
            return False, 'No pic found'

        if not self.corp:
            myLogger.error('No corp info')
            return False, 'No corp info'

        try:
            agent = self.corp.apps.all().get(name=AGENT_NAME)
        except CorpApp.DoesNotExist:
            myLogger.error('Corp [{0}] does NOT have agent'.format(self.corp.name))
            return False, 'Corp [{0}] does NOT have agent'.format(self.corp.name)

        wechat = WorkWechat(agent)
        filepath = self.pic.path
        filename = os.path.basename(filepath)
        content_type = mimetypes.guess_type(filepath)[0]
        with open(filepath, 'rb') as filedata:
            media_file = (filename, filedata, content_type)
            status, res = wechat.upload_image(media_file)
            if not status:
                myLogger.error(res.get('errmsg'))
                return False, res.get('errmsg')

            myLogger.info(res)
            self.wechat_url = res.get('url')
            self.save()
            return True, ''

    class Meta:
        db_table = 'MaterialImage'
        verbose_name = '图片信息'
        verbose_name_plural = verbose_name


class MaterialTemp(models.Model):
    TYPE_CHOICES = (
        ('image', '图片'),
        ('voice', '语音'),
        ('video', '视频'),
        ('file', '文件')
    )
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='materialTemps', null=True, on_delete=models.SET_NULL,
                             verbose_name='所属企业')
    media_type = models.CharField(verbose_name='媒体文件类型', max_length=8, choices=TYPE_CHOICES, default='image')
    media_file = models.FileField(verbose_name='媒体文件', upload_to=user_directory_path, null=True, blank=True)
    media_id = models.CharField(verbose_name='企业微信文件标识', max_length=256, null=True, blank=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    def send2workwechat(self):
        if not self.media_file:
            myLogger.error('No media found')
            return False, 'No media found'

        if not self.corp:
            myLogger.error('No corp info')
            return False, 'No corp info'

        try:
            agent = self.corp.apps.all().get(name=AGENT_NAME)
        except CorpApp.DoesNotExist:
            myLogger.error('Corp [{0}] does NOT have agent'.format(self.corp.name))
            return False, 'Corp [{0}] does NOT have agent'.format(self.corp.name)

        wechat = WorkWechat(agent)
        filepath = self.media_file.path
        filename = os.path.basename(filepath)
        content_type = mimetypes.guess_type(filepath)[0]
        with open(filepath, 'rb') as filedata:
            media_file = (filename, filedata, content_type)
            status, res = wechat.upload_media(self.media_type, media_file)
            if not status:
                myLogger.error(res.get('errmsg'))
                return False, res.get('errmsg')

            myLogger.info(res)
            self.media_id = res.get('media_id')
            self.save()
            return True, ''

    class Meta:
        db_table = 'MaterialTemp'
        verbose_name = '临时素材'
        verbose_name_plural = verbose_name


