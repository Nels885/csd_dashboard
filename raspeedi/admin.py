from django.contrib import admin

from .models import Raspeedi, UnlockProduct


class RaspeediAdmin(admin.ModelAdmin):
    list_display = ('ref_boitier', 'produit', 'facade', 'type', 'dab', 'cam', 'connecteur_ecran')
    list_filter = ('type', 'produit', 'facade')
    ordering = ('ref_boitier', 'produit',)
    search_fields = ('facade', 'type', 'produit')


admin.site.register(Raspeedi, RaspeediAdmin)
admin.site.register(UnlockProduct)
