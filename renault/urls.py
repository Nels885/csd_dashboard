from django.urls import path

from . import views

app_name = 'renault'

urlpatterns = [
    path('useful-links/', views.useful_links, name='useful_links'),
    path('tools/', views.tools, name="tools"),
    path('decode/ajax/', views.ajax_decode, name="ajax_decode"),
]
