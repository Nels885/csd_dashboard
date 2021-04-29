from django.urls import path

from . import views

app_name = 'import_export'

urlpatterns = [
    path('detail/', views.import_export, name='detail'),
    path('export/reman/', views.export_reman, name='reman'),
    path('export/tools/', views.export_tools, name='tools'),
    path('import/part/', views.import_sparepart, name='import_part'),
    path('import/ecu-base/', views.import_ecurefbase, name='import_ecu_base'),
    path('export/corvet/async/', views.export_corvet_async, name='export_corvet'),
    path('export/corvet-vin/async/', views.export_corvet_vin_async, name="export_corvet_vin")
]
