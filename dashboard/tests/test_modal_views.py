from django.contrib.auth.models import User, Group

from .base import UnitTest, reverse

from squalaetp.models import Xelon
from tools.models import TagXelon


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        user = User.objects.get(username='toto')
        user.groups.add(Group.objects.create(name="technician"))
        user.save()
        self.xelonId = str(xelon.id)

    def test_TagXelonAjaxMixin(self):
        """
        Test if initial request is attached to the form instance through
        PassRequestMixin and PopRequestMixin.
        """
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('tools:tag-xelon'),
            data={
                'xelon': 'wrong_xelon',
                'comments': ''
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        tags = TagXelon.objects.all()
        self.assertEqual(tags.count(), 0)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('tools:tag-xelon'),
            data={
                'xelon': 'A123456789',
                'comments': ''
            }
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        tags = TagXelon.objects.all()
        self.assertEqual(tags.count(), 1)

    def test_LoginAjaxMixin(self):
        """
        Login user through BSModalLoginView.
        """

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('dashboard:login'),
            data={
                'username': 'toto',
                # Wrong value
                'password': 'wrong_password'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # User is anonymous
        self.assertTrue(response.wsgi_request.user.is_anonymous)

        # Second post request = non-ajax request logging the user in
        response = self.client.post(
            reverse('dashboard:login'),
            data={
                'username': 'toto',
                'password': 'totopassword'
            }
        )

        # Redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/dashboard/charts/')
        # User is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
