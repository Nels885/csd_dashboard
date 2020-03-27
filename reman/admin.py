from django.contrib import admin

from .models import Batch, EcuModel, Repair, SparePart


class BatchAdmin(admin.ModelAdmin):
    list_display = (str, 'quantity', 'created_by', 'created_at', 'active')


class SparePartAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'code_zone', 'code_emplacement', 'cumul_dispo')


admin.site.register(Batch, BatchAdmin)
admin.site.register(EcuModel)
admin.site.register(Repair)
admin.site.register(SparePart, SparePartAdmin)
