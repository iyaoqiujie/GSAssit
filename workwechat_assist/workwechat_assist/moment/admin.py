from django.contrib import admin
from .models import Moment

# Register your models here.


@admin.register(Moment)
class MomentAdmin(admin.ModelAdmin):
    raw_id_fields = ('member',)
    list_display = ('id', 'member', 'category', 'text', 'created')
    list_filter = ('member__name', 'category')
    ordering = ('-created',)
    list_per_page = 20
