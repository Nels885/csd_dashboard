from django.contrib import admin

from .models import Batch, EcuModel, Repair


class BatchAdmin(admin.ModelAdmin):
    list_display = ('year', 'number', 'quantity', 'created_by', 'created_at', 'active')


admin.site.register(Batch, BatchAdmin)
admin.site.register(EcuModel)
admin.site.register(Repair)
