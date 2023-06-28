from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'api/tagxelon', views.TagXelonViewSet, basename='api_tagxelon')

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
    path('thermal/ajax/', views.ajax_temp, name="ajax_temp"),
    path('thermal/<int:pk>/disable/', views.thermal_disable, name="thermal_disable"),
    path('thermal/<int:pk>/delete/', views.ThermalDeleteView.as_view(), name="thermal_delete"),
    path('3d-printer/ultimaker/stream/', views.UltimakerStreamView.as_view(), name="ultimaker_stream"),
    path('suptech/', views.suptech_list, name='suptech_list'),
    path('suptech/add/', views.SupTechCreateView.as_view(), name="suptech_add"),
    path('suptech/<int:pk>/detail/', views.SuptechDetailView.as_view(), name="suptech_detail"),
    path('suptech/<int:pk>/update/', views.SuptechResponseView.as_view(), name="suptech_update"),
    path('suptech/item/ajax/', views.suptech_item_ajax, name='suptech_item_ajax'),
    path('infotech/', views.infotech_list, name='infotech_list'),
    path('infotech/add/', views.InfotechCreateView.as_view(), name="infotech_add"),
    path('infotech/<int:pk>/detail/', views.InfotechDetailView.as_view(), name="infotech_detail"),
    path('infotech/<int:pk>/update/', views.InfotechActionView.as_view(), name="infotech_update"),
    path('infotech/mailing/ajax/', views.infotech_mailing_ajax, name='infotech_mailing_ajax'),
    path('bga/time/', views.bga_time, name='bga_time'),
    path('usb-devices/', views.usb_devices, name='usb_devices'),
    path('config-files/', views.config_files, name='config_files'),
    path('config-files/add/', views.ConfigFileCreateView.as_view(), name='config_add'),
    path('config-files/<int:pk>/edit/', views.config_files, name='config_edit')
]
