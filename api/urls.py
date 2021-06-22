from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from api import views

router = DefaultRouter()
router.register(r'prog', views.ProgViewSet, basename='prog')
router.register(r'cal', views.CalViewSet, basename='cal')
router.register(r'unlock', views.UnlockViewSet, basename='unlock')
router.register(r'reman/batch', views.RemanBatchViewSet, basename='reman_batch')
router.register(r'reman/checkout', views.RemanCheckOutViewSet, basename='reman_checkout')
router.register(r'reman/repair', views.RemanRepairViewSet, basename='reman_repair')
router.register(r'reman/ecurefbase', views.RemanEcuRefBaseViewSet, basename='reman_ecurefbase')
router.register(r'tools/tc-measure', views.ThermalChamberMeasureViewSet, basename='tools_tc_measure')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='token_auth'),
    path('doc/', views.documentation, name='doc'),
    path('nac-license/', views.NacLicenseView.as_view(), name='nac_license')
]
