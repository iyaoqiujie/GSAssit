from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = (
        ('A', '管理员'),
        ('M', '经理'),
        ('DM', '部门经理'),
        ('E', '员工'),
    )
    GENDER_CHOICES = (
        ('0', '未知'),
        ('1', '男'),
        ('2', '女'),
    )
    name = models.CharField(verbose_name='姓名', max_length=32, blank=True)
    mobile = models.CharField(verbose_name='手机号码', max_length=16, blank=True)
    role = models.CharField(verbose_name='角色', max_length=4, choices=ROLE_CHOICES, default='E')
    avatar = models.ImageField(verbose_name='头像', upload_to='UserProfile/avatar/%y/%d/', null=True, blank=True)
    # Wechat related fields below
    openid = models.CharField(verbose_name='微信openid', max_length=64, blank=True, default='')
    uid = models.CharField(verbose_name='微信UnionID', max_length=64, blank=True, default='')
    nickName = models.CharField(verbose_name='微信昵称', max_length=32, blank=True, default='')
    avatarUrl = models.URLField( verbose_name='微信头像', max_length=256, blank=True, default='')
    gender = models.CharField(verbose_name='性别', max_length=4, choices=GENDER_CHOICES, default='0')

    class Meta:
        db_table = 'User'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}:{1}'.format(self.username, self.name)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})
