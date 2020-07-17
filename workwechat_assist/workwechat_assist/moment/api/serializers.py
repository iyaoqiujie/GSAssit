# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/7/16 3:36 下午

import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from workwechat_assist.moment.models import Moment
import logging

User = get_user_model()
myLogger = logging.getLogger('WWAssist.moment')


class MomentSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    member_name = serializers.ReadOnlyField(source='member.name')


    class Meta:
        model = Moment
        fields = '__all__'
