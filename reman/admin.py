from django.contrib import admin

from .models import Batch, EcuModel, Repair, SparePart, Default, EcuRefBase, EcuType


class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'quantity', 'created_by', 'created_at', 'active')
    ordering = ('batch_number',)
    search_fields = ('batch_number',)

    def batch_number(self, obj):
        return obj

    batch_number.short_description = "Numéro de lot"


class SparePartAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'code_zone', 'code_emplacement', 'cumul_dispo')
    ordering = ('code_produit',)
    search_fields = ('code_produit', 'code_zone', 'code_emplacement')


class EcuModelAdmin(admin.ModelAdmin):
    list_display = (
        'psa_barcode', 'oe_raw_reference', 'sw_reference'
    )


admin.site.register(Batch, BatchAdmin)
admin.site.register(EcuRefBase)
admin.site.register(EcuType)
admin.site.register(EcuModel, EcuModelAdmin)
admin.site.register(Repair)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(Default)
