from django.contrib import admin
from .models import MaterialImage, MaterialTemp

# Register your models here.


@admin.register(MaterialImage)
class MaterialImageAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp',)
    list_display = ('id', 'pic', 'wechat_url', 'created')
    ordering = ('-created',)
    list_per_page = 20


@admin.register(MaterialTemp)
class MaterialTempAdmin(admin.ModelAdmin):
    raw_id_fields = ('corp',)
    list_display = ('id', 'media_type', 'media_file', 'media_id', 'created')
    list_filter = ('media_type', )
    ordering = ('-created',)
    list_per_page = 20

