from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from utils.django.contrib import CustomModelAdmin

from .models import (
    Corvet, Multimedia, Firmware, Calibration, CorvetChoices, Ecu, CorvetProduct, CorvetAttribute, SupplierCode,
    DefaultCode, ProductChoice, CanRemote, Vehicle
)
from .forms import (
    EcuAdminForm, MultimediaAdminForm, CanRemoteAdminForm, CalibrationAdminForm, FirmwareAdminForm,
    ProductChoiceAdminForm
)


class CorvetListFilter(admin.SimpleListFilter):
    title = 'Marque Commerciale'

    parameter_name = 'donnee_marque_commerciale'

    def lookups(self, request, model_admin):
        return CorvetChoices.objects.filter(column='DON_MAR_COMM').values_list('key', 'value').distinct()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(donnee_marque_commerciale=self.value())
        return queryset


class CorvetAdmin(CustomModelAdmin):
    list_display = (
        'vin', 'donnee_marque_commerciale', 'electronique_14f', 'electronique_94f', 'electronique_14x',
        'electronique_94x', 'electronique_14a', 'electronique_94a', 'get_update'
    )
    list_filter = (CorvetListFilter, 'opts__update')
    ordering = ('vin',)
    search_fields = (
        'vin', 'electronique_14f', 'electronique_94f', 'electronique_14x', 'electronique_94x', 'electronique_14a',
        'electronique_94a',
    )

    @admin.display(description=_('Update'))
    def get_update(self, obj):
        if obj.opts.update:
            return _('Yes')
        return _('No')


class CorvetAttributeAdmin(admin.ModelAdmin):
    list_display = ('key_1', 'key_2', 'label', 'col_ext')
    list_filter = ('key_1',)
    search_fields = ('key_1', 'key_2', 'label')


class MultimediaAdmin(CustomModelAdmin):
    form = MultimediaAdminForm
    list_display = (
        'comp_ref', 'mat_ref', 'label_ref', 'pr_reference', 'name', 'xelon_name', 'level', 'type', 'dab', 'cam',
        'media', 'emmc', 'firmware', 'relation_by_name'
    )
    list_filter = ('name', 'type', 'media', 'xelon_name', 'relation_by_name')
    ordering = ('comp_ref',)
    search_fields = ('comp_ref', 'mat_ref', 'label_ref', 'name', 'xelon_name', 'type', 'pr_reference')
    actions = ('relation_by_name_disabled', 'relation_by_name_enabled')

    @admin.action(description=_('Relation by name disabled'))
    def relation_by_name_disabled(self, request, queryset):
        rows_updated = queryset.update(relation_by_name=False)
        self._message_product_about_update(request, rows_updated, 'disabled')

    @admin.action(description=_('Relation by name enabled'))
    def relation_by_name_enabled(self, request, queryset):
        rows_updated = queryset.update(relation_by_name=True)
        self._message_product_about_update(request, rows_updated, 'enabled')


class FirmwareAdmin(admin.ModelAdmin):
    form = FirmwareAdminForm
    list_display = ('update_id', 'version', 'type', 'version_date', 'ecu_type', 'is_active')
    list_filter = ('type', 'ecu_type')
    ordering = ('-update_id',)
    search_fields = ('update_id', 'version', 'type', 'ecu_type', 'is_active')


class CalibrationAdmin(admin.ModelAdmin):
    form = CalibrationAdminForm
    list_display = ('factory', 'get_type', 'get_type_display', 'current', 'pr_reference')
    list_filter = ('type',)
    ordering = ('-factory',)
    search_fields = ('factory', 'type', 'current', 'pr_reference')

    def get_type(self, obj):
        return f"electronique_{obj.type}"

    def get_type_display(self, obj):
        return obj.get_type_display()

class CorvetChoicesAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'column')
    list_filter = ('column',)
    ordering = ('key', 'value', 'column')
    search_fields = ('key', 'value', 'column')


class EcuAdmin(CustomModelAdmin):
    form = EcuAdminForm
    list_display = (
        'comp_ref', 'mat_ref', 'label_ref', 'pr_reference', 'name', 'xelon_name', 'type', 'hw', 'sw', 'supplier_oe',
        'relation_by_name'
    )
    list_filter = ('type', 'supplier_oe', 'xelon_name', 'relation_by_name')
    ordering = ('comp_ref',)
    search_fields = ('comp_ref', 'mat_ref', 'label_ref', 'pr_reference', 'name', 'xelon_name', 'type')
    actions = ('relation_by_name_disabled', 'relation_by_name_enabled')

    @admin.action(description=_('Relation by name disabled'))
    def relation_by_name_disabled(self, request, queryset):
        rows_updated = queryset.update(relation_by_name=False)
        self._message_product_about_update(request, rows_updated, 'disabled')

    @admin.action(description=_('Relation by name enabled'))
    def relation_by_name_enabled(self, request, queryset):
        rows_updated = queryset.update(relation_by_name=True)
        self._message_product_about_update(request, rows_updated, 'enabled')


class CorvetProductAdmin(admin.ModelAdmin):
    list_display = ('corvet', 'btel', 'radio', 'emf', 'bsi', 'bsm', 'cmm', 'hdc')
    ordering = ('corvet',)
    search_fields = (
        'corvet__vin', 'btel__name', 'radio__name', 'emf__name', 'bsi__name', 'bsm__name', 'cmm__name', 'hdc__name'
    )


class DefaultCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'type', 'characterization', 'ecu_type')
    list_filter = ('ecu_type',)
    ordering = ('code', 'description', 'ecu_type')
    search_fields = ('code', 'description', 'type', 'ecu_type')


class ProductChoiceAdmin(admin.ModelAdmin):
    form = ProductChoiceAdminForm
    list_display = ('name', 'family', 'short_name', 'ecu_type', 'cal_attribute', 'protocol', 'uce_code', 'unlock_key', 'supplier')
    list_filter = ('family', 'ecu_type', 'protocol')
    ordering = ('name', 'family', 'short_name', 'ecu_type', 'cal_attribute', 'protocol')
    search_fields = ('name', 'short_name', 'cal_attribute')


class CanRemoteAdmin(CustomModelAdmin):
    form = CanRemoteAdminForm
    list_display = ('label', 'location', 'type', 'product', 'get_vehicle', 'can_id', 'dlc', 'data')
    list_filter = ('type', 'product',)
    ordering = ('location',)
    search_fields = ('label', 'product', 'can_id', 'vehicles__name')

    def get_vehicle(self, obj):
        return ", ".join(query.name for query in obj.vehicles.all())


class SupplierCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    ordering = ('code',)
    search_fields = ('code', 'name')


admin.site.register(Corvet, CorvetAdmin)
admin.site.register(CorvetProduct, CorvetProductAdmin)
admin.site.register(CorvetAttribute, CorvetAttributeAdmin)
admin.site.register(Multimedia, MultimediaAdmin)
admin.site.register(Firmware, FirmwareAdmin)
admin.site.register(Calibration, CalibrationAdmin)
admin.site.register(CorvetChoices, CorvetChoicesAdmin)
admin.site.register(Ecu, EcuAdmin)
admin.site.register(SupplierCode, SupplierCodeAdmin)
admin.site.register(DefaultCode, DefaultCodeAdmin)
admin.site.register(ProductChoice, ProductChoiceAdmin)
admin.site.register(CanRemote, CanRemoteAdmin)
admin.site.register(Vehicle)
