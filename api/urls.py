from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('chart/data/', views.CharData.as_view(), name="api-data"),
]
