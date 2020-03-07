from django.urls import reverse

from dashboard.tests.base import UnitTest

from tools.models import CsdSoftware, ThermalChamber


class ToolsTestCase(UnitTest):

    def setUp(self):
        super(ToolsTestCase, self).setUp()
        self.form_data = {
            'jig': 'test', 'new_version': '1', 'link_download': 'test', 'status': 'En test',
        }
        self.add_perms_user(CsdSoftware, 'add_csdsoftware', 'change_csdsoftware')

    def test_soft_list_page(self):
        response = self.client.get(reverse('tools:soft_list'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_disconnected(self):
        response = self.client.get(reverse('tools:soft_add'))
        self.assertRedirects(response, '/accounts/login/?next=/tools/soft/add/', status_code=302)

    def test_soft_add_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('tools:soft_add'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_valid(self):
        self.login()
        old_soft = CsdSoftware.objects.count()
        response = self.client.post(reverse('tools:soft_add'), self.form_data)
        new_soft = CsdSoftware.objects.count()
        self.assertEqual(new_soft, old_soft + 1)
        self.assertEqual(response.status_code, 200)

    def test_tag_xelon_is_disconnected(self):
        response = self.client.get(reverse('tools:tag_xelon'))
        self.assertRedirects(response, '/accounts/login/?next=/tools/tag-xelon/', status_code=302)

    def test_thermal_chamber_page_is_disconnected(self):
        response = self.client.get(reverse('tools:thermal'))
        self.assertRedirects(response, '/accounts/login/?next=/tools/thermal/', status_code=302)

    def test_thermal_chamber_page_is_connected(self):
        self.login()
        response = self.client.get(reverse('tools:thermal'))
        self.assertEqual(response.status_code, 200)

    def test_thermal_chamber_page_is_valid(self):
        self.login()
        old_thermal = ThermalChamber.objects.count()
        response = self.client.post(reverse('tools:thermal'), {'operating_mode': 'CHAUD'})
        new_thermal = ThermalChamber.objects.count()
        self.assertEqual(new_thermal, old_thermal + 1)
        self.assertEqual(response.status_code, 200)

    def test_thermal_disable_view(self):
        self.login()
        self.client.post(reverse('tools:thermal'), {'operating_mode': 'CHAUD'})
        thermal = ThermalChamber.objects.first()
        response = self.client.post(reverse('tools:thermal_disable', kwargs={'pk': thermal.pk}))
        new_thermal = ThermalChamber.objects.get(pk=thermal.pk)
        self.assertEqual(new_thermal.active, False)
        self.assertEqual(response.status_code, 302)
