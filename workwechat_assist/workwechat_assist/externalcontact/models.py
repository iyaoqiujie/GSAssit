from django.db import models
from django.utils import timezone
import datetime
from jsonfield import JSONField
from workwechat_assist.corporation.models import Corporation, Member


class ContactMe(models.Model):
    TYPE_CHOICES = (
        (1, '单人'),
        (2, '多人')
    )

    SCENE_CHOICES = (
        (1, '小程序联系'),
        (2, '二维码联系')
    )

    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='contactmes', on_delete=models.CASCADE, verbose_name='所属企业')
    config_id = models.CharField(verbose_name='联系我配置Id', max_length=64, blank=True)
    type = models.SmallIntegerField(verbose_name='联系方式类型', choices=TYPE_CHOICES, default=1)
    scene = models.SmallIntegerField(verbose_name='场景', choices=SCENE_CHOICES, default=2)
    style = models.SmallIntegerField(verbose_name='小程序中的控件样式', null=True, default=1)
    remark = models.CharField(verbose_name='备注信息', max_length=32, blank=True)
    skip_verify = models.BooleanField(verbose_name='是否无需验证', default=True)
    qr_code = models.URLField(verbose_name='联系二维码的URL', null=True, blank=True)
    state = models.CharField(verbose_name='添加渠道', max_length=32, unique=True)
    user = JSONField(verbose_name='成员userId列表', null=True, blank=True)
    party = JSONField(verbose_name='部门id列表', null=True, blank=True)
    tags = JSONField(verbose_name='应用标签', null=True, blank=True)
    welcome_code = JSONField(verbose_name='欢迎语', null=True, blank=True)
    is_temp = JSONField(verbose_name='是否临时会话', default=False, null=True)
    expires_in = models.PositiveIntegerField(verbose_name='临时会话二维码有效期', default=3600*24*7, null=True)
    chat_expires_in = models.PositiveIntegerField(verbose_name='临时会话有效期', default=3600*24, null=True)
    unionid = models.CharField(verbose_name='客户unionid', max_length=64, blank=True)
    conclusions = JSONField(verbose_name='结束语', blank=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        unique_together = (('corp', 'config_id'),)
        db_table = 'ContactMe'
        verbose_name = '联系我信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.config_id


class Customer(models.Model):
    TYPE_CHOICES = (
        (1, 'wechat'),
        (2, 'work_wechat')
    )

    GENDER_CHOICES = (
        ('1', 'male'),
        ('2', 'female')
    )
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='customers', on_delete=models.CASCADE, verbose_name='所属企业')
    external_userid = models.CharField(verbose_name='客户userid', max_length=64)
    name = models.CharField(verbose_name='客户名称', max_length=64)
    avatar = models.URLField(verbose_name='成员头像', blank=True)
    type = models.SmallIntegerField(verbose_name='激活状态', choices=TYPE_CHOICES, default=1)
    gender = models.CharField(verbose_name='性别', max_length=2, choices=GENDER_CHOICES, default='1')
    unionid = models.CharField(verbose_name='微信unionid', max_length=32, blank=True, default='')
    position = models.CharField(verbose_name='职位', max_length=32, blank=True, default='')
    corp_name = models.CharField(verbose_name='企业简称', max_length=32, blank=True, default='')
    corp_full_name = models.CharField(verbose_name='企业全称', max_length=32, blank=True, default='')
    external_profile = JSONField(verbose_name='自定义展示信息', null=True, blank=True)
    members = models.ManyToManyField(Member, through='CustomerFollowUserRelationship')
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        unique_together = (('corp', 'external_userid'),)
        db_table = 'Customer'
        verbose_name = '客户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.external_userid, self.name)


