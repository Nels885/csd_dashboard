from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group

from dashboard.models import CsdSoftware


class ToolsTestCase(TestCase):

    def setUp(self):
        self.form_data = {
            'jig': 'test', 'new_version': '1', 'link_download': 'test', 'status': 'En test',
        }
        user = User.objects.create_user(username='toto', email='toto@bibi.com', password='totopassword')
        user.groups.add(Group.objects.create(name="cellule"))
        user.save()
        self.redirectUrl = reverse('index')

    def test_soft_list_page(self):
        response = self.client.get(reverse('tools:soft-list'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_disconnected(self):
        response = self.client.get(reverse('tools:soft-add'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/tools/soft/add/')

    def test_soft_add_page_is_connected(self):
        self.client.login(username='toto', password='totopassword')
        response = self.client.get(reverse('tools:soft-add'))
        self.assertEqual(response.status_code, 200)

    def test_soft_add_page_is_valid(self):
        self.client.login(username='toto', password='totopassword')
        old_soft = CsdSoftware.objects.count()
        response = self.client.post(reverse('tools:soft-add'), self.form_data)
        new_soft = CsdSoftware.objects.count()
        self.assertEqual(new_soft, old_soft + 1)
        self.assertEqual(response.status_code, 200)
