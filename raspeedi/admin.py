from django.contrib import admin

from .models import Raspeedi, UnlockProduct


class RaspeediAdmin(admin.ModelAdmin):
    list_display = ('ref_boitier', 'produit', 'facade', 'type', 'dab', 'cam', 'connecteur_ecran')
    list_filter = ('type', 'produit', 'facade')
    ordering = ('ref_boitier', 'produit',)
    search_fields = ('facade', 'type', 'produit')


class UnlockProductAdmin(admin.ModelAdmin):
    list_display = ('unlock', 'user', 'created_at', 'active')
    ordering = ('unlock', 'user', 'created_at')
    search_fields = ('unlock', 'user')


admin.site.register(Raspeedi, RaspeediAdmin)
admin.site.register(UnlockProduct, UnlockProductAdmin)
