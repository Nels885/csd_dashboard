from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from utils.django.contrib import CustomModelAdmin

from .models import Batch, EcuModel, Repair, RepairCloseReason, SparePart, Default, EcuRefBase, EcuType


class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'customer', 'quantity', 'box_quantity', 'created_by', 'created_at', 'active')
    ordering = ('batch_number',)
    list_filter = ('active', 'customer')
    search_fields = ('batch_number',)

    def batch_number(self, obj):
        return obj

    batch_number.short_description = _("Batch number")


class EcuRefBaseAdmin(CustomModelAdmin):
    list_display = (
        'reman_reference', 'ecu_type', 'ref_cal_out', 'ref_psa_out', 'req_diag', 'open_diag', 'req_ref', 'ref_mat',
        'ref_comp', 'req_cal', 'cal_ktag', 'req_status', 'status', 'test_clear_memory', 'cle_appli'
    )
    ordering = ('reman_reference',)
    list_filter = ('ecu_type',)
    search_fields = ('reman_reference',)


class RepairAdmin(CustomModelAdmin):
    list_display = (
        'identify_number', 'get_batch_number', 'get_customer', 'get_hw_reference', 'barcode', 'created_at', 'status',
        'quality_control', 'checkout', 'closing_date'
    )
    ordering = ('identify_number', 'batch__batch_number')
    list_filter = ('status', 'quality_control', 'checkout')
    search_fields = (
        'identify_number', 'batch__batch_number', 'batch__customer', 'batch__ecu_ref_base__ecu_type__hw_reference')
    actions = ('checkout_enabled',)

    def checkout_enabled(self, request, queryset):
        rows_updated = queryset.update(checkout=True)
        self._message_product_about_update(request, rows_updated, 'enabled')
    checkout_enabled.short_description = _('Checkout enabled')

    def get_batch_number(self, obj):
        return obj.batch.batch_number

    def get_customer(self, obj):
        return obj.batch.customer

    def get_hw_reference(self, obj):
        return obj.batch.ecu_ref_base.ecu_type.hw_reference

    get_batch_number.short_description = _("Batch number")
    get_customer.short_description = _("Customer")
    get_hw_reference.short_description = _("HW reference")


class RepairCloseReasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'extra', 'is_active')
    ordering = ('name', 'extra', 'is_active')
    search_fields = ('name',)


class SparePartAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'code_zone', 'code_emplacement', 'cumul_dispo')
    ordering = ('code_produit',)
    search_fields = ('code_produit', 'code_zone', 'code_emplacement')


class EcuModelAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'oe_raw_reference', 'oe_reference', 'get_ecu_type', 'to_dump')
    ordering = ('barcode', 'oe_raw_reference')
    list_filter = ('ecu_type', 'to_dump')
    search_fields = ('barcode', 'ecu_type__hw_reference', 'ecu_type__technical_data')

    def get_ecu_type(self, obj):
        return obj.ecu_type

    get_ecu_type.short_description = _("ECU TYPE")


class EcuTypeAdmin(admin.ModelAdmin):
    list_display = ('hw_reference', 'technical_data', 'supplier_oe', 'get_spare_part',)
    ordering = ('hw_reference',)
    list_filter = ('technical_data', 'supplier_oe')
    search_fields = ('hw_reference', 'technical_data', 'supplier_oe')

    def get_spare_part(self, obj):
        return obj.spare_part

    get_spare_part.short_description = _("XELON - Product code")


admin.site.register(Batch, BatchAdmin)
admin.site.register(EcuRefBase, EcuRefBaseAdmin)
admin.site.register(EcuType, EcuTypeAdmin)
admin.site.register(EcuModel, EcuModelAdmin)
admin.site.register(Repair, RepairAdmin)
admin.site.register(RepairCloseReason, RepairCloseReasonAdmin)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(Default)
