from django.contrib import admin

from .models import Corvet, Multimedia, Firmware, Calibration, CorvetChoices, BsiModel, EmfModel


class CorvetAdmin(admin.ModelAdmin):
    list_display = (
        'vin', 'electronique_14f', 'electronique_94f',
        'electronique_14x', 'electronique_94x',
        'electronique_14a', 'electronique_94a',
    )
    list_filter = ('donnee_silhouette', 'donnee_marque_commerciale')
    ordering = ('vin',)
    search_fields = ('vin', 'electronique_14l', 'electronique_94l')


class MultimediaAdmin(admin.ModelAdmin):
    list_display = ('hw_reference', 'name', 'level', 'type', 'dab', 'cam', 'media')
    list_filter = ('name', 'level', 'type', 'media')
    ordering = ('hw_reference',)
    search_fields = ('hw_reference', 'name', 'type')


class FirmwareAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'version', 'type', 'version_date', 'ecu_type', 'is_active')
    list_filter = ('type', 'ecu_type')
    ordering = ('-update_id',)
    search_fields = ('update_id', 'version', 'type', 'ecu_type', 'is_active')


class CalibrationAdmin(admin.ModelAdmin):
    list_display = ('factory', 'type', 'current')
    list_filter = ('type',)
    ordering = ('-factory',)
    search_fields = ('factory', 'type', 'current')


class CorvetChoicesAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'column')
    list_filter = ('column',)
    ordering = ('key', 'value', 'column')
    search_fields = ('key', 'value', 'column')


class BsiModelAdmin(admin.ModelAdmin):
    list_display = ('reference', 'name', 'hw', 'sw', 'supplier_oe')
    list_filter = ('name', 'hw', 'sw', 'supplier_oe')
    ordering = ('reference',)
    search_fields = ('reference', 'name',)


class EmfModelAdmin(admin.ModelAdmin):
    list_display = ('hw_reference', 'name', 'hw', 'sw', 'supplier_oe', 'pr_reference')
    list_filter = ('name', 'hw', 'sw', 'supplier_oe')
    ordering = ('hw_reference',)
    search_fields = ('hw_reference', 'name')


admin.site.register(Corvet, CorvetAdmin)
admin.site.register(Multimedia, MultimediaAdmin)
admin.site.register(Firmware, FirmwareAdmin)
admin.site.register(Calibration, CalibrationAdmin)
admin.site.register(CorvetChoices, CorvetChoicesAdmin)
admin.site.register(BsiModel, BsiModelAdmin)
admin.site.register(EmfModel, EmfModelAdmin)
