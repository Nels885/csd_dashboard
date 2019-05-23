from django.contrib import admin

# Register your models here.

from .models import Xelon, Corvet, CorvetBackup

admin.site.register(Xelon)
admin.site.register(Corvet)
admin.site.register(CorvetBackup)
