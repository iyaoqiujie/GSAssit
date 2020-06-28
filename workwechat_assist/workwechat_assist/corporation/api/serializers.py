# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/6/17 12:06 下午

import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from config.settings.base import AGENT_ID
import logging
from workwechat_assist.corporation.models import Corporation, CorpApp, Department, Member, \
    DepartmentMemberRelationShip, Tag, ExternalAttr
from workwechat_assist.utils.workwechat_sdk import WorkWechat

User = get_user_model()
myLogger = logging.getLogger('WWAssist.corporation')


class CorporationSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Corporation
        fields = '__all__'


class CorpAppSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = CorpApp
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    def create(self, validated_data):
        corp = validated_data.get('corp')
        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id='contact')
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('通讯录APP信息获取失败')

        parent = validated_data.get('parent')
        order = validated_data.get('order')
        if parent:
            parentid = parent.department_id
        else:
            parentid = 1

        status, res = WorkWechat(myapp).create_department(validated_data.get('name'), parentid, order)
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        myLogger.info('Successfully created the department: {0}'.format(validated_data.get('name')))
        department_id = res.get('id')

        department = Department(corp=validated_data.get('corp'), name=validated_data.get('name'),
                                department_id=department_id, parent=parent, order=order)
        department.save()
        return department

    def update(self, instance, validated_data):
        try:
            myapp = CorpApp.objects.get(corp=instance.corp, agent_id='contact')
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('通讯录APP信息获取失败')

        name = validated_data.get('name', instance.name)
        #name_en = validated_data.get('name_en', instance.name_en)
        parent = validated_data.get('parent', instance.parent)
        order = validated_data.get('order', instance.order)

        status, res = WorkWechat(myapp).update_department(instance.department_id, name=name,
                                                          parentid=parent.department_id, order=order)
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        instance.name = name
        instance.parent = parent
        instance.order = order
        instance.save()

        return instance

    class Meta:
        model = Department
        fields = '__all__'


class MemberSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Member
        fields = '__all__'


class DMRelSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = DepartmentMemberRelationShip
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'

    def create(self, validated_data):
        corp = validated_data.get('corp')
        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('APP信息获取失败')

        tagname = validated_data.get('tagname')
        status, res = WorkWechat(myapp).create_tag(tagname)
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        myLogger.info('Successfully created the tag: {0}'.format(validated_data.get('tagname')))
        tagid = res.get('tagid')

        tag = Tag(corp=corp, tagname=validated_data.get('tagname'), tagid=tagid)
        tag.save()

        return tag

    def update(self, instance, validated_data):
        corp = validated_data.get('corp')
        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('APP信息获取失败')

        tagname = validated_data.get('tagname', instance.tagname)

        status, res = WorkWechat(myapp).update_tag(instance.tagid, tagname)
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        instance.tagname = tagname
        instance.save()

        return instance

