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
    path('tool/add/', views.ToolCreateView.as_view(), name='tool_add'),
    path('tool/<int:pk>/edit/', views.ToolUpdateView.as_view(), name='tool_update'),
    path('tool/info/<int:pk>/ajax/', views.ajax_tool_info, name='ajax_tool_info'),
]
