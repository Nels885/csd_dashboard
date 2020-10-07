from django.urls import path

from . import views

app_name = 'import_export'

urlpatterns = [
    path('detail/', views.import_export, name='detail'),
    path('export/corvet/', views.export_corvet, name='corvet'),
    path('export/reman/', views.export_reman, name='reman'),
    path('import/part/', views.import_sparepart, name='import_part'),
    path('import/ecu/', views.import_ecureference, name='import_ecu'),
    path('import/ecu-base/', views.import_ecurefbase, name='import_ecu_base'),
]
