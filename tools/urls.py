from django.urls import path

from . import views

app_name = 'tools'

urlpatterns = [
    path('soft/', views.soft_list, name="soft_list"),
    path('soft/add/', views.soft_add, name="soft_add"),
    path('soft/<int:soft_id>/edit/', views.soft_edit, name="soft_edit"),
    path('tag-xelon/', views.TagXelonView.as_view(), name="tag_xelon"),
    path('thermal/', views.thermal_chamber, name="thermal"),
    path('thermal/<int:pk>/disable/', views.thermal_disable, name="thermal_disable")
]
