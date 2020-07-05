# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/6/18 2:05 下午


from django.contrib.auth import get_user_model
from rest_framework import permissions, authentication
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.serializers import ValidationError
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
# Search, Ordering, Filter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
import logging
from workwechat_assist.corporation.models import Corporation, CorpApp, Department, Member
from workwechat_assist.externalcontact.models import ContactMe, Customer, CustomerFollowUserRelationship, \
    TagGroup, Tag, GroupChat, GroupMessage
from .serializers import ContactMeSerializer, CustomerSerializer, CustomerFollowUserRelationshipSerializer, \
    TagGroupSerializer, TagSerializer, GroupChatSerializer, GroupMessageSerializer
from workwechat_assist.utils.workwechat_sdk import WorkWechat
from config.settings.base import AGENT_ID
import json

User = get_user_model()
myLogger = logging.getLogger('WWAssist.externalcontact')


class ContactMeViewSet(viewsets.ModelViewSet):
    serializer_class = ContactMeSerializer
    queryset = ContactMe.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('type', 'scene', 'skip_verify')
    search_fields = ('config_id', 'state', 'remark')
    ordering_fields = ('created',)

    def perform_destroy(self, instance):
        try:
            myapp = CorpApp.objects.get(corp=instance.corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            myLogger.debug('Failed to delete the contactme: [{0}]'.format(instance.config_id))
            return

        status, res = WorkWechat(myapp).del_contact_way(instance.config_id)
        if not status:
            myLogger.error(res.get('errmsg'))
            raise ValidationError(res.get('errmsg'))
        else:
            myLogger.debug('Successfully deleted the contactme: [{0}]'.format(instance.config_ids))

        instance.delete()


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', )
    ordering_fields = ('created',)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        result = {'result': 'FAIL', 'message': '', 'code': 20000}
        corpid = request.data.get('corpid')
        try:
            corp = Corporation.objects.get(id=corpid)
        except Corporation.DoesNotExist:
            myLogger.error('公司[{0}]不存在'.format(corpid))
            result['message'] = '公司[{0}]不存在'.format(corpid)
            return Response(result)

        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            myLogger.error('应用获取失败')
            result['message'] = '应用获取失败'
            return Response(result)

        wechat = WorkWechat(myapp)
        status, res = wechat.get_follow_user_list()
        if not status:
            result['message'] = res.get('errmsg')
            return Response(result)

        follow_user = res.get('follow_user')
        customer_li = []
        for user in follow_user:
            status, res = wechat.get_customer_list(user)
            if status:
                customer_li.extend(res.get('external_userid'))
            else:
                myLogger.error('Failed to get the customer list for user: {0}'.format(user))

        for c in list(set(customer_li)):
            status, res = wechat.get_customer_detail(c)
            myLogger.debug(res)
            a_customer, created = Customer.objects.get_or_create(corp=corp, external_userid=c)
            customer_info = res.get('external_contact')
            a_customer.name = customer_info.get('name')
            a_customer.type = customer_info.get('type', 1)
            a_customer.avatar = customer_info.get('avatar')
            a_customer.gender = customer_info.get('gender')
            a_customer.save()

            # Setup the bounding
            follow_user_li = res.get('follow_user')
            for f in follow_user_li:
                myLogger.debug('remark info:{0}'.format(f))
                try:
                    a_member = Member.objects.get(corp=corp, userid=f.get('userid'))
                    cfurel, created = CustomerFollowUserRelationship.objects.get_or_create(member=a_member, customer=a_customer)
                    cfurel.remark = f.get('remark')
                    cfurel.description = f.get('description')
                    cfurel.createtime = f.get('createtime')
                    cfurel.remark_corp_name = f.get('remark_corp_name', '')
                    cfurel.add_way = f.get('add_way', 0)
                    cfurel.remark_mobiles = json.dumps(f.get('remark_mobiles')).encode('utf-8').decode('unicode_escape')
                    cfurel.tags = json.dumps(f.get('tags')).encode('utf-8').decode('unicode_escape')
                    cfurel.save()
                except Member.DoesNotExist:
                    myLogger.error('成员{0}不存在'.format(f.get('userid')))

        result['result'] = 'OK'
        return Response(result)


class CustomerFollowUserRelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerFollowUserRelationshipSerializer
    queryset = CustomerFollowUserRelationship.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('member__name', 'customer__name',)
    ordering_fields = ('createtime',)

    @action(detail=True, methods=['post'])
    def mark_tag(self, request, pk=None):
        result = {'result': 'FAIL', 'message': '', 'code': 20000}
        instance = self.get_object()

        try:
            myapp = CorpApp.objects.get(corp=instance.member.corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            result['message'] = '应用获取失败'
            return Response(result)

        tags = request.data.get('tags', [])
        isadd = request.data.get('isadd', '0')

        wechat = WorkWechat(myapp)
        if isadd == '0':
            status, res = wechat.mark_tag(instance.member.userid,
                                          instance.customer.external_userid,
                                          remove_tag=tags)
        else:
            status, res = wechat.mark_tag(instance.member.userid,
                                          instance.customer.external_userid,
                                          add_tag=tags)

        if not status:
            result['message'] = res.get('errmsg')
            return Response(result)

        status, res = wechat.get_customer_detail(instance.customer.external_userid)
        if not status:
            result['message'] = res.get('errmsg')
            return Response(result)

        follow_user_li = res.get('follow_user')
        for f in follow_user_li:
            if f.get('userid') == instance.member.userid:
                instance.tags = json.dumps(f.get('tags'))
                instance.save()
                result['result'] = 'OK'
                return Response(result)


class TagGroupViewSet(viewsets.ModelViewSet):
    serializer_class = TagGroupSerializer
    queryset = TagGroup.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('groupname',)
    ordering_fields = ('create_time',)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('taggroup__groupname', 'tagname')
    ordering_fields = ('create_time',)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        result = {'result': 'FAIL', 'message': '', 'code': 20000}
        corpid = request.data.get('corpid')
        try:
            corp = Corporation.objects.get(id=corpid)
        except Corporation.DoesNotExist:
            myLogger.error('公司[{0}]不存在'.format(corpid))
            result['message'] = '公司[{0}]不存在'.format(corpid)
            return Response(result)

        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id='crm')
        except CorpApp.DoesNotExist:
            myLogger.error('应用获取失败')
            result['message'] = '应用获取失败'
            return Response(result)

        wechat = WorkWechat(myapp)
        status, res = wechat.get_corp_tag_list()
        if not status:
            result['message'] = res.get('errmsg')
            return Response(result)

        tag_groups = res.get('tag_group')
        for g in tag_groups:
            taggroup, created = TagGroup.objects.get_or_create(corp=corp, groupname=g.get('group_name'))
            taggroup.groupid = g.get('group_id')
            taggroup.create_time = g.get('create_time')
            taggroup.order = g.get('order')
            taggroup.save()

            tags = g.get('tag')
            for t in tags:
                tag, created = Tag.objects.get_or_create(taggroup=taggroup, tagname=t.get('name'))
                tag.tagid = t.get('id')
                tag.create_time = t.get('create_time')
                tag.order = t.get('order')
                tag.save()

        result['result'] = 'OK'
        return Response(result)

    def destroy(self, request, *args, **kwargs):
        result = {'result': 'FAIL', 'message': '', 'code': 20000}
        instance = self.get_object()
        try:
            myapp = CorpApp.objects.get(corp=instance.taggroup.corp, agent_id='crm')
        except CorpApp.DoesNotExist:
            myLogger.debug('Failed to delete the tag: [{0}]'.format(instance.tagname))
            result['message'] = 'Failed to delete the tag: [{0}]'.format(instance.tagname)
            return Response(result)

        status, res = WorkWechat(myapp).delete_corp_tag([instance.tagid])
        if not status:
            myLogger.debug(res.get('errmsg'))
            result['message'] = res.get('errmsg')
            return Response(result)
        else:
            myLogger.debug('Successfully deleted the tag: [{0}]'.format(instance.tagname))

        tgroup = instance.taggroup
        instance.delete()

        # If all the tags under the group were deleted, delete the taggroup
        if tgroup.tags.count() == 0:
            tgroup.delete()

        result['result'] = 'OK'
        return Response(result)


class GroupChatViewSet(viewsets.ModelViewSet):
    serializer_class = GroupChatSerializer
    queryset = GroupChat.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'owner')
    ordering_fields = ('create_time',)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        result = {'result': 'FAIL', 'message': '', 'code': 20000}
        corpid = request.data.get('corpid')
        try:
            corp = Corporation.objects.get(id=corpid)
        except Corporation.DoesNotExist:
            myLogger.error('公司[{0}]不存在'.format(corpid))
            result['message'] = '公司[{0}]不存在'.format(corpid)
            return Response(result)

        try:
            myapp = CorpApp.objects.get(corp=corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            myLogger.error('应用获取失败')
            result['message'] = '应用获取失败'
            return Response(result)

        wechat = WorkWechat(myapp)
        wechat = WorkWechat(myapp)
        status, res = wechat.get_groupchat_list()
        if not status:
            result['message'] = res.get('errmsg')
            return Response(result)

        groupchat_list = res.get('group_chat_list')
        for g in groupchat_list:
            chat_id = g.get('chat_id')
            chat_status = g.get('status')

            # Fetch the detail of the groupchat
            status, res = wechat.get_groupchat_detail(chat_id)
            if not status:
                myLogger.error('Error in fetch the groupchat detail: {0}'.format(res.get('errmsg')))

            chat_detail = res.get('group_chat')
            a_chat, created = GroupChat.objects.get_or_create(corp=corp, chat_id=chat_id)
            a_chat.name = chat_detail.get('name')
            a_chat.owner = chat_detail.get('owner')
            a_chat.create_time = chat_detail.get('create_time')
            a_chat.notice = chat_detail.get('notice', '')
            a_chat.members = chat_detail.get('member_list')
            a_chat.status = chat_status
            a_chat.save()

        result['result'] = 'OK'
        return Response(result)


class GroupMessageViewSet(viewsets.ModelViewSet):
    serializer_class = GroupMessageSerializer
    queryset = GroupMessage.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ('created',)




