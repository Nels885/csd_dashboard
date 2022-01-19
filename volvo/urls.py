from django.urls import path
from . import views

app_name = 'volvo'

urlpatterns = [
    path('reman/ref/table/', views.reman_ref_table, name='reman_ref_table'),
    path('reman/ref/create/', views.SemRemanCreateView.as_view(), name='reman_ref_create'),
    path('reman/ref/<int:pk>/update/', views.SemRemanUpdateView.as_view(), name='reman_ref_update'),
    path('reman/hw/table/', views.sem_hw_table, name='sem_hw_table'),
]
