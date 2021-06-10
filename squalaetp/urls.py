from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/xelon', views.XelonViewSet, basename='api_xelon')

app_name = 'squalaetp'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/detail/', views.detail, name='detail'),
    path('<int:pk>/vin/edit/', views.VinCorvetUpdateView.as_view(), name='vin_edit'),
    path('<int:pk>/vin/email/', views.VinEmailFormView.as_view(), name='vin_email'),
    path('<int:pk>/prod/edit/', views.ProductUpdateView.as_view(), name='prod_edit'),
    path('<int:pk>/prod/email/', views.ProdEmailFormView.as_view(), name='prod_email'),
    path('<int:pk>/prog/active/', views.prog_activate, name='prog_activate'),
    path('generate/', views.generate, name='generate'),
    path('excel/import/async/', views.excel_import_async, name='excel_import_async'),
    path('xelon/', views.xelon_table, name='xelon'),
    path('stock-parts/', views.stock_table, name='stock_parts'),
    path('log/<int:pk>/detail/', views.LogFileView.as_view(), name='log_detail'),
    path('change/', views.change_table, name='change_table')
]
