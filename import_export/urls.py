from django.urls import path

from . import views

app_name = 'import_export'

urlpatterns = [
    path('export/csv/corvet/', views.export_corvet_csv, name='export_corvet_csv'),
    path('export/csv/bsi/', views.export_bsi_csv, name='export_bsi_csv'),
    path('export/csv/ecu/', views.export_ecu_csv, name='export_ecu_csv'),
    path('export/csv/com200x/', views.export_com_csv, name='export_com_csv'),
]
