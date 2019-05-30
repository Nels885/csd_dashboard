from django.urls import path

from . import views

app_name = 'raspeedi'

urlpatterns = [
    path('table/', views.table, name='table'),
    path('insert/', views.insert, name='insert'),
]
