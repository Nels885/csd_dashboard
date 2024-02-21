from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import ajax

router = DefaultRouter()
router.register(r'api/corvet', ajax.CorvetViewSet, basename='api_corvet')
router.register(r'api/dtc', ajax.DTCServerSodeViewSet, basename='api_dtc')

app_name = 'psa'

urlpatterns = [
    path('', include(router.urls)),
    path('nac/tools/', views.nac_tools, name='nac_tools'),
    path('nac/tools/license/', views.nac_license, name='nac_license'),
    path('nac/tools/update-id/license/', views.nac_update_id_license, name='nac_id_license'),
    path('nac/tools/update/', views.nac_update, name='nac_update'),
    path('can/tools/', views.can_tools, name='can_tools'),
    path('can/tools/vehicle/async/', ajax.canremote_async, name='ajax_remote'),
    path('useful-links/', views.useful_links, name='useful_links'),
    path('corvet/', views.CorvetView.as_view(), name='corvet'),
    path('corvet/create/', views.CorvetCreateView.as_view(), name='create_corvet'),
    path('corvet/<slug:pk>/edit/', views.CorvetUpdateView.as_view(), name='update_corvet'),
    path('corvet/<slug:pk>/detail/', views.corvet_detail, name='corvet_detail'),
    path('corvet/<slug:pk>/pdf/', views.barcode_pdf_generate, name='barcode_pdf'),
    path('corvet/import/async/', ajax.import_corvet_async, name='import_corvet'),
    path('product/', views.product_table, name='product'),
    path('dtc/', views.dtc_table, name='dtc_table'),
    path('majestic-web/', views.majestic_web, name='majestic_web')
]
