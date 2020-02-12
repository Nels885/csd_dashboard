from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('charts/', views.charts, name='charts'),
    path('set_language/<str:user_language>/', views.set_language, name="set-lang"),
    path('profile/', views.user_profile, name="user-profile"),
    path('activity_log/', views.activity_log, name="activity-log"),
    path('search/', views.search, name="search"),
    path('config/edit/', views.config_edit, name="config-edit"),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    # re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
    #         name='activate')
]
