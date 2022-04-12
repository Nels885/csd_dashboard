from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from reman.models import EcuType, EcuModel, EcuRefBase, Batch, Repair
from squalaetp.models import Xelon
from raspeedi.models import UnlockProduct


class ApiTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='toto', password='totopassword')
        admin = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@test.com')
        self.authError = {"detail": "Informations d'authentification non fournies."}
        self.token = Token.objects.get(user=admin)

    def login(self, user='user'):
        if user == 'admin':
            self.client.login(username='admin', password='adminpassword')
        else:
            self.client.login(username='toto', password='totopassword')

    def api_view_list(self, url):
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, self.authError)

        # Identification with Token
        response = self.client.get(url + f'?auth_token={self.token}', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})

    def test_documentation_view(self):
        response = self.client.get(reverse('api:doc'))
        self.assertEqual(response.status_code, 200)

    def test_unlock_list(self):
        url = reverse('api:unlock-list')
        self.api_view_list(url)
        xelon = Xelon.objects.create(numero_de_dossier="A123456789", vin='VF3ABCDEF12345678')
        UnlockProduct.objects.create(unlock=xelon, user=self.user)
        response = self.client.put(f"{url}{xelon.id}/?auth_token={self.token}", data={'active': False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'id': 1, 'xelon': 'A123456789', 'vin': 'VF3ABCDEF12345678', 'active': False})

    def test_prog_list(self):
        self.api_view_list(reverse('api:prog-list'))

    def test_cal_list(self):
        self.api_view_list(reverse('api:cal-list'))

    def test_batch_list(self):
        self.api_view_list(reverse('api:reman_batch-list'))

    def test_checkout_list(self):
        self.api_view_list(reverse('api:reman_checkout-list'))

    def test_repair_list(self):
        url = reverse('api:reman_repair-list')
        data = {'identify_number': '', 'barcode': '', 'vin': ''}
        self.api_view_list(url)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, self.authError)

        # Identification with Token
        response = self.client.post(url + f'?auth_token={self.token}', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'response': 'ERROR'})

        # Create entry repair VOLVO REMAN
        sem_type = EcuType.objects.create(hw_reference='85023924.P01', hw_type='NAV', technical_data='SEM')
        sem_base = EcuRefBase.objects.create(
            reman_reference='85123456', brand='VOLVO', pf_code='PF832706GK', ecu_type=sem_type)
        EcuModel.objects.create(barcode='PF832200DF', oe_raw_reference='22996488.P02', ecu_type=sem_type)
        batch = Batch.objects.create(
            year="V", number=1, quantity=2, customer="VOLVO", created_by=self.user, ecu_ref_base=sem_base)
        data = {'identify_number': 'V001002001', 'barcode': 'PF832200DF2C000001', 'vin': 'test'}

        response = self.client.post(url + f'?auth_token={self.token}', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {
            'data': {'identify_number': 'V001002001', 'barcode': 'PF832200DF2C000001', 'vin': 'test'}, 'response': 'OK'
        })
        self.assertEqual(Repair.objects.count(), 1)

    def test_ecurefbase_list(self):
        self.api_view_list(reverse('api:reman_ecurefbase-list'))

    def test_nac_license_view(self):
        response = self.client.get(reverse('api:nac_license'), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data, self.authError)

        # Identification with Token
        response = self.client.get(f'/api/nac-license/?auth_token={self.token}', format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, {"error": "Request failed"})

    def test_thermal_chamber_measure_list(self):
        self.api_view_list(reverse('api:tools_tc_measure-list'))

    def test_bga_time_list(self):
        self.api_view_list(reverse('api:tools_bga_time-list'))
