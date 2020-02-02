from django.urls import path

from . import views

app_name = 'squalaetp'

urlpatterns = [
    path('xelon/', views.xelon_table, name='xelon'),
    path('xelon/<int:file_id>/edit/', views.xelon_edit, name='xelon-edit'),
    path('corvet/', views.corvet_table, name='corvet'),
    path('corvet/insert/', views.corvet_insert, name='corvet-insert'),
    path('corvet/<str:vin>/detail/', views.corvet_detail, name='corvet-detail'),
    path('corvet/export/csv/', views.export_corvet_csv, name='export-corvet-csv'),
    path('ajax/xelon/', views.ajax_xelon, name='ajax-xelon'),
    path('<int:file_id>/detail/', views.detail, name='detail'),
]
