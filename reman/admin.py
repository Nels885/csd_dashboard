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
    list_display = ('psa_barcode', 'oe_raw_reference', 'sw_reference', 'get_ecu_type')
    ordering = ('psa_barcode',)
    search_fields = ('psa_barcode', 'ecu_type__hw_reference')

    def get_ecu_type(self, obj):
        return obj.ecu_type

    get_ecu_type.short_description = "TYPE ECU"


class EcuTypeAdmin(admin.ModelAdmin):
    list_display = ('hw_reference', 'technical_data', 'supplier_oe', 'get_spare_part')
    ordering = ('hw_reference',)
    search_fields = ('hw_reference', )

    def get_spare_part(self, obj):
        return obj.spare_part

    get_spare_part.short_description = "XELON- Code produit"


admin.site.register(Batch, BatchAdmin)
admin.site.register(EcuRefBase)
admin.site.register(EcuType, EcuTypeAdmin)
admin.site.register(EcuModel, EcuModelAdmin)
admin.site.register(Repair)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(Default)
