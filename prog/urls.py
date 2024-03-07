from django.urls import path

from . import views

app_name = 'prog'

urlpatterns = [
    path('table/', views.table, name='table'),
    path('insert/', views.insert, name='insert'),
    path('unlock/', views.unlock_prods, name='unlock_prods'),
    path('unlock/table/', views.unlock_table, name='unlock_table'),
    path('unlock/<int:pk>/delete/', views.UnlockProductDeleteView.as_view(), name='unlock_delete'),
    path('<int:ref_case>/edit/', views.edit, name='edit'),
    path('<int:ref_case>/detail/', views.detail, name="detail"),
    path('tool/info/', views.tool_info, name='tool_info'),
    path('tool/info/it/', views.tool_info_it, name='tool_info_it'),
    path('tool/add/', views.ToolCreateView.as_view(), name='tool_add'),
    path('tool/<int:pk>/edit/', views.ToolUpdateView.as_view(), name='tool_update'),
    path('tool/<int:pk>/delete/', views.ToolDeleteView.as_view(), name='tool_delete'),
    path('tool/info/<int:pk>/ajax/', views.ajax_tool_info, name='ajax_tool_info'),
    path('tool/system/<int:pk>/ajax/', views.ajax_tool_system, name='ajax_tool_system'),
    path('aet/info/', views.aet_info, name='aet_info'),
    path('aet/info/<int:pk>/ajax/', views.ajax_aet_status, name='ajax_aet_status'),
    path('aet/add/', views.AetCreateView.as_view(), name='aet_add'),
    path('aet/<int:pk>/delete_aet/', views.AetDeleteView.as_view(), name='aet_delete'),
    path('aet/<int:pk>/update/', views.AetUpdateView.as_view(), name='aet_update'),
    path('aet/<int:pk>/edit_firmware/', views.MbedFirmwareUpdateView.as_view(), name='firmware_update'),
    path('aet/<int:pk>/delete_firmware/', views.MbedFirmwareDeleteView.as_view(), name='firmware_delete'),
    path('aet/add_software/', views.AetAddSoftwareView.as_view(), name='aet_add_software'),
    path('aet/<int:pk>/send_software/', views.AetSendSoftwareView.as_view(), name='aet_send_software'),
]
