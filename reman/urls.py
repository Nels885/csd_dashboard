from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import repair, batch

router = DefaultRouter()
router.register(r'api/repair', repair.RepairViewSet, basename='api_repair')

app_name = 'reman'

urlpatterns = [
    path('', include(router.urls)),
    path('repair/table/', repair.repair_table, name='repair_table'),
    path('repair/create/', repair.RepairCreateView.as_view(), name='create_repair'),
    path('repair/select/', repair.RepairSelectView.as_view(), name='select_repair'),
    path('repair/<int:pk>/edit/', repair.repair_edit, name='edit_repair'),
    path('repair/<int:pk>/close/', repair.repair_close, name='close_repair'),
    path('repair/<int:pk>/detail/', repair.repair_detail, name='detail_repair'),
    path('repair-part/<int:pk>/create/ajax/', repair.ajax_repair_part_create, name='create_part_ajax'),
    path('repair-part/<int:pk>/delete/ajax/', repair.ajax_repair_part_delete, name='delete_part_ajax'),
    path('repair-part/<int:pk>/list/ajax/', repair.ajax_repair_part_list, name='part_list_ajax'),
    path('out/filter/', views.CheckOutFilterView.as_view(), name='out_filter'),
    path('out/table/', views.out_table, name='out_table'),
    path('part/table/', views.part_table, name='part_table'),
    path('part/check/', views.check_parts, name='part_check'),
    path('part/<str:barcode>/create/', views.create_part, name='part_create'),
    path('part/<str:barcode>/email/', views.new_part_email, name='part_email'),
    path('batch/table/', batch.batch_table, name='batch_table'),
    path('batch/create/', batch.BatchCreateView.as_view(), name='create_batch'),
    path('batch/<int:pk>/pdf/', batch.batch_pdf_generate, name='batch_pdf'),
    path('batch/<int:pk>/update/', batch.BatchUpdateView.as_view(), name='update_batch'),
    path('batch/<int:pk>/delete/', batch.BatchDeleteView.as_view(), name='delete_batch'),
    path('batch/type/ajax/', batch.batch_type_ajax, name='batch_type_ajax'),
    path('base-ref/table/', views.base_ref_table, name='base_ref_table'),
    path('base-ref/create/', views.RefRemanCreateView.as_view(), name='ref_reman_create'),
    path('base-ref/<int:pk>/update/', views.RefRemanUpdateView.as_view(), name='ref_reman_update'),
    path('base-ref/<str:barcode>/edit/', views.ref_base_edit, name='edit_ref_base'),
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
