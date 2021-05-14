from dashboard.tests.base import UnitTest, reverse

from squalaetp.models import Xelon
from psa.models import Corvet
from utils.django.urls import reverse


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')

    def test_vin_corvet_update_ajax_mixin(self):
        """
        Update VIN and Corvet throught BSModalCreateView.
        """
        self.add_perms_user(Xelon, 'change_vin')
        self.login()

        # Update object through BSModalUpdateView
        xelon = Xelon.objects.first()
        response = self.client.post(
            reverse('squalaetp:vin_edit', kwargs={'pk': xelon.pk}),
            data={
                'vin': self.vin,
                'xml_data': self.xmlData,
            }
        )
        # redirection
        self.assertRedirects(
            response, reverse('squalaetp:detail', args=[xelon.pk], get={'select': 'ihm'}), status_code=302)
        # Object is updated
        xelon = Xelon.objects.first()
        self.assertEqual(xelon.vin, self.vin)

    def test_vin_email_ajax_mixin(self):
        """
        Send email for VIN data update.
        """
        self.add_perms_user(Xelon, 'email_vin')
        self.login()

        # Update object through BSModalUpdateView
        xelon = Xelon.objects.first()
        response = self.client.post(
            reverse('squalaetp:vin_email', kwargs={'pk': xelon.pk}),
            data={
                'to': 'test@test.com',
                'cc': 'test@test.com',
                'subject': 'test',
                'message': 'test'
            }
        )
        # redirection
        self.assertRedirects(
            response, reverse('squalaetp:detail', args=[xelon.pk], get={'select': 'ihm'}), status_code=302)

    def test_product_update_ajax_mixin(self):
        """
        Update Product throught BSModalCreateView.
        """
        self.add_perms_user(Xelon, 'change_product')
        self.login()

        # Update object through BSModalUpdateView
        xelon = Xelon.objects.first()
        response = self.client.post(
            reverse('squalaetp:prod_edit', kwargs={'pk': xelon.pk}),
            data={
                'modele_produit': 'test',
                'modele_vehicule': 'peugeot',
            }
        )
        # redirection
        self.assertRedirects(
            response, reverse('squalaetp:detail', args=[xelon.pk], get={'select': 'ihm'}), status_code=302)
        # Object is updated
        xelon = Xelon.objects.first()
        self.assertEqual(xelon.modele_produit, 'test')

    def test_prod_email_ajax_mixin(self):
        """
        Send email for Product data update.
        """
        self.add_perms_user(Xelon, 'email_product')
        self.login()

        # Update object through BSModalUpdateView
        xelon = Xelon.objects.first()
        response = self.client.post(
            reverse('squalaetp:prod_email', kwargs={'pk': xelon.pk}),
            data={
                'to': 'test@test.com',
                'cc': 'test@test.com',
                'subject': 'test',
                'message': 'test'
            }
        )
        # redirection
        self.assertRedirects(
            response, reverse('squalaetp:detail', args=[xelon.pk], get={'select': 'ihm'}), status_code=302)
