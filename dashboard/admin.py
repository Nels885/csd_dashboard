from django.contrib import admin

from .models import UserProfile, Post, CsdSoftware

admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(CsdSoftware)
