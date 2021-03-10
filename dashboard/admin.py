from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import UserProfile, Post, WebLink, ShowCollapse


class ShowCollapseAdmin(admin.ModelAdmin):
    list_display = ('user', 'general', 'motor', 'interior', 'diverse')
    search_fields = ('user',)


admin.site.register(Permission)
admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(WebLink)
admin.site.register(ShowCollapse, ShowCollapseAdmin)
