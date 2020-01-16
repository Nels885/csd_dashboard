from django.urls import path

from . import views

app_name = 'tools'

urlpatterns = [
    path('soft/', views.soft_list, name="soft-list"),
    path('soft/add/', views.soft_add, name="soft-add"),
    path('soft/<int:soft_id>/edit/', views.soft_edit, name="soft-edit"),
]
