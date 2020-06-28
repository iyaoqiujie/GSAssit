from rest_framework import serializers

from workwechat_assist.users.models import User


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
