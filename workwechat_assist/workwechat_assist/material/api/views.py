# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/7/13 3:31 下午

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
from workwechat_assist.material.models import MaterialImage, MaterialTemp
from .serializers import MaterialImageSerializer, MaterialTempSerializer
from workwechat_assist.utils.workwechat_sdk import WorkWechat
from config.settings.base import AGENT_ID
import json

User = get_user_model()
myLogger = logging.getLogger('WWAssist.material')


class MaterialImageViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialImageSerializer
    queryset = MaterialImage.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ('created',)

    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        result = {'result': 'FAIL', 'message': '', 'code': 20000}

        pic = request.FILES.get('pic', None)
        if not pic:
            result['message'] = 'None image file uploaded'
            return Response(result)

        corpid = request.data.get('corpid')
        try:
            corp = Corporation.objects.get(id=corpid)
        except Corporation.DoesNotExist:
            myLogger.error('公司[{0}]不存在'.format(corpid))
            result['message'] = '公司[{0}]不存在'.format(corpid)
            return Response(result)

        mt_image = MaterialImage(corp=corp, pic=pic)
        mt_image.save()

        ret, err = mt_image.send2workwechat()
        if not ret:
            result['message'] = err
            return Response(result)

        result['result'] = 'OK'
        result['picUrl'] = mt_image.wechat_url
        return Response(result)


class MaterialTempViewSet(viewsets.ModelViewSet):
    serializer_class = MaterialTempSerializer
    queryset = MaterialTemp.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('media_type',)
    ordering_fields = ('created',)

    @action(detail=False, methods=['post'])
    def upload_media(self, request):
        result = {'result': 'FAIL', 'message': '', 'code': 20000}

        file = request.FILES.get('media_file', None)
        if not file:
            result['message'] = 'None file uploaded'
            return Response(result)

        media_type = request.data.get('media_type')
        corpid = request.data.get('corpid')
        try:
            corp = Corporation.objects.get(id=corpid)
        except Corporation.DoesNotExist:
            myLogger.error('公司[{0}]不存在'.format(corpid))
            result['message'] = '公司[{0}]不存在'.format(corpid)
            return Response(result)

        mt_temp = MaterialTemp(corp=corp, media_type=media_type, media_file=file)
        mt_temp.save()

        ret, err = mt_temp.send2workwechat()
        if not ret:
            result['message'] = err
            return Response(result)

        result['result'] = 'OK'
        result['media_id'] = mt_temp.media_id
        return Response(result)

