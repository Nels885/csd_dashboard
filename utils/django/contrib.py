from django.contrib import admin
from django.template.defaultfilters import pluralize
from django.contrib.admin import widgets
from django.utils.translation import gettext_lazy as _


class CustomModelAdmin(admin.ModelAdmin):

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        vertical = False  # change to True if you prefer boxes to be stacked vertically
        kwargs['widget'] = widgets.FilteredSelectMultiple(
            db_field.verbose_name,
            vertical,
        )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def _message_product_about_update(self, request, rows_updated, verb):
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

    def _message_item_about_update(self, request, rows_updated, verb):
        """Send message about action to user.
        `verb` should shortly describe what have changed (e.g. 'enabled').
        """
        self.message_user(
            request,
            _('{0} item{1} {2} successfully {3}').format(
                rows_updated,
                pluralize(rows_updated),
                pluralize(rows_updated, _('was,were')),
                verb,
            ),
        )
