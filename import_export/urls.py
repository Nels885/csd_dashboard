from django.urls import path

from . import views

app_name = 'import_export'

urlpatterns = [
    path('export/corvet/', views.export_corvet, name='corvet'),
    path('export/reman/', views.export_reman, name='reman'),
    path('export/csv/corvet/', views.export_corvet_csv, name='export_corvet_csv'),
    path('export/csv/bsi/', views.export_bsi_csv, name='export_bsi_csv'),
    path('export/csv/ecu/', views.export_ecu_csv, name='export_ecu_csv'),
    path('export/csv/com200x/', views.export_com_csv, name='export_com_csv'),
    path('export/csv/bsm/', views.export_bsm_csv, name='export_bsm_csv'),
    path('export/csv/batch/', views.export_batch_csv, name='export_batch_csv'),
    path('export/csv/repair/', views.export_repair_csv, name='export_repair_csv'),
    path('import/part/', views.import_sparepart, name='import_part'),
    path('import/ecu/', views.import_ecureference, name='import_ecu'),
]
