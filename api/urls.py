from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from api import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'xelon', views.XelonViewSet)
router.register(r'corvet', views.CorvetViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('chart/', views.CharData.as_view(), name="data"),
    path('prog/', views.ProgList.as_view(), name="prog"),
    path('cal/', views.CalList.as_view(), name="cal"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='token-auth'),
]
