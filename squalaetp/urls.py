from django.urls import path

from . import views

app_name = 'squalaetp'

urlpatterns = [
    path('<int:pk>/edit/vin/', views.VinCorvetUpdateView.as_view(), name='vin_edit'),
    path('<int:pk>/edit/prod/', views.ProductUpdateView.as_view(), name='prod_edit'),
    path('<int:pk>/email/vin/', views.VinEmailFormView.as_view(), name='vin_email'),
    path('<int:pk>/email/prod/', views.ProdEmailFormView.as_view(), name='prod_email'),
    path('<int:pk>/prog/active/', views.prog_activate, name='prog_activate'),
    path('<int:pk>/detail/', views.detail, name='detail'),
    path('generate/', views.generate, name='generate'),
    path('xelon/', views.xelon_table, name='xelon'),
    path('stock-parts/', views.stock_table, name='stock_parts'),
    path('log/<int:pk>/detail/', views.LogFileView.as_view(), name='log_detail'),
    path('change/', views.change_table, name='change_table')
]
