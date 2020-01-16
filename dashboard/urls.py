from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('set_language/<str:user_language>/', views.set_language, name="set-lang"),
    path('profile/', views.user_profile, name="user-profile"),
    path('activity_log/', views.activity_log, name="activity-log"),
    path('search/', views.search, name="search"),
    path('config/edit/', views.config_edit, name="config-edit"),
    path('register/', views.register, name='register'),
]
