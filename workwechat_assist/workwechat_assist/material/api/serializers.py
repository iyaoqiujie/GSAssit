# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/7/13 3:31 下午

import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from config.settings.base import AGENT_ID
import logging
import json
from workwechat_assist.material.models import MaterialTemp, MaterialImage
from workwechat_assist.utils.workwechat_sdk import WorkWechat


User = get_user_model()
myLogger = logging.getLogger('WWAssist.material')


class MaterialImageSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    corpid = serializers.IntegerField(default=1, write_only=True)

    class Meta:
        model = MaterialImage
        fields = '__all__'


class MaterialTempSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    corpid = serializers.IntegerField(default=1, write_only=True)

    class Meta:
        model = MaterialTemp
        fields = '__all__'

