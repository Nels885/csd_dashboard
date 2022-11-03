from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _

from .models import (
    TagXelon, CsdSoftware, EtudeProject, ThermalChamber, ThermalChamberMeasure, Suptech, SuptechCategory, SuptechItem,
    SuptechMessage, SuptechFile, BgaTime, ConfigFile
)


class TagXelonAdmin(admin.ModelAdmin):
    list_display = ('xelon', 'calibre', 'telecode', 'comments', 'created_by', 'created_at')
    search_fields = ('xelon', 'created_by__username')
    list_filter = ('calibre', 'telecode')


class ThermalChamberAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'created_by', 'xelon_number', 'start_time', 'stop_time', 'operating_mode', 'active')
    ordering = ('-created_at',)
    search_fields = ('xelon_number', 'created_by__username')


class ThermalChamberMeasureAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'value', 'temp')
    search_fields = ('datetime',)


class SuptechFileline(admin.TabularInline):
    model = SuptechFile


class SuptechAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'date', 'user', 'xelon', 'item', 'category', 'is_48h', 'time', 'info', 'rmq', 'action', 'status')
    ordering = ('-date',)
    list_filter = ('status', 'category', 'is_48h')
    search_fields = ('id', 'user', 'xelon', 'item')
    actions = ('is_48h_disabled', 'is_48h_enabled')
    inlines = (SuptechFileline, )

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

    def is_48h_disabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=False)
        self._message_user_about_update(request, rows_updated, 'disabled')
    is_48h_disabled.short_description = _('48h processing disabled')

    def is_48h_enabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=True)
        self._message_user_about_update(request, rows_updated, 'enabled')
    is_48h_enabled.short_description = _('48h processing enabled')


class SuptechItemAdminForm(forms.ModelForm):
    to_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=FilteredSelectMultiple("User", is_stacked=False), required=False)
    cc_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=FilteredSelectMultiple("User", is_stacked=False), required=False)

    class Meta:
        model = SuptechItem
        fields = '__all__'


class SuptechItemAdmin(admin.ModelAdmin):
    form = SuptechItemAdminForm
    list_display = ('name', 'extra', 'category', 'is_48h', 'is_active', 'mailing_list', 'cc_mailing_list')
    ordering = ('name',)
    list_filter = ('category', 'is_48h', 'is_active')
    search_fields = ('name', 'mailing_list', 'cc_mailing_list')
    actions = ('is_48h_disabled', 'is_48h_enabled', 'is_disabled', 'is_activated')

    def _message_user_about_update(self, request, rows_updated, verb):
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

    def is_48h_disabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=False)
        self._message_user_about_update(request, rows_updated, 'disabled')
    is_48h_disabled.short_description = _('48h processing disabled')

    def is_48h_enabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=True)
        self._message_user_about_update(request, rows_updated, 'enabled')
    is_48h_enabled.short_description = _('48h processing enabled')

    def is_disabled(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self._message_user_about_update(request, rows_updated, 'disabled')
    is_disabled.short_description = _('Item disabled')

    def is_activated(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self._message_user_about_update(request, rows_updated, 'activated')
    is_activated.short_description = _('Item activated')


class SuptechCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')


class SuptechMessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'added_at', 'added_by', 'content_object')


class SuptechFileAdmin(admin.ModelAdmin):
    list_display = ('suptech', 'file')
    ordering = ('suptech',)


admin.site.register(TagXelon, TagXelonAdmin)
admin.site.register(CsdSoftware)
admin.site.register(EtudeProject)
admin.site.register(ThermalChamber, ThermalChamberAdmin)
admin.site.register(Suptech, SuptechAdmin)
admin.site.register(SuptechCategory, SuptechCategoryAdmin)
admin.site.register(SuptechItem, SuptechItemAdmin)
admin.site.register(SuptechMessage, SuptechMessageAdmin)
admin.site.register(SuptechFile, SuptechFileAdmin)
admin.site.register(BgaTime)
admin.site.register(ThermalChamberMeasure, ThermalChamberMeasureAdmin)
admin.site.register(ConfigFile)
