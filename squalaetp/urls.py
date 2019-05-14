from django.urls import path

from . import views

app_name = 'squalaetp'

urlpatterns = [
    path('table/', views.table, name='table'),
]
