from django.contrib import admin
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import widgets

from .models import (
    Corvet, Multimedia, Firmware, Calibration, CorvetChoices, Ecu, CorvetProduct, CorvetAttribute, SupplierCode,
    DefaultCode, ProductChoice, CanRemote, Vehicle
)
from .forms import EcuAdminForm, MultimediaAdminForm, CanRemoteAdminForm


class CorvetListFilter(admin.SimpleListFilter):
    title = 'Marque Commerciale'

    parameter_name = 'donnee_marque_commerciale'

    def lookups(self, request, model_admin):
        return CorvetChoices.objects.filter(column='DON_MAR_COMM').values_list('key', 'value').distinct()

    def queryset(self, request, queryset):
        return queryset.filter(donnee_marque_commerciale=self.value())


class CorvetAdmin(admin.ModelAdmin):
    list_display = (
        'vin', 'donnee_marque_commerciale', 'electronique_14f', 'electronique_94f', 'electronique_14x',
        'electronique_94x', 'electronique_14a', 'electronique_94a',
    )
    list_filter = (CorvetListFilter,)
    ordering = ('vin',)
    search_fields = (
        'vin', 'electronique_14f', 'electronique_94f', 'electronique_14x', 'electronique_94x', 'electronique_14a',
        'electronique_94a',
    )


class CorvetAttributeAdmin(admin.ModelAdmin):
    list_display = ('key_1', 'key_2', 'label', 'col_ext')
    list_filter = ('key_1',)
    search_fields = ('key_1', 'key_2', 'label')


class MultimediaAdmin(admin.ModelAdmin):
    form = MultimediaAdminForm
    list_display = (
        'comp_ref', 'mat_ref', 'label_ref', 'pr_reference', 'name', 'xelon_name', 'level', 'type', 'dab', 'cam',
        'media', 'firmware', 'relation_by_name'
    )
    list_filter = ('name', 'type', 'media', 'xelon_name', 'relation_by_name')
    ordering = ('comp_ref',)
    search_fields = ('comp_ref', 'mat_ref', 'label_ref', 'name', 'xelon_name', 'type', 'pr_reference')
    actions = ('relation_by_name_disabled', 'relation_by_name_enabled')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        vertical = False  # change to True if you prefer boxes to be stacked vertically
        kwargs['widget'] = widgets.FilteredSelectMultiple(
            db_field.verbose_name,
            vertical,
        )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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

    @admin.action(description=_('Relation by name disabled'))
    def relation_by_name_disabled(self, request, queryset):
            rows_updated = queryset.update(relation_by_name=False)
            self._message_user_about_update(request, rows_updated, 'disabled')

    @admin.action(description=_('Relation by name enabled'))
    def relation_by_name_enabled(self, request, queryset):
            rows_updated = queryset.update(relation_by_name=True)
            self._message_user_about_update(request, rows_updated, 'enabled')


class FirmwareAdmin(admin.ModelAdmin):
    list_display = ('update_id', 'version', 'type', 'version_date', 'ecu_type', 'is_active')
    list_filter = ('type', 'ecu_type')
    ordering = ('-update_id',)
    search_fields = ('update_id', 'version', 'type', 'ecu_type', 'is_active')


class CalibrationAdmin(admin.ModelAdmin):
    list_display = ('factory', 'type', 'current', 'pr_reference')
    list_filter = ('type',)
    ordering = ('-factory',)
    search_fields = ('factory', 'type', 'current', 'pr_reference')


class CorvetChoicesAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'column')
    list_filter = ('column',)
    ordering = ('key', 'value', 'column')
    search_fields = ('key', 'value', 'column')


class EcuAdmin(admin.ModelAdmin):
    form = EcuAdminForm
    list_display = (
        'comp_ref', 'mat_ref', 'label_ref', 'pr_reference', 'name', 'xelon_name', 'type', 'hw', 'sw', 'supplier_oe',
        'relation_by_name'
    )
    list_filter = ('type', 'supplier_oe', 'xelon_name', 'relation_by_name')
    ordering = ('comp_ref',)
    search_fields = ('comp_ref', 'mat_ref', 'label_ref', 'pr_reference', 'name', 'xelon_name', 'type')
    actions = ('relation_by_name_disabled', 'relation_by_name_enabled')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        vertical = False  # change to True if you prefer boxes to be stacked vertically
        kwargs['widget'] = widgets.FilteredSelectMultiple(
            db_field.verbose_name,
            vertical,
        )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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

    @admin.action(description=_('Relation by name disabled'))
    def relation_by_name_disabled(self, request, queryset):
            rows_updated = queryset.update(relation_by_name=False)
            self._message_user_about_update(request, rows_updated, 'disabled')

    @admin.action(description=_('Relation by name enabled'))
    def relation_by_name_enabled(self, request, queryset):
            rows_updated = queryset.update(relation_by_name=True)
            self._message_user_about_update(request, rows_updated, 'enabled')


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
    list_display = ('name', 'family', 'short_name', 'ecu_type', 'cal_attribute', 'protocol')
    list_filter = ('family', 'ecu_type', 'protocol')
    ordering = ('name', 'family', 'short_name', 'ecu_type', 'cal_attribute', 'protocol')
    search_fields = ('name', 'short_name', 'cal_attribute')


class CanRemoteAdmin(admin.ModelAdmin):
    form = CanRemoteAdminForm
    list_display = ('label', 'location', 'type', 'product', 'can_id', 'dlc', 'data')
    list_filter = ('type', 'product',)
    ordering = ('location',)
    search_fields = ('label', 'product', 'can_id')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        vertical = False  # change to True if you prefer boxes to be stacked vertically
        kwargs['widget'] = widgets.FilteredSelectMultiple(
            db_field.verbose_name,
            vertical,
        )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Corvet, CorvetAdmin)
admin.site.register(CorvetProduct, CorvetProductAdmin)
admin.site.register(CorvetAttribute, CorvetAttributeAdmin)
admin.site.register(Multimedia, MultimediaAdmin)
admin.site.register(Firmware, FirmwareAdmin)
admin.site.register(Calibration, CalibrationAdmin)
admin.site.register(CorvetChoices, CorvetChoicesAdmin)
admin.site.register(Ecu, EcuAdmin)
admin.site.register(SupplierCode)
admin.site.register(DefaultCode, DefaultCodeAdmin)
admin.site.register(ProductChoice, ProductChoiceAdmin)
admin.site.register(CanRemote, CanRemoteAdmin)
admin.site.register(Vehicle)
