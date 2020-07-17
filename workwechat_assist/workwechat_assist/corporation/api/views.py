# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/6/17 12:06 下午

from django.contrib.auth import get_user_model
from rest_framework import permissions, authentication
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
# Search, Ordering, Filter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
import logging
import uuid
from workwechat_assist.corporation.models import Corporation, CorpApp, Department, Member, \
    DepartmentMemberRelationShip, Tag, ExternalAttr
from .serializers import CorporationSerializer, CorpAppSerializer, DepartmentSerializer, MemberSerializer, \
    DMRelSerializer, TagSerializer
from workwechat_assist.utils.workwechat_sdk import WorkWechat
from config.settings.base import AGENT_ID

User = get_user_model()
myLogger = logging.getLogger('WWAssist.corporation')


class CorporationViewSet(viewsets.ModelViewSet):
    serializer_class = CorporationSerializer
    queryset = Corporation.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'corp_id', 'phone')
    ordering_fields = ('-created', )


class CorpAppViewSet(viewsets.ModelViewSet):
    serializer_class = CorpAppSerializer
    queryset = CorpApp.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'corp__name')
    ordering_fields = ('-created', )


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'corp__name',)
    ordering_fields = ('department_id', 'order', 'created', )

    def perform_destroy(self, instance):
        try:
            myapp = CorpApp.objects.get(corp=instance.corp, agent_id='contact')
        except CorpApp.DoesNotExist:
            myLogger.debug('Failed to delete the department: [{0}, {1}]'.format(instance.name, instance.department_id))
            return

        status, res = WorkWechat(myapp).delete_department(instance.department_id)
        if not status:
            myLogger.debug(res.get('errmsg'))
            return
        else:
            myLogger.debug('Successfully deleted the department: [{0}, {1}]'.format(
                instance.name, instance.department_id))

        instance.delete()


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    queryset = Member.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'corp__name')
    ordering_fields = ('-created', )

    @action(detail=False, methods=['post'])
    def sync_members(self, request):
        result = {'result': 'FAIL', 'message': ''}
        corpid = request.data.get('corpid')
        try:
            corp = Corporation.objects.get(id=corpid)
        except Corporation.DoesNotExist:
            myLogger.error('公司[{0}]不存在'.format(corpid))
            result['message'] = '公司[{0}]不存在'.format(corpid)
            return Response(result)

        try:
            contactapp = CorpApp.objects.get(corp=corp, agent_id='contact')
        except CorpApp.DoesNotExist:
            myLogger.error('通讯录应用获取失败')
            result['message'] = '通讯录应用获取失败'
            return Response(result)

        status, res = WorkWechat(contactapp).get_users_in_department_detail(request.data.get('departmentid'),
                                                                            fetch_child=1)
        if not status:
            result['message'] = res.get('errmsg')
            return Response(result)

        for u in res.get('userlist'):
            myLogger.debug(u)
            myLogger.debug(type(u))
            m, created = Member.objects.get_or_create(corp=corp, userid=u.get('userid'))
            m.naruto = uuid.uuid3(uuid.NAMESPACE_URL, m.userid)
            m.name = u.get('name')
            m.position = u.get('position')
            m.mobile = u.get('mobile')
            m.gender = u.get('gender')
            m.email = u.get('email')
            m.avatar = u.get('avatar')
            m.status = u.get('status')
            m.enable = u.get('enable')
            m.telephone = u.get('telephone')
            m.qr_code = u.get('qr_code')
            m.alias = u.get('alias')
            m.thumb_avatar = u.get('thumb_avatar')
            m.save()

        result['result'] = 'OK'
        return Response(result)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'corp__name')
    ordering_fields = ('-created', )

    @action(detail=False, methods=['post'])
    def add_tag_users(self, request):
        pass

    @action(detail=False, methods=['post'])
    def del_tag_users(self, request):
        pass

    @action(detail=False, methods=['post'])
    def get_tag_users(self, request):
        result = {'result': 'FAIL', 'message': ''}
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

        tagid = request.data.get('tagid')
        status, res = WorkWechat(myapp).get_user_from_tag(tagid)
        if not status:
            result['message'] = res.get('errmsg')
            return Response(result)

        result['result'] = 'OK'
        result['tagname'] = res.get('tagname')
        result['userlist'] = res.get('userlist')
        result['partylist'] = res.get('partylist')

        return Response(result)

    def perform_destroy(self, instance):
        try:
            myapp = CorpApp.objects.get(corp=instance.corp, agent_id=AGENT_ID)
        except CorpApp.DoesNotExist:
            myLogger.debug('Failed to find the app')
            return

        status, res = WorkWechat(myapp).delete_tag(instance.tagid)
        if not status:
            myLogger.debug(res.get('errmsg'))
            return
        else:
            myLogger.debug('Successfully deleted the tag: [{0}, {1}]'.format(
                instance.tagname, instance.tagid))

        instance.delete()
