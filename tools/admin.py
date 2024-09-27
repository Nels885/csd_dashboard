from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from utils.django.contrib import CustomModelAdmin

from .models import (
    TagXelon, CsdSoftware, EtudeProject, ThermalChamber, ThermalChamberMeasure, Suptech, SuptechCategory, SuptechItem,
    Message, SuptechFile, BgaTime, RaspiTime, ConfigFile, Infotech, InfotechMailingList
)

ACTIVE_USERS = User.objects.filter(is_active=True).order_by('first_name')


class UserMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Custom multiple select Field with full name + username
    """
    def label_from_instance(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name} ({obj.username})"
        return obj.username


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


class SuptechAdmin(CustomModelAdmin):
    list_display = (
        'id', 'date', 'delta', 'days_late', 'user', 'modified_by', 'status', 'xelon', 'product', 'item', 'category',
        'is_48h', 'action')
    ordering = ('-date',)
    list_filter = ('status', 'category', 'is_48h')
    search_fields = ('id', 'user', 'xelon', 'product', 'item')
    actions = ('is_48h_disabled', 'is_48h_enabled')
    inlines = (SuptechFileline, )

    def is_48h_disabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=False)
        self._message_product_about_update(request, rows_updated, 'disabled')
    is_48h_disabled.short_description = _('48h processing disabled')

    def is_48h_enabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=True)
        self._message_product_about_update(request, rows_updated, 'enabled')
    is_48h_enabled.short_description = _('48h processing enabled')

    @admin.display(description="Delta")
    def delta(self, obj):
        try:
            if obj.modified_at:
                return (obj.modified_at.date() - obj.date).days
            return (timezone.now().date() - obj.date).days
        except Exception:
            return ""


class SuptechItemAdminForm(forms.ModelForm):
    to_users = UserMultipleChoiceField(
        queryset=ACTIVE_USERS, widget=FilteredSelectMultiple("User", is_stacked=False), required=False)
    cc_users = UserMultipleChoiceField(
        queryset=ACTIVE_USERS, widget=FilteredSelectMultiple("User", is_stacked=False), required=False)

    class Meta:
        model = SuptechItem
        fields = '__all__'


class SuptechItemAdmin(CustomModelAdmin):
    form = SuptechItemAdminForm
    list_display = ('name', 'extra', 'category', 'is_48h', 'is_active', 'to_list', 'cc_list')
    ordering = ('name',)
    list_filter = ('category', 'is_48h', 'is_active')
    search_fields = ('name', 'mailing_list', 'cc_mailing_list', 'to_users__email', 'cc_users__email')
    actions = ('is_48h_disabled', 'is_48h_enabled', 'is_disabled', 'is_activated')

    def is_48h_disabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=False)
        self._message_item_about_update(request, rows_updated, 'disabled')
    is_48h_disabled.short_description = _('48h processing disabled')

    def is_48h_enabled(self, request, queryset):
        rows_updated = queryset.update(is_48h=True)
        self._message_item_about_update(request, rows_updated, 'enabled')
    is_48h_enabled.short_description = _('48h processing enabled')

    def is_disabled(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self._message_item_about_update(request, rows_updated, 'disabled')
    is_disabled.short_description = _('Item disabled')

    def is_activated(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self._message_item_about_update(request, rows_updated, 'activated')
    is_activated.short_description = _('Item activated')

    @staticmethod
    def to_list(obj):
        """Special method for looking up and returning the user's registration key
        """
        return obj.to_list()

    @staticmethod
    def cc_list(obj):
        """Special method for looking up and returning the user's registration key
        """
        return obj.cc_list()


class SuptechCategoryAdminForm(forms.ModelForm):
    to_users = UserMultipleChoiceField(
        queryset=ACTIVE_USERS, widget=FilteredSelectMultiple("User", is_stacked=False), required=False)
    cc_users = UserMultipleChoiceField(
        queryset=ACTIVE_USERS, widget=FilteredSelectMultiple("User", is_stacked=False), required=False)

    class Meta:
        model = SuptechCategory
        fields = '__all__'


class SuptechCategoryAdmin(admin.ModelAdmin):
    form = SuptechCategoryAdminForm
    list_display = ('name', 'manager')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'added_at', 'added_by', 'content_object')


class SuptechFileAdmin(admin.ModelAdmin):
    list_display = ('suptech', 'file')
    ordering = ('suptech',)


class InfotechMailingListAdminForm(forms.ModelForm):
    to_users = UserMultipleChoiceField(
        queryset=ACTIVE_USERS, widget=FilteredSelectMultiple("User", is_stacked=False), required=False)
    cc_users = UserMultipleChoiceField(
        queryset=ACTIVE_USERS, widget=FilteredSelectMultiple("User", is_stacked=False), required=False)

    class Meta:
        model = InfotechMailingList
        fields = '__all__'


class InfotechAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'info', 'created_by', 'created_at', 'status')
    ordering = ('id',)
    list_filter = ('status',)
    search_fields = ('id', 'created_by', 'item')


class InfotechMailingListAdmin(CustomModelAdmin):
    form = InfotechMailingListAdminForm
    list_display = ('name', 'is_active', 'to_list', 'cc_list')
    ordering = ('name',)
    list_filter = ('is_active',)
    search_fields = ('name',)
    actions = ('is_disabled', 'is_activated')

    def is_disabled(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        self._message_item_about_update(request, rows_updated, 'disabled')
    is_disabled.short_description = _('Item disabled')

    def is_activated(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        self._message_item_about_update(request, rows_updated, 'activated')
    is_activated.short_description = _('Item activated')

    @staticmethod
    def to_list(obj):
        """Special method for looking up and returning the user's registration key
        """
        return obj.to_list()

    @staticmethod
    def cc_list(obj):
        """Special method for looking up and returning the user's registration key
        """
        return obj.cc_list()


class BGATimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date', 'start_time', 'end_time', 'duration')
    ordering = ('id',)
    list_filter = ('name',)
    search_fields = ('name', 'date')


class RaspiTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'date', 'start_time', 'end_time', 'duration', 'xelon')
    ordering = ('-id',)
    list_filter = ('name', 'type')
    search_fields = ('name', 'type', 'date', 'xelon')


admin.site.register(TagXelon, TagXelonAdmin)
admin.site.register(CsdSoftware)
admin.site.register(EtudeProject)
admin.site.register(ThermalChamber, ThermalChamberAdmin)
admin.site.register(Suptech, SuptechAdmin)
admin.site.register(SuptechCategory, SuptechCategoryAdmin)
admin.site.register(SuptechItem, SuptechItemAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(SuptechFile, SuptechFileAdmin)
admin.site.register(BgaTime, BGATimeAdmin)
admin.site.register(RaspiTime, RaspiTimeAdmin)
admin.site.register(ThermalChamberMeasure, ThermalChamberMeasureAdmin)
admin.site.register(ConfigFile)
admin.site.register(Infotech, InfotechAdmin)
admin.site.register(InfotechMailingList, InfotechMailingListAdmin)
