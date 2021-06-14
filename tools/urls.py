from django.urls import path

from . import views

app_name = 'tools'

urlpatterns = [
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
    path('suptech/<int:pk>/update/', views.SuptechResponseView.as_view(), name="suptech_update"),
    path('suptech/item/ajax/', views.suptech_item_ajax, name='suptech_item_ajax'),
    path('bga/time/', views.bga_time, name='bga_time'),
]
