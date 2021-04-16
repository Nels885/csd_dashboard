from django.urls import reverse

from dashboard.tests.base import UnitTest

from squalaetp.models import Xelon


class XelonTestCase(UnitTest):

    def setUp(self):
        super(XelonTestCase, self).setUp()
        self.add_perms_user(Xelon, "view_xelon")
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        self.xelonId = str(xelon.id)
        self.authError = {"detail": "Informations d'authentification non fournies."}

    def test_xelon_table_page(self):
        url = reverse('squalaetp:xelon')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_squalaetp_detail_page(self):
        url = reverse('squalaetp:detail', kwargs={'pk': self.xelonId})
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        # Detail is not found
        self.login()
        response = self.client.get(reverse('squalaetp:detail', kwargs={'pk': 666}))
        self.assertEqual(response.status_code, 404)

        # Detail is valid
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_stock_table_page(self):
        url = reverse('squalaetp:stock_parts')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_generate_squalaetp_view(self):
        url = reverse('squalaetp:generate')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertRedirects(response, reverse('index'), status_code=302)

    def test_change_table_page(self):
        url = reverse('squalaetp:change_table')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_prog_activate_view(self):
        url = reverse('squalaetp:prog_activate', kwargs={'pk': self.xelonId})
        response = self.client.get(url)
        xelon = Xelon.objects.get(pk=self.xelonId)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.assertEqual(xelon.is_active, False)
        self.login()
        response = self.client.get(url)
        xelon = Xelon.objects.get(pk=self.xelonId)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(xelon.is_active, True)

    def test_xelon_view_set_is_disconnected(self):
        response = self.client.get(reverse('squalaetp:api_xelon-list'), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, self.authError)

    # def test_xelon_view_set_is_connected(self):
    #     self.login('admin')
    #     response = self.client.get(reverse('squalaetp:api_xelon-list'), format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data), 4)
