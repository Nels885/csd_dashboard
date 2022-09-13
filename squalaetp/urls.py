from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/xelon', views.XelonViewSet, basename='api_xelon')
router.register(r'api/temporary', views.TemporaryViewSet, basename='api_temporary')
router.register(r'api/sivin', views.SivinViewSet, basename='api_sivin')
router.register(r'api/sparepart', views.StockViewSet, basename='api_stock')

app_name = 'squalaetp'

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/detail/', views.detail, name='detail'),
    path('<int:pk>/close/', views.XelonCloseView.as_view(), name="xelon_close"),
    path('<int:pk>/pdf/', views.barcode_pdf_generate, name='barcode_pdf'),
    path('<int:pk>/vin/edit/', views.VinCorvetUpdateView.as_view(), name='vin_edit'),
    path('<int:pk>/vin/email/', views.VinEmailFormView.as_view(), name='vin_email'),
    path('<int:pk>/prod/edit/', views.ProductUpdateView.as_view(), name='prod_edit'),
    path('<int:pk>/prod/email/', views.ProdEmailFormView.as_view(), name='prod_email'),
    path('<int:pk>/prog/active/', views.prog_activate, name='prog_activate'),
    path('<int:pk>/adm/email/', views.AdmEmailFormView.as_view(), name='adm_email'),
    path('generate/', views.generate, name='generate'),
    path('excel/import/async/', views.excel_import_async, name='excel_import_async'),
    path('xelon/', views.xelon_table, name='xelon'),
    path('temporary/', views.temporary_table, name='temporary'),
    path('stock-parts/', views.stock_table, name='stock_parts'),
    path('log/<int:pk>/detail/', views.LogFileView.as_view(), name='log_detail'),
    path('change/', views.change_table, name='change_table'),
    path('sivin/', views.sivin_table, name='sivin_table'),
    path('sivin/<slug:immat>/detail/', views.sivin_detail, name='sivin_detail'),
    path('sivin/create/', views.SivinCreateView.as_view(), name='sivin_create'),
]
