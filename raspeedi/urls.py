from django.urls import path

from . import views

app_name = 'raspeedi'

urlpatterns = [
    path('table/', views.raspeedi_table, name='table'),
]
