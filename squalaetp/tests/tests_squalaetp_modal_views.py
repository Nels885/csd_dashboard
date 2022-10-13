from dashboard.tests.base import UnitTest, reverse

from squalaetp.models import Xelon, Sivin, Action
from psa.models import Corvet
from utils.django.urls import reverse


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        self.xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vinNG, modele_produit='produit',
                             modele_vehicule='peugeot')
        Xelon.objects.create(numero_de_dossier='A987654321', vin=self.vin, modele_produit='test',
                             modele_vehicule='peugeot')

    def test_vin_corvet_update_ajax_mixin(self):
        """
        Update VIN and Corvet throught BSModalCreateView.
        """
        self.add_perms_user(Xelon, 'change_vin')
        self.login()
        old_action_nb = Action.objects.count()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('squalaetp:vin_edit', kwargs={'pk': self.xelon.pk}),
            data={
                'vin': self.vin,
                # Wrong value
                'xml_data': 'ERREUR COMMUNICATION SYSTEME CORVET'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        corvets = Corvet.objects.filter(vin=self.vinNG)
        self.assertEqual(corvets.count(), 0)
        # Action is not created
        self.assertEqual(old_action_nb, Action.objects.count())

        # Second post request = Update object through BSModalUpdateView
        xelon = Xelon.objects.get(pk=self.xelon.pk)
        for xml_data, corvet_nb in [(self.xmlData, 1), ('', 1)]:
            response = self.client.post(
                reverse('squalaetp:vin_edit', kwargs={'pk': xelon.pk}),
                data={
                    'vin': self.vin,
                    'xml_data': xml_data,
                }
            )
            # redirection
            self.assertEqual(response.status_code, 302)
            # Object is updated
            xelon = Xelon.objects.get(pk=self.xelon.pk)
            self.assertEqual(xelon.vin, self.vin)
            corvets = Corvet.objects.filter(vin=self.vin)
            self.assertEqual(len(corvets), corvet_nb)
        # Action is created
        actions = Action.objects.all()
        self.assertEqual(old_action_nb + 1, actions.count())
        self.assertEqual(f"OLD_VIN: {self.vinNG}\nNEW_VIN: {self.vin}", actions.first().content)

    def test_vin_email_ajax_mixin(self):
        """
        Send email for VIN data update.
        """
        self.add_perms_user(Xelon, 'email_vin')
        self.login()

        # Update object through BSModalUpdateView
        response = self.client.post(
            reverse('squalaetp:vin_email', kwargs={'pk': self.xelon.pk}),
            data={
                'to': 'test@test.com',
                'cc': 'test@test.com',
                'subject': 'test',
                'message': 'test'
            }
        )
        # redirection
        self.assertRedirects(
            response, reverse('squalaetp:detail', args=[self.xelon.pk], get={'select': 'ihm'}), status_code=302)

    def test_product_update_ajax_mixin(self):
        """
        Update Product throught BSModalCreateView.
        """
        self.add_perms_user(Xelon, 'change_product')
        self.login()

        # Update object through BSModalUpdateView
        old_action_nb = Action.objects.count()
        response = self.client.post(
            reverse('squalaetp:prod_edit', kwargs={'pk': self.xelon.pk}),
            data={
                'modele_produit': 'test',
                'modele_vehicule': 'peugeot',
            }
        )
        # redirection
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(
        #     response, reverse('squalaetp:detail', args=[xelon.pk], get={'select': 'ihm'}), status_code=302)
        # Object is updated
        xelon = Xelon.objects.get(pk=self.xelon.pk)
        self.assertEqual(xelon.modele_produit, 'test')
        # Action is created
        actions = Action.objects.all()
        self.assertEqual(old_action_nb + 1, actions.count())
        self.assertEqual("OLD_PROD: produit\nNEW_PROD: test", actions.first().content)

    def test_prod_email_ajax_mixin(self):
        """
        Send email for Product data update.
        """
        self.add_perms_user(Xelon, 'email_product')
        self.login()

        # Update object through BSModalUpdateView
        response = self.client.post(
            reverse('squalaetp:prod_email', kwargs={'pk': self.xelon.pk}),
            data={
                'to': 'test@test.com',
                'cc': 'test@test.com',
                'subject': 'test',
                'message': 'test'
            }
        )
        # redirection
        self.assertRedirects(
            response, reverse('squalaetp:detail', args=[self.xelon.pk], get={'select': 'ihm'}), status_code=302)

    def test_sivin_create_ajax_mixin(self):
        """
        Create SIVIN throught BSModalCreateView.
        """
        self.add_perms_user(Sivin, 'add_sivin')
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(reverse('squalaetp:sivin_create'),
            data={
                'immat_siv': self.immat,
                # Wrong value
                'xml_data': 'ERREUR COMMUNICATION SYSTEME SIVIN'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        sivins = Sivin.objects.filter(immat_siv=self.immat)
        self.assertEqual(sivins.count(), 0)

        # Second post request = create object through BSModalUpdateView
        response = self.client.post(reverse('squalaetp:sivin_create'),
            data={
                'immat_siv': self.immat,
                'xml_data': self.xmlDataSivin,
            }
        )

        # redirection
        sivin = Sivin.objects.get(immat_siv=self.immat)
        self.assertRedirects(response, reverse('squalaetp:sivin_detail', args=[sivin.pk]), status_code=302)
        # Object is updated
        self.assertEqual(Sivin.objects.count(), 1)

    def test_xelon_close_ajax_mixin(self):
        """
        Xelon close throught BSModalCreateView.
        """
        self.add_perms_user(Xelon, 'change_xelon')
        self.login()

        # Update object through BSModalUpdateView
        response = self.client.post(
            reverse('squalaetp:xelon_close', kwargs={'pk': self.xelon.pk}),
            data={
                'type_de_cloture': ''
            }
        )
        # redirection
        self.assertRedirects(
            response, reverse('dashboard:products', get={'filter': 'late'}), status_code=302)
        # Object is updated
        xelon = Xelon.objects.get(pk=self.xelon.pk)
        self.assertEqual(xelon.type_de_cloture, 'N/A')
