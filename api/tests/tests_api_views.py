from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class ApiTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(username='toto', password='totopassword')
        admin = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@test.com')
        self.authError = {"detail": "Informations d'authentification non fournies."}
        self.token = Token.objects.get(user=admin)

    def login(self, user='user'):
        if user == 'admin':
            self.client.login(username='admin', password='adminpassword')
        else:
            self.client.login(username='toto', password='totopassword')

    def test_prog_list(self):
        response = self.client.get(reverse('api:prog-list'), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, self.authError)

        # Identification with Token
        response = self.client.get('/api/prog/?auth_token={}'.format(self.token), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})

    def test_cal_list(self):
        response = self.client.get(reverse('api:cal-list'), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, self.authError)

        # Identification with Token
        response = self.client.get('/api/cal/?auth_token={}'.format(self.token), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})

    def test_thermal_chamber_measure_list(self):
        url = reverse('api:tools_tc_measure-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, self.authError)

        # Identification with Token
        response = self.client.get(url + '?auth_token={}'.format(self.token), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})
