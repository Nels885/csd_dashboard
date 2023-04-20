from django.contrib.messages import get_messages

from dashboard.tests.base import UnitTest, reverse

from dashboard.models import UserProfile
from squalaetp.models import Xelon
from prog.models import UnlockProduct, ToolStatus


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        self.add_perms_user(UnlockProduct, 'delete_unlockproduct')
        xelon = Xelon.objects.create(numero_de_dossier='A123456789')
        UnlockProduct.objects.create(unlock=xelon, user=self.user)

    def test_Delete_unlockproduct_ajax_mixin(self):
        """
        Delete object through BSModalDeleteView.
        """
        self.login()
        # Request to delete view passes message to the response
        post = UnlockProduct.objects.first()
        response = self.client.post(reverse('prog:unlock_delete', kwargs={'pk': post.pk}))
        messages = get_messages(response.wsgi_request)
        self.assertEqual(len(messages), 1)

    def test_add_tool_ajax_mixin(self):
        """
        Add tool through BSModalCreateView.
        """
        self.add_perms_user(ToolStatus, 'add_toolstatus')
        self.login()

        # First post request = ajax request checking if form in view is not valid
        response = self.client.post(
            reverse('prog:tool_add'),
            data={
                'name': '',
                'comment': '',
                'url': '',
                'status_path': '',
                'api_path': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        tools = ToolStatus.objects.all()
        self.assertEqual(tools.count(), 0)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('prog:tool_add'),
            data={
                'name': 'test',
                'comment': '',
                'url': 'http//test.com/',
                'status_path': '',
                'api_path': '',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        tools = ToolStatus.objects.all()
        self.assertEqual(tools.count(), 1)

    def test_update_tool_ajax_mixin(self):
        """
        Update batch throught BSModalUpdateView.
        """
        self.add_perms_user(ToolStatus, 'change_toolstatus')
        self.login()

        # Update object through BSModalUpdateView
        old_tool = ToolStatus.objects.create(name='test', url='http://test.com/')
        response = self.client.post(
            reverse('prog:tool_update', kwargs={'pk': old_tool.pk}),
            data={
                'name': 'new_test',
                'comment': '',
                'url': 'http//test.com/',
                'status_path': '',
                'api_path': '',
            },
        )
        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is updated
        new_tool = ToolStatus.objects.get(pk=old_tool.pk)
        self.assertNotEqual(new_tool.name, old_tool.name)
