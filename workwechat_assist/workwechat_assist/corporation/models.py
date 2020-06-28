from django.db import models
from django.utils import timezone
import datetime
# Create your models here.


class Corporation(models.Model):
    id = models.BigAutoField(primary_key=True)
    corp_id = models.CharField(verbose_name='企业ID', max_length=32, unique=True)
    name = models.CharField(verbose_name='企业名称', max_length=256, )
    address = models.CharField(verbose_name='地址', max_length=256, blank=True)
    phone = models.CharField(verbose_name='联系电话', max_length=64, blank=True)
    industry_type = models.CharField(verbose_name='行业类型', max_length=128, )
    staff_size = models.CharField(verbose_name='人员规模', max_length=32, default='1-50人')
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        db_table = 'Corporation'
        verbose_name = '企业信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


def one_hour_later():
    return timezone.now() + datetime.timedelta(hours=1)


class CorpApp(models.Model):
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='apps', on_delete=models.CASCADE, verbose_name='所属企业')
    name = models.CharField(verbose_name='APP名称', max_length=128, default='盘陀企业微信助手')
    agent_id = models.CharField(verbose_name='企业微信AgentId', max_length=32,)
    secret = models.CharField(verbose_name='企业微信Secret', max_length=64,)
    token = models.CharField(verbose_name='企业微信回调Token', max_length=32, blank=True)
    aes_key = models.CharField(verbose_name='企业微信回调EncodingAESKey', max_length=64, blank=True)
    #access_token = models.CharField(verbose_name='访问票据', max_length=64, blank=True)
    #token_valid_time = models.DateTimeField(verbose_name='票据有效时间', default=one_hour_later, null=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        unique_together = (('corp', 'agent_id'),)
        db_table = 'CorpApp'
        verbose_name = '企业微信应用信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}应用: {1}'.format(self.corp.name, self.name)


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='departments', on_delete=models.CASCADE, verbose_name='所属企业')
    department_id = models.PositiveIntegerField(verbose_name='企业微信部门ID', null=True)
    name = models.CharField(verbose_name='部门名称', max_length=32)
    name_en = models.CharField(verbose_name='部门英文名称', max_length=32, blank=True)
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.SET_NULL,
                               verbose_name='父部门')
    order = models.PositiveIntegerField(verbose_name='在父部门中的次序', null=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        unique_together = (('corp', 'name'), ('parent', 'order'))
        db_table = 'Department'
        verbose_name = '部门信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.parent:
            return '{0} {1}, 父部门:{2}, 次序: {3}'.format(self.corp.name, self.name, self.parent.name, self.order)
        else:
            return '{0} {1}'.format(self.corp.name, self.name)


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='tags', on_delete=models.CASCADE, verbose_name='所属企业')
    tagname = models.CharField(verbose_name='标签名称', max_length=32)
    tagid = models.PositiveIntegerField(verbose_name='标签ID', blank=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        unique_together = (('corp', 'tagname'),)
        db_table = 'MemberTag'
        verbose_name = '员工标签信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}: {1}'.format(self.corp.name, self.tagname)


class Member(models.Model):
    STATUS_CHOICES = (
        (1, 'ACTIVE'),
        (2, 'FORBIDDEN'),
        (4, 'INACTIVE'),
        (5, 'QUIT')
    )
    GENDER_CHOICES = (
        ('1', 'male'),
        ('2', 'female')
    )
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='members', on_delete=models.CASCADE, verbose_name='所属企业')
    userid = models.CharField(verbose_name='成员ID', max_length=64)
    open_userid = models.CharField(verbose_name='成员OpenID', max_length=64, blank=True,)
    name = models.CharField(verbose_name='成员名称', max_length=64)
    alias = models.CharField(verbose_name='成员别名', max_length=32, blank=True)
    mobile = models.CharField(verbose_name='手机号码', max_length=16, blank=True)
    address = models.CharField(verbose_name='地址', max_length=128, blank=True)
    #main_department = models.PositiveIntegerField(verbose_name='主部门', null=True)
    #department=
    #order=
    #is_leader_in_dept=
    departments = models.ManyToManyField(Department, through='DepartmentMemberRelationShip')
    position = models.CharField(verbose_name='职务', max_length=128, blank=True)
    external_position = models.CharField(verbose_name='对外职务', max_length=128, blank=True)
    gender = models.CharField(verbose_name='性别', max_length=2, choices=GENDER_CHOICES, default='1')
    email = models.EmailField(verbose_name='邮箱', blank=True)
    telephone = models.CharField(verbose_name='座机', max_length=32, blank=True)
    avatar = models.URLField(verbose_name='成员头像', blank=True)
    thumb_avatar = models.URLField(verbose_name='头像缩略图', blank=True)
    qr_code = models.URLField(verbose_name='个人二维码', blank=True)
    status = models.SmallIntegerField(verbose_name='激活状态', choices=STATUS_CHOICES, default=1)
    enable = models.BooleanField(verbose_name='启用成员', default=True)
    #extattr
    #external_profile
    #to_invite = models.BooleanField(verbose_name='邀请使用企业微信', default=True)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        unique_together = (('corp', 'userid'),)
        db_table = 'Member'
        verbose_name = '成员信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.corp.name, self.name)


class DepartmentMemberRelationShip(models.Model):
    id = models.BigAutoField(primary_key=True)
    member = models.ForeignKey(Member, related_name='dmrels', on_delete=models.CASCADE, verbose_name='成员')
    department = models.ForeignKey(Department, related_name='dmrels', on_delete=models.CASCADE, verbose_name='部门')
    order = models.PositiveIntegerField(verbose_name='在部门中的次序')
    is_leader_in_dept = models.BooleanField(verbose_name='部门领导', default=False)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        db_table = 'DepartmentMemberRelationShip'
        verbose_name = '成员部门绑定信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} {1}'.format(self.member.name, self.department.name)


class ExternalAttr(models.Model):
    ATTR_TYPE_CHOICES = (
        (0, '文本'),
        (1, '网页'),
        (2, '小程序')
    )
    id = models.BigAutoField(primary_key=True)
    corp = models.ForeignKey(Corporation, related_name='externalAttrs', on_delete=models.CASCADE, verbose_name='所属企业')
    member = models.ForeignKey(Member, related_name='externalAttrs', on_delete=models.CASCADE,
                               verbose_name='成员对外信息')
    type = models.SmallIntegerField(verbose_name='类型', choices=ATTR_TYPE_CHOICES, default=0)
    name = models.CharField(verbose_name='属性名称', max_length=64)

    # Text Attr
    value = models.CharField(verbose_name='文本属性值', max_length=64, null=True, blank=True)
    # Web Attr
    url = models.URLField(verbose_name='网页URL', null=True, blank=True)
    title = models.CharField(verbose_name='标题', max_length=64, null=True, blank=True)
    # Miniprogram
    appid = models.CharField(verbose_name='小程序appid', max_length=64)
    pagepath = models.CharField(verbose_name='小程序页面路径', max_length=64)

    class Meta:
        db_table = 'ExternalAttr'
        verbose_name = '成员对外属性'
        verbose_name_plural = verbose_name

    def __str__(self):
        type_info = ['文本', '网页', '小程序']
        return '{0} {1}属性: {2}'.format(self.corp.name, type_info[self.type], self.name)




