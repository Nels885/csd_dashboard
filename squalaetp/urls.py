from django.urls import path

from . import views

app_name = 'squalaetp'

urlpatterns = [
    path('xelon/', views.xelon_table, name='xelon'),
    path('xelon/<int:file_id>/edit/', views.xelon_edit, name='xelon_edit'),
    path('stock-parts/', views.stock_table, name='stock_parts'),
    path('corvet/<int:pk>/edit/', views.SqualaetpUpdateView.as_view(), name='corvet_edit'),
    path('<int:file_id>/detail/', views.detail, name='detail'),
    path('log/<str:file>/detail/', views.LogFileView.as_view(), name='log_detail'),
    path('ajax/xelon/', views.ajax_xelon, name='ajax_xelon'),
]
