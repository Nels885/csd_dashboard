from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'xelon', views.XelonViewSet)
router.register(r'corvet', views.CorvetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chart/data/', views.CharData.as_view(), name="api-data"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
