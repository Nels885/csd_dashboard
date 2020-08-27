from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import UserProfile, Post, WebLink

admin.site.register(Permission)
admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(WebLink)
