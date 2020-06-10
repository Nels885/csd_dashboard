from django.urls import path

from . import views

app_name = 'reman'

urlpatterns = [
    path('repair/table/', views.repair_table, name='repair_table'),
    path('repair/create/', views.RepairCreateView.as_view(), name='create_repair'),
    path('repair/<int:pk>/edit/', views.edit_repair, name='edit_repair'),
    path('repair/out/table/', views.out_table, name='out_table'),
    path('part/table/', views.part_table, name='part_table'),
    path('part/check/', views.check_parts, name='part_check'),
    path('batch/table/', views.batch_table, name='batch_table'),
    path('batch/create/', views.BatchCreateView.as_view(), name='create_batch'),
    path('ecu/table/', views.ecu_ref_table, name='ecu_table'),
]
