# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/6/28 5:02 下午

from django.urls import path

from workwechat_assist.externalcontact.views import gsassist_callback_view

app_name = 'external'
urlpatterns = [
    path('weworkcall/', view=gsassist_callback_view, name='weworkcall'),
]

