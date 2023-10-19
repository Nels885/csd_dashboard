from dashboard.tests.base import UnitTest, reverse

from squalaetp.models import Xelon
from tools.models import TagXelon, Suptech, SuptechItem, InfotechMailingList, Infotech


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        xelon = Xelon.objects.create(numero_de_dossier='A123456789', vin=self.vin, modele_produit='produit',
                                     modele_vehicule='peugeot')
        SuptechItem.objects.create(name='Hot Line Tech')
        InfotechMailingList.objects.create(name='Mailing test')
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
                'calibre': True,
                'telecode': False,
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
                'calibre': True,
                'telecode': False,
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
                'to': 'test@test.com',
                'info': 'test',
                'rmq': 'test',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        suptechs = Suptech.objects.all()
        self.assertNotEqual(suptechs.count(), 0)

    def test_create_infotech_ajax_mixin(self):
        """
        Create Infotech through BSModalCreateView.
        """

        # First post request = ajax request checking if form in view is valid
        response = self.client.post(
            reverse('tools:infotech_add'),
            data={
                'item': 'test',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        queryset = Infotech.objects.all()
        mailing = InfotechMailingList.objects.first()
        self.assertEqual(queryset.count(), 0)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('tools:infotech_add'),
            data={
                'username': self.user.username,
                'item': 'test',
                'mailing': mailing.id,
                'info': 'test',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        queryset = Infotech.objects.all()
        self.assertNotEqual(queryset.count(), 0)
