from django.contrib import admin

from .models import Raspeedi, UnlockProduct, Programing


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


admin.site.register(Raspeedi, RaspeediAdmin)
admin.site.register(UnlockProduct, UnlockProductAdmin)
admin.site.register(Programing, ProgramingAdmin)
