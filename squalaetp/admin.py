from django.contrib import admin
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import widgets

from .models import Xelon, SparePart, ProductCode, Indicator, Action, ProductCategory, Sivin


class XelonAdmin(admin.ModelAdmin):
    list_display = (
        'numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule', 'date_retour', 'type_de_cloture', 'vin_error', 'is_active'
    )
    list_filter = ('type_de_cloture', 'vin_error', 'is_active')
    ordering = ('-date_retour',)
    search_fields = ('numero_de_dossier', 'vin', 'modele_produit', 'modele_vehicule')
    actions = ('vin_error_disabled',)

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

    def vin_error_disabled(self, request, queryset):
        rows_updated = queryset.update(vin_error=False)
        self._message_user_about_update(request, rows_updated, 'disabled')
    vin_error_disabled.short_description = _('Vin error disabled')


class SparePartAdmin(admin.ModelAdmin):
    list_display = ('get_code_produit', 'code_magasin', 'code_zone', 'code_site', 'code_emplacement', 'cumul_dispo')
    ordering = ('code_produit__name',)
    search_fields = ('code_produit__name', 'code_magasin', 'code_zone', 'code_emplacement')

    def get_code_produit(self, obj):
        return obj.code_produit.name
    get_code_produit.short_description = 'Code Produit'


class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('date', 'products_to_repair', 'late_products', 'express_products', 'output_products')
    ordering = ('date',)


class ActionAdmin(admin.ModelAdmin):
    list_display = ('content', 'modified_at', 'modified_by', 'content_object')


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('product_model', 'category', 'corvet_type', 'animator')
    list_filter = ('category', 'corvet_type')
    search_fields = ('product_model', 'category')
    actions = (
        'psa_category_update', 'other_category_update', 'clarion_category_update', 'etude_category_update',
        'ecu_category_update', 'default_category_update', 'radio_corvet_type_update', 'btel_corvet_type_update',
        'emf_corvet_type_update', 'cmb_corvet_type_update', 'bsi_corvet_type_update', 'bsm_corvet_type_update',
        'hdc_corvet_type_update', 'cmm_corvet_type_update'
    )

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

    def psa_category_update(self, request, queryset):
        rows_updated = queryset.update(category="PSA")
        self._message_user_about_update(request, rows_updated, 'PSA')
    psa_category_update.short_description = _('Change category for PSA products')

    def other_category_update(self, request, queryset):
        rows_updated = queryset.update(category="AUTRE")
        self._message_user_about_update(request, rows_updated, 'Others Products')
    other_category_update.short_description = _('Change category for Others products')

    def clarion_category_update(self, request, queryset):
        rows_updated = queryset.update(category="CLARION")
        self._message_user_about_update(request, rows_updated, 'Clarion')
    clarion_category_update.short_description = _('Change category for Clarion')

    def etude_category_update(self, request, queryset):
        rows_updated = queryset.update(category="ETUDE")
        self._message_user_about_update(request, rows_updated, 'Etude')
    etude_category_update.short_description = _('Change category for Etude')

    def ecu_category_update(self, request, queryset):
        rows_updated = queryset.update(category="CALCULATEUR")
        self._message_user_about_update(request, rows_updated, 'Calculators')
    ecu_category_update.short_description = _('Change category for Calculators')

    def default_category_update(self, request, queryset):
        rows_updated = queryset.update(category="DEFAUT")
        self._message_user_about_update(request, rows_updated, 'Default')
    default_category_update.short_description = _('Change category for Default')

    def radio_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="RAD")
        self._message_user_about_update(request, rows_updated, 'Radio')
    radio_corvet_type_update.short_description = _('Change Corvet type for Radio')

    def btel_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="NAV")
        self._message_user_about_update(request, rows_updated, 'Navigation')
    btel_corvet_type_update.short_description = _('Change Corvet type for Navigation')

    def emf_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="EMF")
        self._message_user_about_update(request, rows_updated, 'EMF')
    emf_corvet_type_update.short_description = _('Change Corvet type for EMF')

    def cmb_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="CMB")
        self._message_user_about_update(request, rows_updated, 'CMB')
    cmb_corvet_type_update.short_description = _('Change Corvet type for CMB')

    def bsi_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="BSI")
        self._message_user_about_update(request, rows_updated, 'BSI')
    bsi_corvet_type_update.short_description = _('Change Corvet type for BSI')

    def bsm_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="BSM")
        self._message_user_about_update(request, rows_updated, 'BSM')
    bsm_corvet_type_update.short_description = _('Change Corvet type for BSM')

    def hdc_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="HDC")
        self._message_user_about_update(request, rows_updated, 'COM200x')
    hdc_corvet_type_update.short_description = _('Change Corvet type for COM200x')

    def cmm_corvet_type_update(self, request, queryset):
        rows_updated = queryset.update(corvet_type="CMM")
        self._message_user_about_update(request, rows_updated, 'CMM')
    cmm_corvet_type_update.short_description = _('Change Corvet type for CMM')


class SivinAdmin(admin.ModelAdmin):
    list_display = (
        'immat_siv', 'codif_vin', 'type_vin_cg', 'n_serie', 'marque', 'modele', 'genre_v', 'nb_portes', 'nb_pl_ass',
        'version'
    )
    list_filter = ('marque', 'nb_portes', 'nb_pl_ass', 'version')
    search_fields = ('immat_siv', 'codif_vin', 'marque', 'modele', 'genre_v')


admin.site.register(Xelon, XelonAdmin)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(ProductCode)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Sivin, SivinAdmin)
