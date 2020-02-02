from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User


class ApiTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(username='toto', password='totopassword')
        User.objects.create_superuser(username='admin', password='adminpassword', email='admin@test.com')
        self.authError = {"detail": "Informations d'authentification non fournies."}

    def test_user_view_set_is_disconnected(self):
        response = self.client.get(reverse('api:user-list'), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.authError)

    def test_user_view_set_is_connected(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('api:user-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

    def test_group_view_set_is_disconnected(self):
        response = self.client.get(reverse('api:group-list'), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.authError)

    def test_group_view_set_is_connected(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('api:group-list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)

    def test_prog_list_is_disconnected(self):
        response = self.client.get(reverse('api:prog'), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.authError)

    def test_prog_list_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('api:prog'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})

    def test_cal_list_is_disconnected(self):
        response = self.client.get(reverse('api:cal'), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.authError)

    def test_cal_list_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('api:cal'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})

    def test_charts_is_valid(self):
        response = self.client.get(reverse('api:charts'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
