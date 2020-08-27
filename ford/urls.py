from django.urls import path

from . import views

app_name = 'ford'

urlpatterns = [
    path('userful-links/', views.useful_links, name='userful_links'),
]
