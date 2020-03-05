from django.urls import path

from . import views

app_name = 'reman'

urlpatterns = [
    path('repair/table/', views.repair_table, name='repair_table'),
    path('repair/add/', views.new_folder, name='new_folder'),
    path('part/table/', views.part_table, name='part_table'),
    path('batch/create/', views.BatchCreateView.as_view(), name='create_batch'),
]
