from django.contrib import admin

from .models import Corvet, Product, Firmware


class CorvetAdmin(admin.ModelAdmin):
    list_display = (
        'vin', 'electronique_14f', 'electronique_94f',
        'electronique_14x', 'electronique_94x',
        'electronique_14a', 'electronique_94a',
    )
    list_filter = ('donnee_silhouette', 'donnee_marque_commerciale')
    ordering = ('vin',)
    search_fields = ('vin', 'electronique_14l', 'electronique_94l')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('reference', 'name', 'front', 'type', 'dab', 'cam', 'media', 'carto')
    list_filter = ('name', 'front', 'type', 'media', 'carto')
    ordering = ('reference',)
    search_fields = ('reference', 'name', 'type')


class FirmwareAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'version', 'type', 'version_date', 'ecu_type', 'is_active')
    list_filter = ('type', 'ecu_type')
    ordering = ('-update_id',)
    search_fields = ('update_id', 'version', 'type', 'ecu_type', 'is_active')


admin.site.register(Corvet, CorvetAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Firmware, FirmwareAdmin)
