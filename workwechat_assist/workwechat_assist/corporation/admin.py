from django.contrib import admin
from .models import Corporation, CorpApp, Department, Member, DepartmentMemberRelationShip, Tag, ExternalAttr

# Register your models here.


@admin.register(Corporation)
class CorporationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'phone', 'industry_type', 'staff_size', 'corp_id',)
    filter_fields = ('industry_type', )
    search_fields = ('name', 'corp_id', 'phone')
    ordering = ('-created',)
    list_per_page = 20


@admin.register(CorpApp)
class CorpAppAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp',)
    list_display = ('id', 'name', 'corp', 'agent_id', 'secret', 'token', 'aes_key',)
    search_fields = ('name', 'corp__name', )
    ordering = ('-created',)
    list_per_page = 20


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp', 'parent')
    list_display = ('id', 'corp', 'name', 'name_en', 'department_id', 'parent', 'order',)
    search_fields = ('name', 'corp__name',)
    ordering = ('department_id', 'order', 'created',)
    list_per_page = 20


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp',)
    filter_horizontal = ('departments',)
    search_fields = ('name', 'userid', 'mobile')
    ordering = ('created',)
    list_per_page = 20


@admin.register(DepartmentMemberRelationShip)
class DMRelAdmin(admin.ModelAdmin):
    raw_id_fields = ('department', 'member')
    list_display = ('member', 'department', 'order', 'is_leader_in_dept')
    ordering = ('created',)
    list_per_page = 20

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp',)
    list_display = ('id', 'corp', 'tagname', 'tagname', 'created')
    ordering = ('-created',)
    list_per_page = 20


