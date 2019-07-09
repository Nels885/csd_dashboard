from django.urls import path

from . import views

app_name = 'raspeedi'

urlpatterns = [
    path('table/', views.table, name='table'),
    path('insert/', views.insert, name='insert'),
    path('<int:ref_case>/edit/', views.edit, name='edit'),
    path('<int:ref_case>/detail/', views.detail, name="detail"),
]
