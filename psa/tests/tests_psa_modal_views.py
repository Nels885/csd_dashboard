from dashboard.tests.base import UnitTest, reverse

from psa.models import Corvet


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()

    def test_create_corvet_ajax_mixin(self):
        """
        Create Corvet through BSModalCreateView.
        """
        self.add_perms_user(Corvet, 'add_corvet')
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('psa:create_corvet'),
            data={
                'vin': self.vin,
                # Wrong value
                'xml_data': ''
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        corvets = Corvet.objects.all()
        self.assertEqual(corvets.count(), 0)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('psa:create_corvet'),
            data={
                'vin': self.vin,
                'xml_data': self.xmlData
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        corvets = Corvet.objects.all()
        self.assertEqual(corvets.count(), 1)
