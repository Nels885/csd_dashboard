from django.urls import path

from . import views

app_name = 'reman'

urlpatterns = [
    path('add/', views.new_folder, name='new-folder'),
]
