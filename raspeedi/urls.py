from django.urls import path

from . import views

app_name = 'raspeedi'

urlpatterns = [
    path('table/', views.table, name='table'),
    path('insert/', views.insert, name='insert'),
    path('unlock/', views.unlock_prods, name='unlock_prods'),
    path('unlock/table/', views.unlock_table, name='unlock_table'),
    path('unlock/<int:pk>/delete/', views.UnlockProductDeleteView.as_view(), name='unlock_delete'),
    path('<int:ref_case>/edit/', views.edit, name='edit'),
    path('<int:ref_case>/detail/', views.detail, name="detail"),
]
