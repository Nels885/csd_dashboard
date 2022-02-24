from django.urls import path

from . import views

app_name = 'import_export'

urlpatterns = [
    path('export/csd/async/', views.export_csd_async, name='csd_async'),
    path('export/reman/async/', views.export_reman_async, name="reman_async"),
    path('export/tools/async/', views.export_tools_async, name="tools_async"),
    path('import/part/', views.import_sparepart, name='import_part'),
    path('import/ecu-base/', views.import_ecurefbase, name='import_ecu_base'),
    path('import/corvet-vin/async/', views.import_corvet_vin_async, name="import_corvet_vin"),
]
