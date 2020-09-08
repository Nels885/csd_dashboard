from django.urls import path

from . import views

app_name = 'renault'

urlpatterns = [
    path('useful-links/', views.useful_links, name='useful_links'),
]
