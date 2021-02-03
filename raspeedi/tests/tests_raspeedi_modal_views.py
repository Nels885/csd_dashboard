from django.contrib.messages import get_messages

from dashboard.tests.base import UnitTest, reverse

from dashboard.models import UserProfile
from squalaetp.models import Xelon
from raspeedi.models import UnlockProduct


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        self.add_perms_user(UnlockProduct, 'delete_unlockproduct')
        xelon = Xelon.objects.create(numero_de_dossier='A123456789')
        userprofile = UserProfile.objects.get(user=self.user)
        UnlockProduct.objects.create(unlock=xelon, user=userprofile)

    def test_Delete_unlockproduct_ajax_mixin(self):
        """
        Delete object through BSModalDeleteView.
        """
        self.login()
        # Request to delete view passes message to the response
        post = UnlockProduct.objects.first()
        response = self.client.post(reverse('raspeedi:unlock_delete', kwargs={'pk': post.pk}))
        messages = get_messages(response.wsgi_request)
        self.assertEqual(len(messages), 1)
