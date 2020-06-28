# -*- coding: utf-8 -*-
# Author：Qiujie Yao
# Email: yaoqiujie@gscopetech.com
# @Time: 2020/6/1 11:37 上午


def jwt_response_payload_handler(token, user=None, request=None):
    """为返回的结果添加用户相关信息"""

    return {
        'code': 20000,
        'token': token,
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'mobile': user.mobile,
        'email': user.email,
        'roles': user.role,
        'nickName': user.nickName,
        'avatarUrl': user.avatarUrl,
    }
