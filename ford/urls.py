from django.urls import path

from . import views

app_name = 'ford'

urlpatterns = [
    path('useful-links/', views.useful_links, name='useful_links'),
    path('tools/', views.tools, name='tools'),
]
