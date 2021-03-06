from django.contrib import admin

from .models import TagXelon, CsdSoftware, EtudeProject, ThermalChamber, Suptech


class TagXelonAdmin(admin.ModelAdmin):
    list_display = ('xelon', 'comments', 'created_by', 'created_at')


class ThermalChamberAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'created_by', 'xelon_number', 'start_time', 'stop_time', 'operating_mode', 'active')
    ordering = ('-created_at',)
    search_fields = ('xelon_number', 'created_by')


class SuptechAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'xelon', 'item', 'time', 'info', 'rmq', 'action')
    ordering = ('-date',)
    search_fields = ('user', 'xelon', 'item')


admin.site.register(TagXelon, TagXelonAdmin)
admin.site.register(CsdSoftware)
admin.site.register(EtudeProject)
admin.site.register(ThermalChamber, ThermalChamberAdmin)
admin.site.register(Suptech, SuptechAdmin)
