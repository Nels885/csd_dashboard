from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/repair', views.RepairViewSet, basename='api_repair')

app_name = 'reman'

urlpatterns = [
    path('', include(router.urls)),
    path('repair/table/', views.repair_table, name='repair_table'),
    path('repair/create/', views.RepairCreateView.as_view(), name='create_repair'),
    path('repair/<int:pk>/edit/', views.repair_edit, name='edit_repair'),
    path('repair/<int:pk>/close/', views.repair_close, name='close_repair'),
    path('repair/<int:pk>/detail/', views.repair_detail, name='detail_repair'),
    path('out/filter/', views.CheckOutFilterView.as_view(), name='out_filter'),
    path('out/table/', views.out_table, name='out_table'),
    path('part/table/', views.part_table, name='part_table'),
    path('part/check/', views.check_parts, name='part_check'),
    path('part/<str:psa_barcode>/email/', views.new_part_email, name='part_email'),
    path('batch/table/', views.batch_table, name='batch_table'),
    path('batch/create/', views.BatchCreateView.as_view(), name='create_batch'),
    path('batch/etude/create/', views.BatchEtudeCreateView.as_view(), name='create_etude_batch'),
    path('batch/<int:pk>/update/', views.BatchUpdateView.as_view(), name='update_batch'),
    path('batch/<int:pk>/delete/', views.BatchDeleteView.as_view(), name='delete_batch'),
    path('base-ref/table/', views.base_ref_table, name='base_ref_table'),
    path('base-ref/create/', views.RefRemanCreateView.as_view(), name='ref_reman_create'),
    path('base-ref/<str:psa_barcode>/create/', views.ref_base_create, name='create_ref_base'),
    path('base-ref/<str:psa_barcode>/edit/', views.ref_base_edit, name='edit_ref_base'),
    path('ecu/hw/table/', views.ecu_hw_table, name='ecu_hw_table'),
    path('ecu/hw/generate/', views.ecu_hw_generate, name='ecu_hw_generate'),
    path('ecu/hw/create/', views.EcuHwCreateView.as_view(), name='ecu_hw_create'),
    path('ecu/hw/<int:pk>/update/', views.EcuHwUpdateView.as_view(), name='ecu_hw_update'),
    path('ecu/dump/table/', views.ecu_dump_table, name='ecu_dump_table'),
    path('ecu/dump/<int:pk>/update/', views.EcuDumpUpdateView.as_view(), name='update_ecu_dump'),
    path('default/create/', views.DefaultCreateView.as_view(), name='create_default'),
    path('default/<int:pk>/edit/', views.DefaultUpdateView.as_view(), name='update_default'),
    path('default/table/', views.default_table, name='default_table'),
]
