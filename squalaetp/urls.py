from django.urls import path

from . import views

app_name = 'squalaetp'

urlpatterns = [
    path('xelon/', views.xelon_table, name='xelon'),
    path('xelon/barcode/', views.barcode, name="barcode"),
    path('xelon/<int:file_id>/edit/', views.xelon_edit, name='xelon-edit'),
    path('xelon/<int:file_id>/detail/', views.xelon_detail, name='xelon-detail'),
    path('corvet/', views.corvet_table, name='corvet'),
    path('corvet/insert/', views.corvet_insert, name='corvet-insert'),
    path('corvet/<str:vin>/detail/', views.corvet_detail, name='corvet-detail'),
]
