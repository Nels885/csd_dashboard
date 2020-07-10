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
    path('part/<str:psa_barcode>/email/', views.new_part_email, name='part_email'),
    path('batch/table/', views.batch_table, name='batch_table'),
    path('batch/create/', views.BatchCreateView.as_view(), name='create_batch'),
    path('ecu/table/', views.ecu_ref_table, name='ecu_table'),
    path('ecu/<str:psa_barcode>/model/create/', views.ecu_model_create, name='create_ecu_model'),
    path('ecu/<str:hw_reference>/type/create/', views.ecu_type_create, name='create_ecu_type'),
    path('default/create/', views.DefaultCreateView.as_view(), name='create_default'),
    path('default/<int:pk>/edit/', views.DefaultUpdateView.as_view(), name='update_default'),
    path('default/table/', views.default_table, name='default_table'),
]
