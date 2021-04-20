from django.contrib import admin

from .models import Xelon, SparePart, Indicator, Action


class XelonAdmin(admin.ModelAdmin):
    list_display = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'type_de_cloture')
    list_filter = ('type_de_cloture', 'modele_vehicule')
    ordering = ('numero_de_dossier',)
    search_fields = ('numero_de_dossier', 'vin')


class SparePartAdmin(admin.ModelAdmin):
    list_display = ('get_code_produit', 'code_magasin', 'code_zone', 'code_site', 'code_emplacement', 'cumul_dispo')
    ordering = ('code_produit__name',)
    search_fields = ('code_produit__name', 'code_magasin', 'code_zone', 'code_emplacement')

    def get_code_produit(self, obj):
        return obj.code_produit.name

    get_code_produit.short_description = 'Code Produit'


class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('date', 'products_to_repair', 'late_products', 'express_products', 'output_products')
    ordering = ('date',)


class ActionAdmin(admin.ModelAdmin):
    list_display = ('content', 'modified_at', 'modified_by', 'content_object')


admin.site.register(Xelon, XelonAdmin)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(Action, ActionAdmin)
