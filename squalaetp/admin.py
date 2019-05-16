from django.contrib import admin

# Register your models here.

from .models import Xelon, CorvetBackup

admin.site.register(Xelon)
admin.site.register(CorvetBackup)
