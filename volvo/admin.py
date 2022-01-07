from django.contrib import admin

from .models import SemRefBase


class SemRefBaseAdmin(admin.ModelAdmin):
    list_display = ('reman_reference', 'map_data', 'oe_reference', 'pf_code', 'asm', 'hw')
    ordering = ('reman_reference',)
    search_fields = ('reman_reference',)


admin.site.register(SemRefBase, SemRefBaseAdmin)
