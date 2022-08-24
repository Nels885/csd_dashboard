from django.contrib import admin
from django.template.defaultfilters import pluralize
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, User
from django.contrib.auth.admin import UserAdmin

from .models import UserProfile, Post, WebLink, ShowCollapse, Contract
from .forms import UserProfileAdminForm


class UserProfileAdmin(admin.StackedInline):
    model = UserProfile
    form = UserProfileAdminForm


class ShowCollapseAdmin(admin.ModelAdmin):
    list_display = ('user', 'general', 'motor', 'axle', 'body', 'interior', 'electric', 'diverse')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileAdmin,)
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'last_login', 'get_job_title', 'get_service', 'is_staff',
        'is_active'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__job_title', 'profile__service')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__job_title', 'profile__service')
    actions = (
        'ce_service_update', 'co_service_update', 'adm_service_update', 'technician_job_title_update',
        'operator_job_title_update', 'animator_job_title_update', 'manager_job_title_update'
    )

    @admin.display(description='Job Title', ordering='profile__job_title')
    def get_job_title(self, obj):
        return obj.profile.job_title

    @admin.display(description='Service', ordering='profile__service')
    def get_service(self, obj):
        return obj.profile.service

    def _message_user_about_update(self, request, rows_updated, verb):
        """Send message about action to user.
        `verb` should shortly describe what have changed (e.g. 'enabled').
        """
        self.message_user(
            request,
            _('{0} user{1} {2} successfully {3}').format(
                rows_updated,
                pluralize(rows_updated),
                pluralize(rows_updated, _('was,were')),
                verb,
            ),
        )

    @admin.action(description=_('Change service for CE'))
    def ce_service_update(self, request, queryset):
        for query in queryset:
            query.profile.service = "CE"
            query.profile.save()
        self._message_user_about_update(request, queryset.count(), 'CE')

    @admin.action(description=_('Change service for CO'))
    def co_service_update(self, request, queryset):
        for query in queryset:
            query.profile.service = "CO"
            query.profile.save()
        self._message_user_about_update(request, queryset.count(), 'CO')

    @admin.action(description=_('Change service for ADM'))
    def adm_service_update(self, request, queryset):
        for query in queryset:
            query.profile.service = "ADM"
            query.profile.save()
        self._message_user_about_update(request, queryset.count(), 'ADM')

    @admin.action(description=_('Change job title for technician'))
    def technician_job_title_update(self, request, queryset):
        for query in queryset:
            query.profile.job_title = "technician"
            query.profile.save()
        self._message_user_about_update(request, queryset.count(), 'Technician')

    @admin.action(description=_('Change job title for operator'))
    def operator_job_title_update(self, request, queryset):
        for query in queryset:
            query.profile.job_title = "operator"
            query.profile.save()
        self._message_user_about_update(request, queryset.count(), 'Operator')

    @admin.action(description=_('Change job title for animator'))
    def animator_job_title_update(self, request, queryset):
        for query in queryset:
            query.profile.job_title = "animator"
            query.profile.save()
        self._message_user_about_update(request, queryset.count(), 'Animator')

    @admin.action(description=_('Change job title for manager'))
    def manager_job_title_update(self, request, queryset):
        for query in queryset:
            query.profile.job_title = "manager"
            query.profile.save()
        self._message_user_about_update(request, queryset.count(), 'Manager')


class ContractAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'code', 'service', 'nature', 'object', 'supplier', 'site', 'end_date', 'is_active', 'renew_date')
    search_fields = ('code', 'service', 'nature', 'object', 'supplier', 'site', 'end_date', 'renew_date')
    list_filter = ('is_active',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Permission)
admin.site.register(Post)
admin.site.register(WebLink)
admin.site.register(ShowCollapse, ShowCollapseAdmin)
admin.site.register(Contract, ContractAdmin)
