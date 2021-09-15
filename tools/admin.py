from django.contrib import admin

from .models import (
    TagXelon, CsdSoftware, EtudeProject, ThermalChamber, ThermalChamberMeasure, Suptech, SuptechItem, SuptechMessage,
    BgaTime
)


class TagXelonAdmin(admin.ModelAdmin):
    list_display = ('xelon', 'comments', 'created_by', 'created_at')


class ThermalChamberAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'created_by', 'xelon_number', 'start_time', 'stop_time', 'operating_mode', 'active')
    ordering = ('-created_at',)
    search_fields = ('xelon_number', 'created_by')


class ThermalChamberMeasureAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'value', 'temp')
    search_fields = ('datetime',)


class SuptechAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action', 'status')
    ordering = ('-date',)
    list_filter = ('status',)
    search_fields = ('id', 'user', 'xelon', 'item')


class SuptechItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'extra', 'mailing_list')
    ordering = ('name',)
    search_fields = ('name', 'mailing_list')


class SuptechMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'added_at', 'added_by', 'content_object')


admin.site.register(TagXelon, TagXelonAdmin)
admin.site.register(CsdSoftware)
admin.site.register(EtudeProject)
admin.site.register(ThermalChamber, ThermalChamberAdmin)
admin.site.register(Suptech, SuptechAdmin)
admin.site.register(SuptechItem, SuptechItemAdmin)
admin.site.register(SuptechMessage, SuptechMessageAdmin)
admin.site.register(BgaTime)
admin.site.register(ThermalChamberMeasure, ThermalChamberMeasureAdmin)
