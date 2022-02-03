from django.contrib import admin

from .models import SemRefBase, SemType, SemModel


class SemRefBaseAdmin(admin.ModelAdmin):
    list_display = ('reman_reference', 'brand', 'map_data', 'product_part', 'pf_code')
    ordering = ('reman_reference',)
    search_fields = ('reman_reference',)


class SemTypeAdmin(admin.ModelAdmin):
    list_display = ('asm_reference', 'hw_reference', 'technical_data', 'supplier_oe')
    ordering = ('asm_reference',)
    search_fields = ('asm_reference', 'hw_reference')


class SemModelAdmin(admin.ModelAdmin):
    list_display = ('pf_code_oe', 'pi_code_oe', 'sam_oe', 'hw_oe', 'vehicle', 'core_part', 'fan', 'rear_bolt', 'hw_oe')
    ordering = ('pf_code_oe',)
    search_fields = ('pf_code_oe', 'pi_code_oe', 'sam_oe', 'hw_oe', 'hw_oe')


admin.site.register(SemRefBase, SemRefBaseAdmin)
admin.site.register(SemType, SemTypeAdmin)
admin.site.register(SemModel, SemModelAdmin)
