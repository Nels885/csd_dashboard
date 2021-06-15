from dashboard.tests.base import UnitTest, reverse

from squalaetp.models import Xelon
from tools.models import TagXelon, Suptech, SuptechItem


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        SuptechItem.objects.create(name='Hot Line Tech')
        self.xelonId = str(xelon.id)

    def test_create_Tag_xelon_ajax_mixin(self):
        """
        Create TagXelon through BSModalCreateView.
        """
        self.add_perms_user(TagXelon, 'add_tagxelon')
        self.login()

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('tools:tag_xelon_add'),
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
            reverse('tools:tag_xelon_add'),
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

    def test_create_suptech_ajax_mixin(self):
        """
        Create Suptech through BSModalCreateView.
        """

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('tools:suptech_add'),
            data={
                'xelon': 'A123456789',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        suptechs = Suptech.objects.all()
        item = SuptechItem.objects.first()
        self.assertEqual(suptechs.count(), 0)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('tools:suptech_add'),
            data={
                'username': self.user.username,
                'xelon': 'A123456789',
                'item': item.id,
                'time': '5',
                'info': 'test',
                'rmq': 'test',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        suptechs = Suptech.objects.all()
        self.assertNotEqual(suptechs.count(), 0)
