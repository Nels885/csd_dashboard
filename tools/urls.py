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
    path('thermal/<int:pk>/disable/', views.thermal_disable, name="thermal_disable"),
    path('thermal/<int:pk>/delete/', views.ThermalDeleteView.as_view(), name="thermal_delete"),
    path('3d-printer/ultimaker/stream/', views.UltimakerStreamView.as_view(), name="ultimaker_stream")
]
