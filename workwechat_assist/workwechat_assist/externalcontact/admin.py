from django.contrib import admin
from .models import ContactMe, Customer, CustomerFollowUserRelationship, TagGroup, Tag, GroupChat, GroupMessage

# Register your models here.


@admin.register(ContactMe)
class ContactMeAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp', )
    list_display = ('id', 'config_id', 'type', 'scene', 'skip_verify', 'remark', 'qr_code', 'state', 'user', 'party')
    list_filter = ('type', 'scene', 'skip_verify')
    search_fields = ('config_id', 'state')
    ordering = ('-created',)
    list_per_page = 20


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp', 'members')
    list_display = ('id', 'name', 'avatar', 'type', 'gender', 'position',)
    search_fields = ('name',)
    ordering = ('-created',)
    list_per_page = 20


@admin.register(CustomerFollowUserRelationship)
class CustomerFollowUserRelationshipAdmin(admin.ModelAdmin):
    raw_id_fields = ('member', 'customer')
    list_display = ('id', 'customer', 'member', 'remark', 'description', 'remark_corp_name', 'createtime',
                    'tags', 'remark_mobiles', 'add_way', 'state')
    list_filter = ('member', 'add_way')
    search_fields = ('member__name', 'customer__name')
    ordering = ('-createtime',)
    list_per_page = 20


@admin.register(TagGroup)
class TagGroupAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp',)
    list_display = ('id', 'groupname', 'groupid', 'corp')
    search_fields = ('groupname', )
    ordering = ('-groupname',)
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    raw_id_fields = ('taggroup',)
    list_display = ('id', 'tagname', 'tagid', 'taggroup')
    search_fields = ('taggroup__groupname', 'tagname')
    ordering = ('-create_time',)
    list_per_page = 20


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'chat_id', 'owner', 'notice', 'members')
    search_fields = ('name', 'owner')
    ordering = ('-create_time',)
    list_per_page = 20


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'msg_id', 'content', 'detail_list', 'created')
    ordering = ('-created',)
    list_per_page = 20
