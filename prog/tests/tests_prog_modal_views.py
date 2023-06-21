from django.contrib.messages import get_messages

from dashboard.tests.base import UnitTest, reverse

from dashboard.models import UserProfile
from squalaetp.models import Xelon
from prog.models import UnlockProduct, ToolStatus, AET, MbedFirmware


class MixinsTest(UnitTest):

    def setUp(self):
        super(MixinsTest, self).setUp()
        self.add_perms_user(UnlockProduct, 'delete_unlockproduct')
        self.add_perms_user(AET, 'add_aet')
        AET.objects.create(name='test', raspi_url='10.0.0.0')
        MbedFirmware.objects.create(name='test', version='0.0', filepath='test.bin')
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
        Update batch through BSModalUpdateView.
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

    def test_delete_tool_ajax_mixin(self):
        """
        Delete ToolsStatus through BSModalDeleteView.
        """
        self.add_perms_user(ToolStatus, 'delete_toolstatus')
        self.login()
        # Request to delete view passes message to the response
        query = ToolStatus.objects.create(name='test', url='http://test.com/')
        response = self.client.post(reverse('prog:tool_delete', kwargs={'pk': query.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_add_aet_ajax_mixin(self):
        """
        Add AET through BSModalCreateView.
        """
        self.add_perms_user(AET, 'add_aet')
        self.login()

        # First post request = ajax request checking if form in view is not valid
        response = self.client.post(
            reverse('prog:aet_add'),
            data={
                'name': '',
                'raspi_url': '',
                'mbed_list': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        aet = AET.objects.all()
        self.assertEqual(aet.count(), 1)

        # Second post request = non-ajax request creating an object
        response = self.client.post(
            reverse('prog:aet_add'),
            data={
                'name': 'AET test',
                'raspi_url': '10.0.0.0',
                'mbed_list': '',
            },
        )

        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is not created
        aet = AET.objects.all()
        self.assertEqual(aet.count(), 2)

    def test_update_aet_ajax_mixin(self):
        """
        Update AET through BSModalUpdateView.
        """
        self.add_perms_user(AET, 'change_aet')
        self.login()

        # Update AET through BSModalUpdateView
        old_aet = AET.objects.create(name='AET test')
        response = self.client.post(
            reverse('prog:aet_update', kwargs={'pk': old_aet.pk}),
            data={
                'name': 'AET test 2',
                'raspi_url': '10.0.0.0',
                'mbed_list': '',
            },
        )
        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is updated
        new_aet = AET.objects.get(pk=old_aet.pk)
        self.assertNotEqual(new_aet.name, old_aet.name)

    def test_delete_aet_ajax_mixin(self):
        """
        Delete AET through BSModalDeleteView.
        """
        self.add_perms_user(AET, 'delete_aet')
        self.login()
        # Request to delete view passes message to the response
        post = AET.objects.first()
        response = self.client.post(reverse('prog:aet_delete', kwargs={'pk': post.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_add_firmware_ajax_mixin(self):
        """
        Add MbedFirmware through BSModalCreateView.
        """
        self.add_perms_user(AET, 'add_aet')
        self.login()

        # First post request = ajax request checking if form in view is not valid
        response = self.client.post(
            reverse('prog:aet_add_software'),
            data={
                'name': '',
                'version': '',
                'filepath': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        # Form has errors
        self.assertTrue(response.context_data['form'].errors)
        # No redirection
        self.assertEqual(response.status_code, 200)
        # Object is not created
        firmware = MbedFirmware.objects.all()
        self.assertEqual(firmware.count(), 1)

    def test_update_firmware_ajax_mixin(self):
        """
        Update MbedFirmware through BSModalUpdateView.
        """
        self.add_perms_user(AET, 'change_aet')
        self.login()

        # Update AET through BSModalUpdateView
        old_firmware = MbedFirmware.objects.create(name='firmware test', version='0.09', filepath='test.bin')
        response = self.client.post(
            reverse('prog:firmware_update', kwargs={'pk': old_firmware.pk}),
            data={
                'name': 'firmware test 2',
                'version': '1.00',
                'filepath': 'test.bin',
            },
        )
        # redirection
        self.assertEqual(response.status_code, 302)
        # Object is updated
        new_firmware = MbedFirmware.objects.get(pk=old_firmware.pk)
        self.assertNotEqual(new_firmware.name, old_firmware.name)

    def test_delete_firmware_ajax_mixin(self):
        """
        Delete MbedFirmware through BSModalDeleteView.
        """
        self.add_perms_user(AET, 'change_aet')
        self.login()
        # Request to delete view passes message to the response
        post = MbedFirmware.objects.first()
        response = self.client.post(reverse('prog:firmware_delete', kwargs={'pk': post.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

