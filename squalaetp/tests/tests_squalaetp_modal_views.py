from dashboard.tests.base import UnitTest, reverse

from squalaetp.models import Xelon
from psa.models import Corvet


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                             modele_vehicule='peugeot')

    def test_update_squalaetp_ajax_mixin(self):
        """
        Update Post throught BSModalCreateView.
        """
        self.add_perms_user(Xelon, 'change_xelon')
        self.add_perms_user(Corvet, 'change_corvet')
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
        # self.assertRedirects(response, reverse('squalaetp:detail', kwargs={'pk': xelon.pk}), status_code=302)
        # Object is updated
        xelon = Xelon.objects.first()
        self.assertEqual(xelon.vin, self.vin)