class CustomerFollowUserRelationship(models.Model):
    id = models.BigAutoField(primary_key=True)
    member = models.ForeignKey(Member, related_name='cfuRels', on_delete=models.CASCADE, verbose_name='成员')
    customer = models.ForeignKey(Customer, related_name='cfuRels', on_delete=models.CASCADE, verbose_name='客户')
    remark = models.CharField(verbose_name='备注', max_length=32, blank=True, default='')
    description = models.CharField(verbose_name='描述', max_length=32, blank=True, default='')
    remark_corp_name = models.CharField(verbose_name='备注企业', max_length=32, blank=True, default='')
    createtime = models.PositiveIntegerField(verbose_name='添加联系人时间', null=True)
    tags = JSONField(verbose_name='客户标签', null=True)
    remark_mobiles = JSONField(verbose_name='备注手机号码', null=True, blank=True)
    add_way = models.SmallIntegerField(verbose_name='客户来源', default=3)
    state = models.CharField(verbose_name='自定义来源', max_length=64,  blank=True)
    deleted = models.BooleanField(verbose_name='客户流失', default=False)

    class Meta:
        unique_together = (('member', 'customer'),)
        db_table = 'CustomerFollowUserRelationship'
        verbose_name = '客户与成员绑定信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.customer.name, self.member.name)


class TagGroup(models.Model):
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='taggroups', on_delete=models.CASCADE, verbose_name='所属企业')
    groupname = models.CharField(verbose_name='标签组名称', max_length=32)
    groupid = models.CharField(verbose_name='标签组ID', max_length=64, blank=True)
    create_time = models.PositiveIntegerField(verbose_name='创建时间', null=True)
    order = models.PositiveIntegerField(verbose_name='次序值', null=True)

    class Meta:
        unique_together = (('corp', 'groupname'),)
        db_table = 'TagGroup'
        verbose_name = '客户标签组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.corp.name, self.groupname)


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    taggroup = models.ForeignKey(TagGroup, related_name='tags',
                                 on_delete=models.CASCADE, verbose_name='标签组')
    tagname = models.CharField(verbose_name='标签名称', max_length=32)
    tagid = models.CharField(verbose_name='标签ID', max_length=64, blank=True)
    create_time = models.PositiveIntegerField(verbose_name='创建时间', null=True)
    order = models.PositiveIntegerField(verbose_name='次序值', null=True)

    class Meta:
        unique_together = (('taggroup', 'tagname'),)
        db_table = 'CustomerTag'
        verbose_name = '客户标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.taggroup.groupname, self.tagname)


class GroupChat(models.Model):
    STATUS_CHOICES = (
        (0, '正常'),
        (1, '跟进人离职'),
        (2, '离职继承中'),
        (3, '离职继承完成'),
    )
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='groupchats', on_delete=models.CASCADE, verbose_name='所属企业')
    name = models.CharField(verbose_name='群名', max_length=32, blank=True)
    chat_id = models.CharField(verbose_name='群ID', max_length=64,)
    owner = models.CharField(verbose_name='群主ID', max_length=64, blank=True)
    create_time = models.PositiveIntegerField(verbose_name='创建时间', null=True)
    notice = models.CharField(verbose_name='群公告', max_length=64, blank=True)
    members = JSONField(verbose_name='群成员', null=True, blank=True)
    status = models.SmallIntegerField(verbose_name='客户群状态', choices=STATUS_CHOICES, default=0)

    class Meta:
        unique_together = (('corp', 'chat_id'),)
        db_table = 'GroupChat'
        verbose_name = '客户群'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.corp.name, self.name)


class GroupMessage(models.Model):
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='groupmessages', on_delete=models.CASCADE, verbose_name='所属企业')
    msg_id = models.CharField(verbose_name='群发消息ID', max_length=64,)
    content = JSONField(verbose_name='消息内容', null=True)
    detail_list = JSONField(verbose_name='群发消息发送结果', null=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        unique_together = (('corp', 'msg_id'),)
        db_table = 'GroupMessage'
        verbose_name = '群发消息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.corp.name, self.msg_id)


