from django.contrib import admin

from .models import Corvet


class CorvetAdmin(admin.ModelAdmin):
    list_display = (
        'vin', 'electronique_14f', 'electronique_94f',
        'electronique_14x', 'electronique_94x',
        'electronique_14a', 'electronique_94a',
    )
    list_filter = ('donnee_silhouette', 'donnee_marque_commerciale')
    ordering = ('vin',)
    search_fields = ('vin', 'electronique_14l', 'electronique_94l')


admin.site.register(Corvet, CorvetAdmin)

