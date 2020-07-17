# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/7/16 3:36 下午

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
from workwechat_assist.moment.models import Moment
from .serializers import MomentSerializer
from workwechat_assist.utils.workwechat_sdk import WorkWechat
from config.settings.base import AGENT_ID
import json

User = get_user_model()
myLogger = logging.getLogger('WWAssist.moment')


class MomentViewSet(viewsets.ModelViewSet):
    serializer_class = MomentSerializer
    queryset = Moment.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('category', 'member__naruto')
    search_fields = ('member__name',)
    ordering_fields = ('created',)



