from django.contrib import admin

from .models import Batch


class BatchAdmin(admin.ModelAdmin):
    list_display = ('year', 'number', 'quantity', 'created_by', 'created_at', 'active')


admin.site.register(Batch, BatchAdmin)
