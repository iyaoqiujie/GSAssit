# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/6/18 2:05 下午

import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from config.settings.base import AGENT_ID
import logging
import json
from workwechat_assist.corporation.models import Corporation, CorpApp, Department, Member
from workwechat_assist.externalcontact.models import ContactMe, Customer, CustomerFollowUserRelationship, \
    TagGroup, Tag, GroupChat, GroupMessage
from workwechat_assist.utils.workwechat_sdk import WorkWechat

User = get_user_model()
myLogger = logging.getLogger('WWAssist.externalcontact')


class ContactMeSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ContactMe
        fields = '__all__'

    # TODO
    #def validate(self, attrs):
    #    return attrs

    def create(self, validated_data):
        corp = validated_data.get('corp')
        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('APP信息获取失败')
        wechat = WorkWechat(myapp)

        status, res = wechat.add_contact_way(
            userid_li=validated_data.get('user', []),
            party_li=validated_data.get('party', []),
            type=validated_data.get('type', 2),
            scene=validated_data.get('scene', 2),
            style=validated_data.get('style', 1),
            remark=validated_data.get('remark', ''),
            skip_verify=validated_data.get('skip_verify', True),
            state=validated_data.get('state', '')
        )
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        config_id = res.get('config_id')
        myLogger.info('Successfully created the contactme: {0}'.format(config_id))

        a_contactme = ContactMe(corp=corp,
                                config_id=config_id,
                                user=validated_data.get('user', []),
                                party=validated_data.get('party', []),
                                type=validated_data.get('type', 2),
                                scene=validated_data.get('scene', 2),
                                style=validated_data.get('style', 1),
                                remark=validated_data.get('remark', ''),
                                skip_verify=validated_data.get('skip_verify', True),
                                state=validated_data.get('state', ''),
                                tags=validated_data.get('tags', []),
                                welcome_code=validated_data.get('welcome_code', {}))

        status, res = wechat.get_contact_way(config_id)
        if not status:
            myLogger.error('Error in fetching the info of the contactme[{0}]: {1}'.format(config_id, res.get('errmsg')))
        else:
            a_contactme.qr_code = res.get('contact_way').get('qr_code', '')

        a_contactme.save()

        return a_contactme

    def update(self, instance, validated_data):
        try:
            myapp = CorpApp.objects.get(corp=instance.corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('APP信息获取失败')

        remark = validated_data.get('remark', instance.remark)
        skip_verify = validated_data.get('skip_verify', instance.skip_verify)
        style = validated_data.get('style', instance.style)
        state = validated_data.get('state', instance.state)
        user = validated_data.get('user', instance.user)
        party = validated_data.get('party', instance.party)
        tags = validated_data.get('tags', instance.tags)
        welcome_code = validated_data.get('welcome_code', instance.welcome_code)

        wechat = WorkWechat(myapp)
        status, res = wechat.update_contact_way(instance.config_id,
                                                remark=remark,
                                                skip_verify=skip_verify,
                                                style=style,
                                                state=state,
                                                user=user,
                                                party=party)
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        instance.remark = remark
        instance.skip_verify = skip_verify
        instance.style = style
        instance.state = state
        instance.user = user
        instance.party = party
        instance.tags = tags
        instance.welcome_code = welcome_code

        status, res = wechat.get_contact_way(instance.config_id)
        if not status:
            myLogger.error('Error in fetching the info of the contactme[{0}]: {1}'.format(instance.config_id, res.get('errmsg')))
        else:
            instance.qr_code = res.get('contact_way').get('qr_code', '')

        instance.save()

        return instance


class CustomerSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'


class CustomJsonField(serializers.JSONField):
    default_error_messages = {
        'invalid_json': '无效的json数据格式'
    }

    def to_representation(self, value):
        return json.loads(value)

    def to_internal_value(self, data):
        try:
            data = json.dumps(data)
        except (TypeError, ValueError):
            self.fail('invalid_json')
        return data


class CustomerFollowUserRelationshipSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    member_name = serializers.ReadOnlyField(source='member.name')
    customer_name = serializers.ReadOnlyField(source='customer.name')
    tags = serializers.SerializerMethodField()
    #remark_mobiles = serializers.SerializerMethodField()
    remark_mobiles = CustomJsonField()

    def get_tags(self, obj):
        return json.loads(obj.tags)

    #def get_remark_mobiles(self, obj):
    #   return json.loads(obj.remark_mobiles)

    class Meta:
        model = CustomerFollowUserRelationship
        fields = '__all__'

    def update(self, instance, validated_data):

        remark = validated_data.get('remark', instance.remark)
        description = validated_data.get('description', instance.description)
        remark_corp_name = validated_data.get('remark_corp_name', instance.description)
        remark_mobiles = validated_data.get('remark_mobiles', instance.remark_mobiles)

        myLogger.debug('rms: {0}'.format(remark_mobiles))
        try:
            myapp = CorpApp.objects.get(corp=instance.member.corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('APP信息获取失败')

        status, res = WorkWechat(myapp).update_customer_remark(instance.member.userid,
                                                               instance.customer.external_userid,
                                                               remark=remark,
                                                               description=description,
                                                               remark_company=remark_corp_name,
                                                               remark_mobiles=json.loads(remark_mobiles))
        myLogger.debug('{0}:{1}'.format(status, res))
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        instance.remark = remark
        instance.description = description
        instance.remark_corp_name = remark_corp_name
        instance.remark_mobiles = remark_mobiles
        instance.save()

        return instance


class TagGroupSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        res = []
        for tag in obj.tags.all():
            res.append({'id': tag.id, 'tagname': tag.tagname, 'tagid': tag.tagid})
        return res

    class Meta:
        model = TagGroup
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    group_name = serializers.CharField(required=False, write_only=True)
    corpid = serializers.IntegerField(default=1, write_only=True)
    taggroup = serializers.ReadOnlyField(source='taggroup.id')

    class Meta:
        model = Tag
        fields = '__all__'

    def create(self, validated_data):
        corpid = validated_data.get('corpid', 1)
        try:
            corp = Corporation.objects.get(id=corpid)
        except Corporation.DoesNotExist:
            raise serializers.ValidationError('企业{0}信息获取失败'.format(corpid))

        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id='crm')
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('APP信息获取失败')

        group_name = validated_data.get('group_name')
        tagname = validated_data.get('tagname')
        status, res = WorkWechat(myapp).create_corp_tag(group_name=group_name, tagname_li=[tagname])
        if not status:
            myLogger.error(res.get('errmsg'))
            raise serializers.ValidationError(res.get("errmsg"))

        myLogger.info('Successfully created the tag: {0} under group: {1}'.format(tagname, group_name))
        group_res = res.get('tag_group')

        taggroup, created = TagGroup.objects.get_or_create(corp=corp, groupname=group_name)
        if created:
            taggroup.groupid = group_res.get('group_id')
            taggroup.create_time = group_res.get('create_time')
            taggroup.order = group_res.get('order')
            taggroup.save()

        created_tag = group_res.get('tag')[0]
        tag, created = Tag.objects.get_or_create(taggroup=taggroup, tagname=tagname)
        tag.tagid = created_tag.get('id')
        tag.create_time = created_tag.get('create_time')
        tag.order = created_tag.get('order')
        tag.save()

        return tag

    def update(self, instance, validated_data):
        corp = instance.taggroup.corp
        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id='crm')
        except CorpApp.DoesNotExist:
            raise serializers.ValidationError('APP信息获取失败')

        tagname = validated_data.get('tagname', instance.tagname)
        order = validated_data.get('order', instance.order)

        status, res = WorkWechat(myapp).update_corp_tag(instance.tagid, tagname, order)
        if not status:
            raise serializers.ValidationError(res.get("errmsg"))

        instance.tagname = tagname
        instance.order = order
        instance.save()

        return instance


class GroupChatSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)

    class Meta:
        model = GroupChat
        fields = '__all__'


class GroupMessageSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(default=20000, read_only=True)
    created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = GroupMessage
        fields = '__all__'
