from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages
from django.utils.translation import ugettext as _

from dashboard.tests.base import UnitTest

from tools.models import CsdSoftware, ThermalChamber, Suptech, BgaTime


class ToolsTestCase(UnitTest):

    def setUp(self):
        super(ToolsTestCase, self).setUp()
        Suptech.objects.create(
            date=timezone.now(), user='test', xelon='A123456789', item='Hot Line Tech', time='5', info='test',
            rmq='test', created_by=self.user
        )

    def test_soft_list_page(self):
        url = reverse('tools:soft_list')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page(self):
        url = reverse('tools:soft_add')
        form_data = {'jig': 'test', 'new_version': '1', 'link_download': 'test', 'status': 'En test'}
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.add_perms_user(CsdSoftware, 'add_csdsoftware', 'change_csdsoftware')
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Adding Software is valid
        old_soft = CsdSoftware.objects.count()
        response = self.client.post(reverse('tools:soft_add'), form_data)
        new_soft = CsdSoftware.objects.count()
        self.assertEqual(new_soft, old_soft + 1)
        self.assertEqual(response.status_code, 302)

    def test_tag_xelon_is_disconnected(self):
        url = reverse('tools:tag_xelon_add')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

    def test_tag_xelon_list_page(self):
        url = reverse('tools:tag_xelon_list')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_thermal_chamber_page(self):
        response = self.client.get(reverse('tools:thermal'))
        self.assertEqual(response.status_code, 200)
        old_thermal = ThermalChamber.objects.count()

        # Warning adding user for thermal chamber if not authenticated
        old_thermal = ThermalChamber.objects.count()
        response = self.client.post(reverse('tools:thermal'), {'operating_mode': 'CHAUD'})
        new_thermal = ThermalChamber.objects.count()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), _('You do not have the required permissions'))
        self.assertEqual(new_thermal, old_thermal)
        self.assertEqual(response.status_code, 200)

        self.login()
        # Adding user for thermal chamber
        response = self.client.post(reverse('tools:thermal'), {'operating_mode': 'CHAUD'})
        new_thermal = ThermalChamber.objects.count()
        self.assertEqual(new_thermal, old_thermal + 1)
        self.assertEqual(response.status_code, 200)

    def test_thermal_disable_view(self):
        self.login()
        self.client.post(reverse('tools:thermal'), {'operating_mode': 'CHAUD', 'xelon_number': 'A123456789'})
        thermal = ThermalChamber.objects.get(xelon_number='A123456789')
        response = self.client.post(reverse('tools:thermal_disable', kwargs={'pk': thermal.pk}))
        new_thermal = ThermalChamber.objects.get(pk=thermal.pk)
        self.assertEqual(new_thermal.active, False)
        self.assertEqual(new_thermal.stop_time, None)
        self.assertEqual(response.status_code, 302)

        self.client.post(reverse('tools:thermal'), {'operating_mode': 'FROID', 'xelon_number': 'A987654321'})
        ThermalChamber.objects.filter(xelon_number='A987654321').update(start_time=timezone.now())
        thermal = ThermalChamber.objects.filter(xelon_number="A987654321").first()
        response = self.client.post(reverse('tools:thermal_disable', kwargs={'pk': thermal.pk}))
        new_thermal = ThermalChamber.objects.get(pk=thermal.pk)
        self.assertEqual(new_thermal.active, False)
        self.assertNotEqual(new_thermal.stop_time, None)
        self.assertEqual(response.status_code, 302)

    def test_thermal_chamber_full_page(self):
        response = self.client.get(reverse('tools:thermal_full'))
        self.assertEqual(response.status_code, 200)

    def test_thermal_chamber_list_page(self):
        url = reverse('tools:thermal_list')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ajax_temp(self):
        response = self.client.get(reverse('tools:ajax_temp'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"temp": "Hors ligne"})

    def test_create_suptech_is_disconnected(self):
        url = reverse('tools:suptech_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_suptech_list_page(self):
        url = reverse('tools:suptech_list')
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)
        self.login()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_response_suptech_page(self):
        suptech = Suptech.objects.first()
        url = reverse('tools:suptech_update', kwargs={'pk': suptech.pk})
        form_data = {
            'xelon': 'A123456789', 'item': 'Hot Line Tech', 'time': '5', 'info': 'test', 'rmq': 'test',
            'action': 'test', 'status': 'Cloturée', 'deadline': ''
        }
        response = self.client.get(url)
        self.assertRedirects(response, self.nextLoginUrl + url, status_code=302)

        self.add_perms_user(Suptech, 'change_suptech')
        self.login()

        response = self.client.post(url, form_data)
        self.assertRedirects(response, reverse('tools:suptech_list'), status_code=302)

        # If the creation user does not exist
        suptech.created_by = None
        suptech.save()
        response = self.client.post(url, form_data)
        self.assertRedirects(response, reverse('tools:suptech_list'), status_code=302)

    def test_bga_time_view(self):
        url = reverse('tools:bga_time')
        response = self.client.get(url)
        self.assertJSONEqual(response.content, {"response": "ERROR"})

        response = self.client.get(url, {"device": "test", "status": "start"})
        self.assertJSONEqual(response.content, {"response": "OK", "device": "test", "status": "START"})
        self.assertEqual(BgaTime.objects.count(), 1)
        self.assertEqual(BgaTime.objects.first().end_time, None)

        response = self.client.get(url, {"device": "test", "status": "start"})
        self.assertJSONEqual(response.content, {"response": "OK", "device": "test", "status": "START"})
        self.assertEqual(BgaTime.objects.count(), 2)
        self.assertEqual(BgaTime.objects.first().duration, 300)
        self.assertEqual(BgaTime.objects.last().end_time, None)

        response = self.client.get(url, {"device": "test", "status": "stop"})
        self.assertJSONEqual(response.content, {"response": "OK", "device": "test", "status": "STOP"})
        self.assertEqual(BgaTime.objects.count(), 2)
        self.assertNotEqual(BgaTime.objects.last().end_time, None)
