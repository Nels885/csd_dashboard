from django.contrib import admin

from .models import Raspeedi, UnlockProduct, Programing, ToolStatus, AETLog, AETMeasure


class RaspeediAdmin(admin.ModelAdmin):
    list_display = ('ref_boitier', 'produit', 'facade', 'type', 'dab', 'cam', 'connecteur_ecran')
    list_filter = ('type', 'produit', 'facade')
    ordering = ('ref_boitier', 'produit',)
    search_fields = ('facade', 'type', 'produit')


class UnlockProductAdmin(admin.ModelAdmin):
    list_display = ('unlock', 'user', 'created_at', 'active')
    ordering = ('unlock', 'user', 'created_at')
    search_fields = ('unlock', 'user')


class ProgramingAdmin(admin.ModelAdmin):
    list_display = ('psa_barcode', 'get_name',  'get_type', 'peedi_path', 'peedi_dump', 'renesas_dump')
    ordering = ('psa_barcode', 'peedi_path', 'peedi_dump', 'renesas_dump')
    list_filter = ('peedi_path', 'multimedia__name', 'multimedia__type')
    search_fields = ('peedi_path', 'multimedia__name', 'multimedia__type')

    def get_name(self, obj):
        return obj.multimedia.get_name_display()

    def get_type(self, obj):
        return obj.multimedia.get_type_display()

    get_name.short_description = "modèle"
    get_type.short_description = "type"


class ToolStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'url', 'last_boot', 'firmware', 'fw_version')
    search_fields = ('name', 'type')


class AETLogAdmin(admin.ModelAdmin):
    list_display = ('xelon', 'comp_ref', 'manu_ref', 'aet_name', 'prod_name', 'date')
    search_fields = ('xelon', 'comp_ref', 'manu_ref', 'aet_name', 'prod_name', 'date')
    list_filter = ('aet_name', 'prod_name')
    ordering = ('xelon', 'comp_ref', 'manu_ref', 'aet_name', 'prod_name', 'date')


class AETMeasureAdmin(admin.ModelAdmin):
    list_display = ('get_xelon', 'get_aet_name', 'measure_name', 'measured_value', 'min_value', 'max_value')
    search_fields = ('measure_name',)
    list_filter = ('measure_name',)

    def get_xelon(self, obj):
        return obj.content_object.xelon

    def get_aet_name(self, obj):
        return obj.content_object.aet_name


admin.site.register(Raspeedi, RaspeediAdmin)
admin.site.register(UnlockProduct, UnlockProductAdmin)
admin.site.register(Programing, ProgramingAdmin)
admin.site.register(ToolStatus, ToolStatusAdmin)
admin.site.register(AETLog, AETLogAdmin)
admin.site.register(AETMeasure, AETMeasureAdmin)
