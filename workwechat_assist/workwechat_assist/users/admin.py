from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from workwechat_assist.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
                    ('微信用户信息', {'fields': ('openid', 'uid', 'nickName', 'avatarUrl', 'gender')}),
                    ('用户信息', {'fields': ('name', 'mobile', 'role', 'avatar')}),
                ) + auth_admin.UserAdmin.fieldsets
    list_display = ['username', 'name', 'mobile', 'nickName', 'avatarUrl', 'gender', 'role']
    search_fields = ['name', 'username', 'mobile', 'nickName']


admin.site.site_header = '盘陀企业微信助手'
admin.site.site_title = '盘陀企业微信助手'
