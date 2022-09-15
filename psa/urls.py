from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/corvet', views.CorvetViewSet, basename='api_corvet')

app_name = 'psa'

urlpatterns = [
    path('', include(router.urls)),
    path('nac/tools/', views.nac_tools, name='nac_tools'),
    path('nac/tools/license/', views.nac_license, name='nac_license'),
    path('nac/tools/update-id/license/', views.nac_update_id_license, name='nac_id_license'),
    path('nac/tools/update/', views.nac_update, name='nac_update'),
    path('useful-links/', views.useful_links, name='useful_links'),
    path('corvet/', views.CorvetView.as_view(), name='corvet'),
    path('corvet/create/', views.CorvetCreateView.as_view(), name='create_corvet'),
    path('corvet/<slug:pk>/edit/', views.CorvetUpdateView.as_view(), name='update_corvet'),
    path('corvet/<slug:pk>/detail/', views.corvet_detail, name='corvet_detail'),
    path('corvet/import/async/', views.import_corvet_async, name='import_corvet'),
    path('product/', views.product_table, name='product'),
    path('majestic-web/', views.majestic_web, name='majestic_web')
]
