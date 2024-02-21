from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from api import views
from api.views import reman, tools

router = DefaultRouter()
router.register(r'prog', views.ProgViewSet, basename='prog')
router.register(r'cal', views.CalViewSet, basename='cal')
router.register(r'unlock', views.UnlockViewSet, basename='unlock')
router.register(r'dtc', views.DefaultCodeViewSet, basename='dtc')
router.register(r'reman/batch', reman.RemanBatchViewSet, basename='reman_batch')
router.register(r'reman/checkout', reman.RemanCheckOutViewSet, basename='reman_checkout')
router.register(r'reman/repair', reman.RemanRepairViewSet, basename='reman_repair')
router.register(r'reman/ecurefbase', reman.RemanEcuRefBaseViewSet, basename='reman_ecurefbase')
router.register(r'tools/tc-measure', tools.ThermalChamberMeasureViewSet, basename='tools_tc_measure')
router.register(r'tools/bga-time', tools.BgaTimeViewSet, basename='tools_bga_time')
router.register(r'tools/raspi-time', tools.RaspiTimeViewSet, basename='tools_raspi_time')
router.register(r'tools/status', tools.ToolStatusViewSet, basename='tools_status')
router.register(r'tools/log', tools.ToolLogViewSet, basename='tools_log')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='token_auth'),
    path('doc/', views.documentation, name='doc'),
    path('nac-license/', views.NacLicenseView.as_view(), name='nac_license')
]
