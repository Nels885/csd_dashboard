from django.contrib import admin
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _

from .models import Xelon, SparePart, Indicator, Action, ProductCategory


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
    list_display = ('product_model', 'category')
    list_filter = ('category', )
    search_fields = ('product_model', 'category')
    actions = (
        'psa_category_update', 'other_category_update', 'clarion_category_update', 'etude_category_update',
        'ecu_category_update', 'default_category_update'
    )

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


admin.site.register(Xelon, XelonAdmin)
admin.site.register(SparePart, SparePartAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
