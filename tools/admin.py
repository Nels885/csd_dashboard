from django.contrib import admin

from .models import TagXelon, CsdSoftware


class TagXelonAdmin(admin.ModelAdmin):
    list_display = ('xelon', 'comments', 'created_by', 'created_at')


admin.site.register(TagXelon, TagXelonAdmin)
admin.site.register(CsdSoftware)
