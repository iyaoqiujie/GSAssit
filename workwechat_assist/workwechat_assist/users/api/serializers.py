import re
from datetime import datetime, timedelta
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging
from workwechat_assist.users.models import User

User = get_user_model()
myLogger = logging.getLogger('WWAssist.user')


class UserRegSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label='用户名', help_text='请输入用户名', required=True,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='用户已经存在')])
    password = serializers.CharField(label='密码', help_text='密码', write_only=True, style={'input_type': 'password'})

    code = serializers.IntegerField(default=20000, read_only=True)

    def create(self, validated_data):
        myLogger.debug('user:[{0}], password:[{1}]'.format(validated_data['username'], validated_data['password']))
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'password', 'code')


class UserSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)

    class Meta:
        model = User
        fields = (
        'code', 'id', 'username', 'name', 'email', 'mobile', 'role',
        'openid', 'nickName', 'avatarUrl', 'gender')
        #fields = ['id', "username", "email", "name"]

        #extra_kwargs = {
        #    "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        #}
