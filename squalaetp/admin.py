from django.contrib import admin

from .models import Xelon, Corvet


class XelonAdmin(admin.ModelAdmin):
    list_display = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'type_de_cloture')
    list_filter = ('type_de_cloture', 'modele_vehicule')
    ordering = ('numero_de_dossier',)
    search_fields = ('numero_de_dossier', 'vin')


class CorvetAdmin(admin.ModelAdmin):
    list_display = (
        'vin', 'electronique_14f', 'electronique_94f',
        'electronique_14x', 'electronique_94x',
        'electronique_14a', 'electronique_94a',
    )
    list_filter = ('donnee_silhouette', 'donnee_marque_commerciale')
    ordering = ('vin',)
    search_fields = ('vin', 'electronique_14l', 'electronique_94l')


admin.site.register(Xelon, XelonAdmin)
admin.site.register(Corvet, CorvetAdmin)
# admin.site.register(CorvetBackup)
