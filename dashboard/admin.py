from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import UserProfile, Post

admin.site.register(Permission)
admin.site.register(UserProfile)
admin.site.register(Post)
