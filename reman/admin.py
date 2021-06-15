from django.contrib import admin
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _

from .models import Batch, EcuModel, Repair, SparePart, Default, EcuRefBase, EcuType


class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'quantity', 'created_by', 'created_at', 'active')
    ordering = ('batch_number',)
    list_filter = ('active',)
    search_fields = ('batch_number',)

    def batch_number(self, obj):
        return obj

    batch_number.short_description = "Numéro de lot"


class EcuRefBaseAdmin(admin.ModelAdmin):
    list_display = ('reman_reference', 'ecu_type')
    ordering = ('reman_reference',)
    list_filter = ('ecu_type',)
    search_fields = ('reman_reference',)


class RepairAdmin(admin.ModelAdmin):
    list_display = (
        'identify_number', 'get_batch_number', 'get_hw_reference', 'psa_barcode', 'created_at', 'status',
        'quality_control', 'checkout', 'closing_date'
    )
    ordering = ('identify_number', 'batch__batch_number')
    list_filter = ('status', 'quality_control', 'checkout')
    search_fields = ('identify_number', 'batch__batch_number', 'batch__ecu_ref_base__ecu_type__hw_reference')
    actions = ('checkout_enabled',)

    def _message_user_about_update(self, request, rows_updated, verb):
        """Send message about action to user.
        `verb` should shortly describe what have changed (e.g. 'enabled').
        """
        self.message_user(
            request,
            _('{0} product{1} {2} successfully {3}').format(
                rows_updated,
                pluralize(rows_updated),
                pluralize(rows_updated, _('was,were')),
                verb,
            ),
        )

    def checkout_enabled(self, request, queryset):
        rows_updated = queryset.update(checkout=True)
        self._message_user_about_update(request, rows_updated, 'enabled')
    checkout_enabled.short_description = _('Checkout enabled')

    def get_batch_number(self, obj):
        return obj.batch.batch_number

    def get_hw_reference(self, obj):
        return obj.batch.ecu_ref_base.ecu_type.hw_reference

    get_batch_number.short_description = "batch number"
    get_hw_reference.short_description = "hw reference"


class SparePartAdmin(admin.ModelAdmin):
    list_display = ('code_produit', 'code_zone', 'code_emplacement', 'cumul_dispo')
    ordering = ('code_produit',)
    search_fields = ('code_produit', 'code_zone', 'code_emplacement')


class EcuModelAdmin(admin.ModelAdmin):
    list_display = ('psa_barcode', 'oe_raw_reference', 'sw_reference', 'get_ecu_type', 'to_dump')
    ordering = ('psa_barcode', 'oe_raw_reference')
    list_filter = ('ecu_type', 'to_dump')
    search_fields = ('psa_barcode', 'ecu_type__hw_reference', 'ecu_type__technical_data')

    def get_ecu_type(self, obj):
        return obj.ecu_type

    get_ecu_type.short_description = "TYPE ECU"


class EcuTypeAdmin(admin.ModelAdmin):
    list_display = (
        'hw_reference', 'technical_data', 'supplier_oe', 'get_spare_part', 'ref_cal_out', 'ref_psa_out', 'req_diag',
        'open_diag', 'req_ref', 'ref_mat', 'ref_comp', 'req_cal', 'cal_ktag', 'req_status', 'status',
        'test_clear_memory', 'cle_appli'
    )
    ordering = ('hw_reference',)
    list_filter = ('technical_data', 'supplier_oe')
    search_fields = ('hw_reference', 'technical_data', 'supplier_oe')

    def get_spare_part(self, obj):
        return obj.spare_part

    get_spare_part.short_description = "XELON- Code produit"


admin.site.register(Batch, BatchAdmin)
admin.site.register(EcuRefBase, EcuRefBaseAdmin)
admin.site.register(EcuType, EcuTypeAdmin)
admin.site.register(EcuModel, EcuModelAdmin)
admin.site.register(Repair, RepairAdmin)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(Default)
