from django.urls import path

from . import views

app_name = 'reman'

urlpatterns = [
    path('/', views.reman_table, name='reman_table'),
    path('add/', views.new_folder, name='new-folder'),
]
