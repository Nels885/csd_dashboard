from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from . import ajax

router = DefaultRouter()
router.register(r'api/tagxelon', ajax.TagXelonViewSet, basename='api_tagxelon')
router.register(r'api/raspitime', ajax.RaspiTimeViewSet, basename='api_raspitime')

app_name = 'tools'

urlpatterns = [
    path('', include(router.urls)),
    path('soft/', views.soft_list, name="soft_list"),
    path('soft/add/', views.soft_add, name="soft_add"),
    path('soft/<int:soft_id>/edit/', views.soft_edit, name="soft_edit"),
    path('tag-xelon/', views.tag_xelon_list, name="tag_xelon_list"),
    path('tag-xelon/add/', views.TagXelonCreateView.as_view(), name="tag_xelon_add"),
    path('thermal/', views.thermal_chamber, name="thermal"),
    path('thermal/table/', views.ThermalChamberList.as_view(), name="thermal_list"),
    path('thermal/full/', views.ThermalFullScreenView.as_view(), name="thermal_full"),
    path('thermal/ajax/', ajax.temp_async, name="temp_async"),
    path('thermal/<int:pk>/disable/', views.thermal_disable, name="thermal_disable"),
    path('thermal/<int:pk>/delete/', views.ThermalDeleteView.as_view(), name="thermal_delete"),
    path('3d-printer/ultimaker/stream/', views.UltimakerStreamView.as_view(), name="ultimaker_stream"),
    path('suptech/', views.suptech_list, name='suptech_list'),
    path('suptech/add/', views.SupTechCreateView.as_view(), name="suptech_add"),
    path('suptech/<int:pk>/detail/', views.SuptechDetailView.as_view(), name="suptech_detail"),
    path('suptech/<int:pk>/update/', views.SuptechResponseView.as_view(), name="suptech_update"),
    path('suptech/mailing/ajax/', ajax.suptech_mailing_async, name='suptech_mailing_async'),
    path('infotech/', views.infotech_list, name='infotech_list'),
    path('infotech/add/', views.InfotechCreateView.as_view(), name="infotech_add"),
    path('infotech/<int:pk>/detail/', views.InfotechDetailView.as_view(), name="infotech_detail"),
    path('infotech/<int:pk>/update/', views.InfotechActionView.as_view(), name="infotech_update"),
    path('infotech/mailing/ajax/', ajax.infotech_mailing_async, name='infotech_mailing_async'),
    path('bga/time/', ajax.bga_time_async, name='bga_time'),
    path('raspi/time/table/', views.raspi_time_list, name="raspi_time_list"),
    path('usb-devices/', views.usb_devices, name='usb_devices'),
    path('serial-devices/', views.serial_devices, name='serial_devices'),
    path('config-files/', views.config_files, name='config_files'),
    path('config-files/add/', views.ConfigFileCreateView.as_view(), name='config_add'),
    path('config-files/<int:pk>/edit/', views.config_files, name='config_edit')
]
